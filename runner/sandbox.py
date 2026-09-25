"""Spawns the harness in a locked-down child process and collects its results."""

import contextlib
import json
import os
import resource
import selectors
import signal
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

DONE_MARKER = b'{"type": "done"}'
HARNESS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "harness.py")


@dataclass
class Limits:
    base_uid: int = int(os.environ.get("RUNNER_BASE_UID", "61000"))
    python: str = os.environ.get("RUNNER_PYTHON", sys.executable)
    workdir: str = os.environ.get("RUNNER_WORKDIR", "/sandbox")
    memory_mb: int = int(os.environ.get("RUNNER_MEMORY_MB", "512"))
    max_wall_s: float = float(os.environ.get("RUNNER_MAX_WALL_S", "20"))
    max_output_bytes: int = 32 * 1024 * 1024
    max_procs: int = int(os.environ.get("RUNNER_MAX_PROCS", "16"))
    drop_privileges: bool = os.environ.get("RUNNER_DROP_PRIVILEGES", "1") == "1"
    seccomp_required: bool = os.environ.get("RUNNER_REQUIRE_SECCOMP", "1") == "1"


LIMITS = Limits()


def _preexec(uid: int, cpu_s: int, lim: Limits) -> Callable[[], None]:
    def fn() -> None:
        os.setsid()  # own process group so we can kill everything it spawns
        mem = lim.memory_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_s, cpu_s + 1))
        resource.setrlimit(resource.RLIMIT_FSIZE, (1 << 20, 1 << 20))
        resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        resource.setrlimit(resource.RLIMIT_STACK, (64 << 20, 64 << 20))
        if lim.drop_privileges:
            resource.setrlimit(resource.RLIMIT_NPROC, (lim.max_procs, lim.max_procs))
            os.setgroups([])
            os.setgid(uid)
            os.setuid(uid)

    return fn


def _kill_uid(uid: int) -> None:
    """SIGKILL every process owned by a sandbox uid (catches anything that escaped the process group)."""
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            if os.stat(f"/proc/{pid}").st_uid == uid:
                os.kill(int(pid), signal.SIGKILL)
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            pass


def run_job(job: dict[str, Any], slot: int, lim: Limits = LIMITS) -> dict[str, Any]:
    uid = lim.base_uid + slot
    n = max(1, len(job.get("tests", [])))
    per_test = max(0.05, job.get("time_limit_ms", 2000) / 1000)
    wall = min(lim.max_wall_s, 1.5 + per_test * (n + 1))
    cpu = int(wall) + 1
    job = dict(job, _sandbox={"seccomp_required": lim.seccomp_required})
    payload = json.dumps(job).encode()

    env = {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", "HOME": "/nonexistent", "PYTHONHASHSEED": "0"}
    started = time.monotonic()
    proc = subprocess.Popen(
        [lim.python, "-I", "-B", HARNESS],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=lim.workdir,
        env=env,
        close_fds=True,
        preexec_fn=_preexec(uid, cpu, lim),
    )
    assert proc.stdin is not None and proc.stdout is not None and proc.stderr is not None  # all are PIPEs
    try:
        proc.stdin.write(payload)
        proc.stdin.close()
    except BrokenPipeError:
        pass

    chunks: list[bytes] = []
    total = 0
    killed_reason: str | None = None
    sel = selectors.DefaultSelector()
    sel.register(proc.stdout, selectors.EVENT_READ)
    sel.register(proc.stderr, selectors.EVENT_READ)
    open_streams = 2
    while open_streams:
        remaining = wall - (time.monotonic() - started)
        if remaining <= 0:
            killed_reason = "timeout"
            break
        for key, _ in sel.select(timeout=remaining):
            data = os.read(key.fd, 65536)
            if not data:
                sel.unregister(key.fileobj)
                open_streams -= 1
                continue
            if key.fileobj is proc.stdout:
                chunks.append(data)
                total += len(data)
                if total > lim.max_output_bytes:
                    killed_reason = "output"
                    break
                if DONE_MARKER in data or (len(chunks) > 1 and DONE_MARKER in chunks[-2][-32:] + data):
                    open_streams = 0  # harness finished; don't wait for stray children holding the pipe
                    break
        if killed_reason:
            break
    sel.close()

    if killed_reason or proc.poll() is None:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(proc.pid, signal.SIGKILL)
    with contextlib.suppress(subprocess.TimeoutExpired):
        proc.wait(timeout=2)
    if lim.drop_privileges:
        _kill_uid(uid)

    results: list[dict[str, Any]] = []
    status, got_done = "ok", False
    error: str | None = None
    for line in b"".join(chunks).decode("utf-8", "replace").splitlines():
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = msg.get("type")
        if t == "result":
            msg.pop("type", None)
            results.append(msg)
        elif t == "compile_error":
            status, error = "compile_error", msg.get("error")
        elif t == "done":
            got_done = True
    if status == "ok" and not got_done:
        if killed_reason == "timeout":
            status, error = "timeout", "Time limit exceeded"
        elif killed_reason == "output":
            status, error = "crashed", "Too much output"
        else:
            rc = proc.returncode
            if rc is not None and rc < 0:
                sig = signal.Signals(-rc).name
                hint = " (often very deep recursion or running out of memory)" if sig in ("SIGSEGV", "SIGKILL") else ""
                if sig == "SIGXCPU":
                    status, error = "timeout", "CPU time limit exceeded"
                else:
                    status, error = "crashed", f"Process was killed by {sig}{hint}"
            else:
                status, error = "crashed", f"Process exited unexpectedly (code {rc})"
    return {
        "status": status,
        "error": error,
        "results": results,
        "elapsed_ms": round((time.monotonic() - started) * 1000),
    }


if __name__ == "__main__":  # manual test: python sandbox.py < job.json
    print(json.dumps(run_job(json.load(sys.stdin), 0), indent=2))
