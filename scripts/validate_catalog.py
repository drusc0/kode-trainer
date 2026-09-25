"""Validate the whole catalog + sandbox inside the runner container (see `make test-sandbox`).

1. Every reference solution runs cleanly on its examples + generated hidden tests.
2. Every reference passes its own checker (catches checker / generator bugs).
3. A set of hostile submissions is contained (timeouts, memory, fork bombs, files, network, exec).
"""
import os
import random
import sys

for p in ("/app", os.path.join(os.path.dirname(__file__), "..", "runner")):
    sys.path.insert(0, p)
for p in ("/backend", os.path.join(os.path.dirname(__file__), "..", "backend")):
    sys.path.insert(0, p)

from sandbox import run_job  # noqa: E402
from app.catalog import PROBLEMS  # noqa: E402


def job(p, code, tests, expected=None, tl=None):
    return {"code": code, "kind": p.kind, "entry": p.entry, "param_types": p.param_types(), "return_type": p.returns,
            "tests": tests, "expected": expected, "compare": p.compare, "time_limit_ms": tl or 10_000}


failures = 0
for p in PROBLEMS:
    tests = [e["args"] for e in p.examples] + p.gen(random.Random(p.slug))
    r1 = run_job(job(p, p.reference, tests), 0)
    bad = [x for x in r1["results"] if "error" in x or x.get("truncated")]
    if r1["status"] != "ok" or len(r1["results"]) != len(tests) or bad:
        failures += 1
        print(f"FAIL {p.slug}: reference {r1['status']} {r1['error'] or (bad[0].get('error') if bad else 'missing results')}")
        continue
    r2 = run_job(job(p, p.reference, tests, [x["output"] for x in r1["results"]]), 1)
    ok = sum(1 for x in r2["results"] if x.get("ok"))
    slowest = max(x["ms"] for x in r1["results"])
    status = "ok  " if ok == len(tests) else "FAIL"
    failures += ok != len(tests)
    print(f"{status} {p.slug:48s} {ok:3d}/{len(tests)} tests, slowest reference test {slowest:.0f} ms")

ATTACKS = {
    "network": "import socket\nclass Solution:\n    def twoSum(self, n, t):\n        socket.create_connection(('1.1.1.1', 80), timeout=2)",
    "exec": "import os\nclass Solution:\n    def twoSum(self, n, t):\n        os.system('id')\n        import subprocess; return [subprocess.check_output(['id']).decode()]",
    "infinite": "class Solution:\n    def twoSum(self, n, t):\n        while True: pass",
    "memory": "class Solution:\n    def twoSum(self, n, t):\n        x = bytearray(10**10)",
    "fork_bomb": "import os\nclass Solution:\n    def twoSum(self, n, t):\n        while True: os.fork()",
    "write_fs": "class Solution:\n    def twoSum(self, n, t):\n        open('/app/harness.py', 'a').write('#')",
    "read_env": "import os\nclass Solution:\n    def twoSum(self, n, t):\n        return [dict(os.environ)]",
}
two_sum = next(p for p in PROBLEMS if p.slug == "two-sum")
print("\nhostile submissions (all should fail safely):")
for name, code in ATTACKS.items():
    r = run_job(job(two_sum, code, [[[2, 7], 9]], [[0, 1]], tl=1000), 2)
    res = r["results"][0] if r["results"] else {}
    contained = r["status"] != "ok" or bool(res.get("error"))
    leaked = "RUNNER_TOKEN" in str(res.get("output")) if name == "read_env" else not contained
    failures += bool(leaked)
    print(f"  {'LEAK' if leaked else 'ok  '} {name:10s} -> {r['status']}: {(r['error'] or res.get('error') or str(res.get('output')))[:100]!r}")

print("\nALL GOOD" if not failures else f"\n{failures} FAILURE(S)")
sys.exit(1 if failures else 0)
