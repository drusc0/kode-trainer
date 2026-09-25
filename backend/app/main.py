import asyncio
import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Literal

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import judge
from .catalog import BY_SLUG, PATTERNS, PROBLEMS, Problem
from .core import Doc, RunnerError, db, ensure_indexes, now, settings

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await ensure_indexes()
    task = asyncio.create_task(judge.seed_all())
    yield
    task.cancel()


app = FastAPI(title="KodeTrain API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"])


# ---------------------------------------------------------------- models
Target = Literal["google", "meta", "general"]


class SessionIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    target: Target = "general"
    notes: str = Field(default="", max_length=2000)


class SessionPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    target: Target | None = None
    notes: str | None = Field(default=None, max_length=2000)


class CodeIn(BaseModel):
    code: str = Field(max_length=settings.max_code_bytes)


class RunIn(CodeIn):
    cases: list[list[Any]] = Field(min_length=1, max_length=settings.max_custom_cases)


# ---------------------------------------------------------------- helpers
def oid(s: str) -> ObjectId:
    try:
        return ObjectId(s)
    except (InvalidId, TypeError):
        raise HTTPException(404, "Session not found") from None


async def get_session(session_id: str) -> Doc:
    s = await db().sessions.find_one({"_id": oid(session_id)})
    if not s:
        raise HTTPException(404, "Session not found")
    return s


def get_problem(slug: str) -> Problem:
    try:
        return judge.problem_or_404(slug)
    except KeyError:
        raise HTTPException(404, "Problem not found") from None


def session_out(s: Doc, solved: int = 0, attempted: int = 0) -> Doc:
    return {
        "id": str(s["_id"]),
        "name": s["name"],
        "target": s["target"],
        "notes": s.get("notes", ""),
        "created_at": s["created_at"],
        "last_active_at": s.get("last_active_at"),
        "solved": solved,
        "attempted": attempted,
    }


def problem_summary(p: Problem, prog: Doc | None) -> Doc:
    return {
        "slug": p.slug,
        "title": p.title,
        "difficulty": p.difficulty,
        "pattern": p.pattern,
        "topics": p.topics,
        "companies": p.companies,
        "status": ("solved" if prog.get("solved") else "attempted") if prog else None,
        "attempts": prog.get("attempts", 0) if prog else 0,
    }


async def progress_map(session_id: str | None) -> dict[str, Doc]:
    if not session_id:
        return {}
    return {d["problem"]: d async for d in db().progress.find({"session_id": session_id})}


# ---------------------------------------------------------------- health
@app.get("/api/health")
async def health() -> Doc:
    return {"ok": True, "seeding": judge.seed_state}


# ---------------------------------------------------------------- problems
@app.get("/api/problems")
async def list_problems(session_id: str | None = None) -> Doc:
    prog = await progress_map(session_id)
    return {"patterns": PATTERNS, "problems": [problem_summary(p, prog.get(p.slug)) for p in PROBLEMS]}


@app.get("/api/problems/{slug}")
async def problem_detail(slug: str, session_id: str | None = None) -> Doc:
    p = get_problem(slug)
    tests = await db().problem_tests.find_one({"_id": slug}, {"tests": {"$slice": len(p.examples)}, "fingerprint": 1})
    examples = []
    for i, ex in enumerate(p.examples):
        exp = tests["tests"][i]["expected"] if tests and i < len(tests["tests"]) else None
        examples.append(
            {
                "args": [judge.preview(v) for v in judge.to_editor(p, ex["args"])],
                "output": judge.preview(exp) if tests else None,
                "note": ex.get("note"),
            }
        )
    draft, prog = None, None
    if session_id:
        d = await db().drafts.find_one({"session_id": session_id, "problem": slug})
        draft = d["code"] if d else None
        prog = await db().progress.find_one({"session_id": session_id, "problem": slug})
    return {
        **problem_summary(p, prog),
        "statement": p.statement,
        "constraints": p.constraints,
        "hints": p.hints,
        "kind": p.kind,
        "fields": judge.editor_fields(p),
        "examples": examples,
        "default_cases": [[json.dumps(v) for v in judge.to_editor(p, ex["args"])] for ex in p.examples],
        "starter_code": p.starter_code(),
        "draft": draft,
    }


# ---------------------------------------------------------------- sessions
@app.get("/api/sessions")
async def list_sessions() -> list[Doc]:
    counts: dict[str, Doc] = {}
    async for row in db().progress.aggregate(
        [{"$group": {"_id": "$session_id", "solved": {"$sum": {"$cond": ["$solved", 1, 0]}}, "attempted": {"$sum": 1}}}]
    ):
        counts[row["_id"]] = row
    out = []
    async for s in db().sessions.find().sort("created_at", -1):
        c = counts.get(str(s["_id"]), {})
        out.append(session_out(s, c.get("solved", 0), c.get("attempted", 0)))
    return out


@app.post("/api/sessions", status_code=201)
async def create_session(body: SessionIn) -> Doc:
    doc = {**body.model_dump(), "created_at": now(), "last_active_at": now()}
    res = await db().sessions.insert_one(doc)
    doc["_id"] = res.inserted_id
    return session_out(doc)


