"""Turns problems + user code into sandbox jobs, computes verdicts, and seeds expected outputs."""
import asyncio
import json
import logging
import random

from .catalog import PROBLEMS, BY_SLUG, Problem, problem_fingerprint
from .core import RunnerError, db, now, run_in_sandbox

log = logging.getLogger("kodetrain.judge")
PREVIEW_CHARS = 4000
seed_state = {"status": "pending", "done": 0, "total": len(PROBLEMS), "errors": []}


# ---------------------------------------------------------------- helpers
def preview(value) -> str:
    text = value if isinstance(value, str) and value.endswith("…") else json.dumps(value)
    return text if len(text) <= PREVIEW_CHARS else text[:PREVIEW_CHARS] + f"… ({len(text) - PREVIEW_CHARS:,} more characters)"


def editor_fields(p: Problem) -> list[dict]:
    return [{"name": n, "type": p.display_type(t)} for n, t in p.params]


def to_editor(p: Problem, args: list) -> list:
    """Stored test args -> one value per editor field."""
    if p.kind == "design":
        return [args[0]["ops"], args[0]["args"]]
    return args


def from_editor(p: Problem, values: list) -> list:
    if p.kind == "design":
        ops, op_args = values
        if not (isinstance(ops, list) and isinstance(op_args, list) and len(ops) == len(op_args) and ops and ops[0] == p.entry):
            raise ValueError(f"operations must start with \"{p.entry}\" and have one argument list per operation")
        return [{"ops": ops, "args": op_args}]
    if len(values) != len(p.params):
        raise ValueError(f"expected {len(p.params)} values, got {len(values)}")
    return values


def make_job(p: Problem, code: str, tests: list, expected: list | None, time_limit_ms: int | None = None) -> dict:
    return {
        "code": code, "kind": p.kind, "entry": p.entry, "param_types": p.param_types(), "return_type": p.returns,
        "tests": tests, "expected": expected, "compare": p.compare,
        "time_limit_ms": time_limit_ms or p.time_limit_ms,
    }


def verdict_of(res: dict, total: int) -> tuple[str, int | None]:
    """(verdict, index of first failing test)."""
    if res["status"] == "compile_error":
        return "Compile Error", None
    results = res["results"]
    for i in range(total):
        if i >= len(results):
            return ("Time Limit Exceeded" if res["status"] == "timeout" else "Runtime Error"), i
        r = results[i]
        if not r.get("ok"):
            return {"timeout": "Time Limit Exceeded", "memory": "Memory Limit Exceeded", "runtime": "Runtime Error"}.get(
                r.get("error_type"), "Wrong Answer"), i
    return "Accepted", None


# ---------------------------------------------------------------- seeding
async def _seed_one(p: Problem) -> None:
    fp = problem_fingerprint(p)
    existing = await db().problem_tests.find_one({"_id": p.slug}, {"fingerprint": 1})
    if existing and existing.get("fingerprint") == fp:
        return
    args = [e["args"] for e in p.examples] + p.gen(random.Random(p.slug))
    res = await run_in_sandbox(make_job(p, p.reference, args, None, time_limit_ms=10_000))
    bad = [r for r in res["results"] if "error" in r or r.get("truncated")]
    if res["status"] != "ok" or len(res["results"]) != len(args) or bad:
        raise RuntimeError(f"{p.slug}: reference failed ({res['status']}: {res.get('error') or (bad[0].get('error') if bad else 'missing results')})")
    tests = [{"args": a, "expected": r["output"]} for a, r in zip(args, res["results"])]
    await db().problem_tests.replace_one(
        {"_id": p.slug},
        {"_id": p.slug, "fingerprint": fp, "examples": len(p.examples), "tests": tests, "seeded_at": now()},
        upsert=True,
    )


