"""Tiny stdlib HTTP front for the sandbox. Only the API talks to it (internal network + shared token)."""

import hmac
import json
import os
import queue
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from sandbox import LIMITS, run_job

TOKEN = os.environ.get("RUNNER_TOKEN", "")
SLOTS = int(os.environ.get("RUNNER_SLOTS", "4"))
MAX_BODY = 16 * 1024 * 1024

free_slots: "queue.Queue[int]" = queue.Queue()
for s in range(SLOTS):
    free_slots.put(s)


class Handler(BaseHTTPRequestHandler):
    server_version = "kodetrain-runner"

    def _send(self, code: int, obj: Any) -> None:
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send(200, {"ok": True, "slots": SLOTS, "free": free_slots.qsize()})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self) -> None:
        if self.path != "/run":
            self._send(404, {"error": "not found"})
            return
        if not TOKEN or not hmac.compare_digest(self.headers.get("X-Runner-Token", ""), TOKEN):
            self._send(401, {"error": "unauthorized"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY:
            self._send(413, {"error": "payload too large"})
            return
        try:
            job = json.loads(self.rfile.read(length))
        except ValueError:
            job = None
        if not (
            isinstance(job, dict)
            and isinstance(job.get("code"), str)
            and isinstance(job.get("tests"), list)
            and isinstance(job.get("entry"), str)
            and isinstance(job.get("time_limit_ms", 0), int)
        ):
            self._send(400, {"error": "bad job"})
            return
        try:
            slot = free_slots.get(timeout=30)
        except queue.Empty:
            self._send(503, {"error": "all sandboxes busy, try again"})
            return
        try:
            self._send(200, run_job(job, slot))
        finally:
            free_slots.put(slot)

    def log_message(self, format: str, *args: Any) -> None:  # keep logs short
        print("runner:", format % args, flush=True)


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("RUNNER_TOKEN must be set")
    print(
        f"runner listening on :8080 with {SLOTS} slots (drop_privileges={LIMITS.drop_privileges}, seccomp_required={LIMITS.seccomp_required})",
        flush=True,
    )
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