@app.patch("/api/sessions/{session_id}")
async def update_session(session_id: str, body: SessionPatch) -> Doc:
    s = await get_session(session_id)
    changes = {k: v for k, v in body.model_dump().items() if v is not None}
    if changes:
        await db().sessions.update_one({"_id": s["_id"]}, {"$set": changes})
        s.update(changes)
    return session_out(s)


@app.delete("/api/sessions/{session_id}", status_code=204)
async def delete_session(session_id: str) -> None:
    s = await get_session(session_id)
    for coll in ("submissions", "drafts", "progress"):
        await db()[coll].delete_many({"session_id": session_id})
    await db().sessions.delete_one({"_id": s["_id"]})


@app.get("/api/sessions/{session_id}/stats")
async def session_stats(session_id: str) -> Doc:
    await get_session(session_id)
    prog = await progress_map(session_id)
    by_diff = {d: {"solved": 0, "total": 0} for d in ("Easy", "Medium", "Hard")}
    by_pattern = {pt: {"solved": 0, "total": 0} for pt in PATTERNS}
    for p in PROBLEMS:
        solved = bool(prog.get(p.slug, {}).get("solved"))
        for bucket in (by_diff[p.difficulty], by_pattern[p.pattern]):
            bucket["total"] += 1
            bucket["solved"] += solved
    total_subs = await db().submissions.count_documents({"session_id": session_id})
    accepted = await db().submissions.count_documents({"session_id": session_id, "verdict": "Accepted"})
    recent = []
    async for sub in (
        db().submissions.find({"session_id": session_id}, {"code": 0, "failing": 0}).sort("created_at", -1).limit(12)
    ):
        prob = BY_SLUG.get(sub["problem"])
        recent.append(
            {
                "id": str(sub["_id"]),
                "problem": sub["problem"],
                "title": prob.title if prob else sub["problem"],
                "verdict": sub["verdict"],
                "created_at": sub["created_at"],
                "runtime_ms": sub.get("runtime_ms"),
            }
        )
    return {
        "by_difficulty": by_diff,
        "by_pattern": by_pattern,
        "submissions": total_subs,
        "accepted": accepted,
        "recent": recent,
    }


# ---------------------------------------------------------------- drafts
@app.put("/api/sessions/{session_id}/problems/{slug}/draft", status_code=204)
async def save_draft(session_id: str, slug: str, body: CodeIn) -> None:
    await get_session(session_id)
    get_problem(slug)
    await db().drafts.update_one(
        {"session_id": session_id, "problem": slug}, {"$set": {"code": body.code, "updated_at": now()}}, upsert=True
    )


@app.delete("/api/sessions/{session_id}/problems/{slug}/draft", status_code=204)
async def reset_draft(session_id: str, slug: str) -> None:
    await db().drafts.delete_one({"session_id": session_id, "problem": slug})


# ---------------------------------------------------------------- run & submit
@app.post("/api/sessions/{session_id}/problems/{slug}/run")
async def run(session_id: str, slug: str, body: RunIn) -> Doc:
    await get_session(session_id)
    p = get_problem(slug)
    try:
        return await judge.run_cases(p, body.code, body.cases)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    except RunnerError as e:
        raise HTTPException(503, str(e)) from e


@app.post("/api/sessions/{session_id}/problems/{slug}/submit")
async def submit(session_id: str, slug: str, body: CodeIn) -> Doc:
    s = await get_session(session_id)
    p = get_problem(slug)
    try:
        result = await judge.submit(p, body.code)
    except LookupError as e:
        raise HTTPException(503, str(e)) from e
    except RunnerError as e:
        raise HTTPException(503, str(e)) from e
    t = now()
    doc = {"session_id": session_id, "problem": slug, "code": body.code, "created_at": t, **result}
    ins = await db().submissions.insert_one(doc)
    accepted = result["verdict"] == "Accepted"
    await db().progress.update_one(
        {"session_id": session_id, "problem": slug},
        {
            "$inc": {"attempts": 1},
            "$set": {"last_verdict": result["verdict"], "last_attempt_at": t},
            "$setOnInsert": {"first_attempt_at": t, "solved": False},
        },
        upsert=True,
    )
    if accepted:
        await db().progress.update_one(
            {"session_id": session_id, "problem": slug, "solved": False}, {"$set": {"solved": True, "solved_at": t}}
        )
        await db().progress.update_one(
            {"session_id": session_id, "problem": slug}, {"$min": {"best_runtime_ms": result["runtime_ms"]}}
        )
    await db().drafts.update_one(
        {"session_id": session_id, "problem": slug}, {"$set": {"code": body.code, "updated_at": t}}, upsert=True
    )
    await db().sessions.update_one({"_id": s["_id"]}, {"$set": {"last_active_at": t}})
    return {"submission_id": str(ins.inserted_id), **result}


@app.get("/api/sessions/{session_id}/problems/{slug}/submissions")
async def list_submissions(session_id: str, slug: str, limit: int = Query(30, le=100)) -> list[Doc]:
    await get_session(session_id)
    out = []
    async for sub in (
        db().submissions.find({"session_id": session_id, "problem": slug}).sort("created_at", -1).limit(limit)
    ):
        out.append(
            {
                "id": str(sub["_id"]),
                "verdict": sub["verdict"],
                "passed": sub["passed"],
                "total": sub["total"],
                "runtime_ms": sub.get("runtime_ms"),
                "created_at": sub["created_at"],
                "code": sub["code"],
            }
        )
    return out