async def seed_all() -> None:
    """Compute expected outputs for every problem whose definition changed. Retries while the runner starts up."""
    seed_state.update(status="running", done=0, errors=[])
    sem = asyncio.Semaphore(3)

    async def one(p):
        async with sem:
            for attempt in range(30):
                try:
                    await _seed_one(p)
                    break
                except RunnerError as e:
                    if attempt == 29:
                        seed_state["errors"].append(f"{p.slug}: {e}")
                    await asyncio.sleep(2)
                except Exception as e:  # noqa: BLE001
                    log.exception("seeding %s failed", p.slug)
                    seed_state["errors"].append(str(e))
                    break
            seed_state["done"] += 1

    await asyncio.gather(*(one(p) for p in PROBLEMS))
    seed_state["status"] = "ready" if not seed_state["errors"] else "error"
    log.info("seeding finished: %s", seed_state)


async def load_tests(slug: str) -> dict:
    doc = await db().problem_tests.find_one({"_id": slug})
    if not doc:
        raise LookupError("This problem's tests are still being prepared. Try again in a few seconds.")
    return doc


# ---------------------------------------------------------------- run & submit
def _case_view(p: Problem, args, r: dict | None, expected=None, show_expected=True) -> dict:
    view = {"args": [preview(v) for v in to_editor(p, args)]}
    if r is not None:
        view.update(ok=bool(r.get("ok")), stdout=r.get("stdout", ""), error=r.get("error"), ms=r.get("ms"))
        if "output" in r:
            view["output"] = preview(r["output"])
    if show_expected:
        view["expected"] = preview(expected)
    return view


async def run_cases(p: Problem, code: str, cases: list[list]) -> dict:
    args = [from_editor(p, c) for c in cases]
    ref = await run_in_sandbox(make_job(p, p.reference, args, None, time_limit_ms=5000))
    expected, ref_errors = [], {}
    for i in range(len(args)):
        r = ref["results"][i] if i < len(ref["results"]) else {"error": "reference did not finish"}
        expected.append(r.get("output"))
        if "error" in r:
            ref_errors[i] = r["error"]
    res = await run_in_sandbox(make_job(p, code, args, expected))
    verdict, _ = verdict_of(res, len(args))
    out = {"verdict": verdict, "compile_error": res["error"] if res["status"] == "compile_error" else None, "cases": []}
    for i, a in enumerate(args):
        r = res["results"][i] if i < len(res["results"]) else None
        if r is None and res["status"] in ("timeout", "crashed") and i == len(res["results"]):
            r = {"ok": False, "error": res["error"]}
        case = _case_view(p, a, r, expected[i])
        if i in ref_errors:
            case["expected"] = None
            case["input_error"] = "This input breaks the problem's constraints, so there is no expected output."
            case["ok"] = False
        out["cases"].append(case)
    if ref_errors and verdict == "Wrong Answer" and all(i in ref_errors for i, c in enumerate(out["cases"]) if not c.get("ok")):
        out["verdict"] = "Invalid Input"
    out["passed"] = sum(1 for c in out["cases"] if c.get("ok"))
    out["runtime_ms"] = round(sum(r.get("ms") or 0 for r in res["results"]), 1) if verdict == "Accepted" else None
    return out


async def submit(p: Problem, code: str) -> dict:
    doc = await load_tests(p.slug)
    tests = doc["tests"]
    res = await run_in_sandbox(make_job(p, code, [t["args"] for t in tests], [t["expected"] for t in tests]))
    verdict, fail = verdict_of(res, len(tests))
    passed = 0
    for r in res["results"]:
        if not r.get("ok"):
            break
        passed += 1
    out = {
        "verdict": verdict, "passed": passed, "total": len(tests),
        "compile_error": res["error"] if res["status"] == "compile_error" else None,
        "runtime_ms": round(sum(r.get("ms") or 0 for r in res["results"]), 1) if verdict == "Accepted" else None,
        "failing": None,
    }
    if fail is not None:
        r = res["results"][fail] if fail < len(res["results"]) else {"ok": False, "error": res["error"]}
        out["failing"] = {"index": fail, "is_example": fail < doc["examples"], **_case_view(p, tests[fail]["args"], r, tests[fail]["expected"])}
    return out


def problem_or_404(slug: str) -> Problem:
    p = BY_SLUG.get(slug)
    if not p:
        raise KeyError(slug)
    return p
