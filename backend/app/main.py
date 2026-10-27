import asyncio
import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from . import chat, judge, llm
from .catalog import BY_SLUG, PATTERNS, PROBLEMS, Problem
from .core import Doc, RunnerError, db, ensure_indexes, now, settings
from .designs import BY_SLUG as DESIGNS_BY_SLUG
from .designs import DESIGNS, Design
from .schemas import (
    ChatHistory,
    ChatIn,
    ChatMessage,
    ChatReply,
    CodeIn,
    DesignChatIn,
    DesignDetail,
    DesignDraftIn,
    DesignSummary,
    Example,
    Health,
    ProblemDetail,
    ProblemList,
    RunIn,
    RunResult,
    Session,
    SessionIn,
    SessionPatch,
    SessionStats,
    Submission,
    SubmitResult,
)

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await ensure_indexes()
    task = asyncio.create_task(judge.seed_all())
    yield
    task.cancel()


app = FastAPI(title="KodeTrain API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)


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
@app.get("/api/health", response_model=Health)
async def health() -> Doc:
    return {"ok": True, "seeding": judge.seed_state}


# ---------------------------------------------------------------- problems
@app.get("/api/problems", response_model=ProblemList)
async def list_problems(session_id: str | None = None) -> Doc:
    prog = await progress_map(session_id)
    return {"patterns": PATTERNS, "problems": [problem_summary(p, prog.get(p.slug)) for p in PROBLEMS]}


async def example_views(p: Problem) -> list[Example]:
    tests = await db().problem_tests.find_one({"_id": p.slug}, {"tests": {"$slice": len(p.examples)}, "fingerprint": 1})
    out = []
    for i, ex in enumerate(p.examples):
        exp = tests["tests"][i]["expected"] if tests and i < len(tests["tests"]) else None
        out.append(
            Example(
                args=[judge.preview(v) for v in judge.to_editor(p, ex["args"])],
                output=judge.preview(exp) if tests else None,
                note=ex.get("note"),
            )
        )
    return out


@app.get("/api/problems/{slug}", response_model=ProblemDetail)
async def problem_detail(slug: str, session_id: str | None = None) -> Doc:
    p = get_problem(slug)
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
        "examples": await example_views(p),
        "default_cases": [[json.dumps(v) for v in judge.to_editor(p, ex["args"])] for ex in p.examples],
        "starter_code": p.starter_code(),
        "draft": draft,
    }


# ---------------------------------------------------------------- sessions
@app.get("/api/sessions", response_model=list[Session])
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


@app.post("/api/sessions", status_code=201, response_model=Session)
async def create_session(body: SessionIn) -> Doc:
    doc = {**body.model_dump(), "created_at": now(), "last_active_at": now()}
    res = await db().sessions.insert_one(doc)
    doc["_id"] = res.inserted_id
    return session_out(doc)


@app.patch("/api/sessions/{session_id}", response_model=Session)
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
    for coll in ("submissions", "drafts", "progress", "chats", "pattern_chats", "design_drafts", "design_chats"):
        await db()[coll].delete_many({"session_id": session_id})
    await db().sessions.delete_one({"_id": s["_id"]})


@app.get("/api/sessions/{session_id}/stats", response_model=SessionStats)
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
@app.post("/api/sessions/{session_id}/problems/{slug}/run", response_model=RunResult)
async def run(session_id: str, slug: str, body: RunIn) -> Doc:
    await get_session(session_id)
    p = get_problem(slug)
    try:
        return await judge.run_cases(p, body.code, body.cases)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    except RunnerError as e:
        raise HTTPException(503, str(e)) from e


@app.post("/api/sessions/{session_id}/problems/{slug}/submit", response_model=SubmitResult)
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


@app.get("/api/sessions/{session_id}/problems/{slug}/submissions", response_model=list[Submission])
async def list_submissions(session_id: str, slug: str, limit: int = Query(30, ge=1, le=100)) -> list[Doc]:
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


# ---------------------------------------------------------------- chat
def require_chat() -> llm.LLMProvider:
    try:
        return llm.provider()
    except ValueError as e:
        raise HTTPException(503, str(e)) from e


def get_pattern(slug: str) -> str:
    if slug not in PATTERNS:
        raise HTTPException(404, "Pattern not found")
    return slug


async def load_chat(coll: str, key: Doc) -> Doc:
    doc = await db()[coll].find_one(key)
    return {"messages": doc["messages"] if doc else []}


async def chat_turn(
    provider: llm.LLMProvider, coll: str, key: Doc, system: str, message: str, turn: str, image: str | None = None
) -> Doc:
    history = [ChatMessage(**m) for m in (await load_chat(coll, key))["messages"]]
    try:
        text = await chat.reply(provider, system, history, turn, image)
    except llm.ChatError as e:
        raise HTTPException(502, str(e)) from e
    answer = ChatMessage(role="assistant", content=text)
    await db()[coll].update_one(
        key,
        {
            "$push": {"messages": {"$each": [{"role": "user", "content": message}, answer.model_dump()]}},
            "$set": {"updated_at": now()},
        },
        upsert=True,
    )
    return {"message": answer}


@app.get("/api/sessions/{session_id}/problems/{slug}/chat", response_model=ChatHistory)
async def get_chat(session_id: str, slug: str) -> Doc:
    await get_session(session_id)
    get_problem(slug)
    return await load_chat("chats", {"session_id": session_id, "problem": slug})


@app.post("/api/sessions/{session_id}/problems/{slug}/chat", response_model=ChatReply)
async def send_chat(session_id: str, slug: str, body: ChatIn) -> Doc:
    provider = require_chat()
    await get_session(session_id)
    p = get_problem(slug)
    system = chat.build_system_prompt(p, await example_views(p))
    turn = chat.user_turn(body.message, body.code)
    return await chat_turn(provider, "chats", {"session_id": session_id, "problem": slug}, system, body.message, turn)


@app.delete("/api/sessions/{session_id}/problems/{slug}/chat", status_code=204)
async def clear_chat(session_id: str, slug: str) -> None:
    await db().chats.delete_one({"session_id": session_id, "problem": slug})


@app.get("/api/sessions/{session_id}/patterns/{slug}/chat", response_model=ChatHistory)
async def get_pattern_chat(session_id: str, slug: str) -> Doc:
    get_pattern(slug)
    await get_session(session_id)
    return await load_chat("pattern_chats", {"session_id": session_id, "pattern": slug})


@app.post("/api/sessions/{session_id}/patterns/{slug}/chat", response_model=ChatReply)
async def send_pattern_chat(session_id: str, slug: str, body: ChatIn) -> Doc:
    provider = require_chat()
    get_pattern(slug)
    await get_session(session_id)
    system = chat.build_pattern_prompt(slug, [p for p in PROBLEMS if p.pattern == slug])
    turn = chat.user_turn(body.message, body.code)
    key = {"session_id": session_id, "pattern": slug}
    return await chat_turn(provider, "pattern_chats", key, system, body.message, turn)


@app.delete("/api/sessions/{session_id}/patterns/{slug}/chat", status_code=204)
async def clear_pattern_chat(session_id: str, slug: str) -> None:
    await db().pattern_chats.delete_one({"session_id": session_id, "pattern": slug})


# ---------------------------------------------------------------- system design
def get_design(slug: str) -> Design:
    if slug not in DESIGNS_BY_SLUG:
        raise HTTPException(404, "Design question not found")
    return DESIGNS_BY_SLUG[slug]


def design_summary(d: Design) -> Doc:
    return {"slug": d.slug, "title": d.title, "difficulty": d.difficulty, "tags": d.tags, "summary": d.summary}


@app.get("/api/designs", response_model=list[DesignSummary])
async def list_designs() -> list[Doc]:
    return [design_summary(d) for d in DESIGNS]


@app.get("/api/designs/{slug}", response_model=DesignDetail)
async def design_detail(slug: str, session_id: str | None = None) -> Doc:
    d = get_design(slug)
    draft = await db().design_drafts.find_one({"session_id": session_id, "design": slug}) if session_id else None
    return {
        **design_summary(d),
        "prompt": d.prompt,
        "functional": d.functional,
        "non_functional": d.non_functional,
        "scale": d.scale,
        "fundamentals": d.fundamentals,
        "scene": draft["scene"] if draft else None,
        "notes": draft.get("notes", "") if draft else "",
    }


@app.put("/api/sessions/{session_id}/designs/{slug}/draft", status_code=204)
async def save_design_draft(session_id: str, slug: str, body: DesignDraftIn) -> None:
    get_design(slug)
    await get_session(session_id)
    await db().design_drafts.update_one(
        {"session_id": session_id, "design": slug}, {"$set": {**body.model_dump(), "updated_at": now()}}, upsert=True
    )


@app.get("/api/sessions/{session_id}/designs/{slug}/chat", response_model=ChatHistory)
async def get_design_chat(session_id: str, slug: str) -> Doc:
    get_design(slug)
    await get_session(session_id)
    return await load_chat("design_chats", {"session_id": session_id, "design": slug})


@app.post("/api/sessions/{session_id}/designs/{slug}/chat", response_model=ChatReply)
async def send_design_chat(session_id: str, slug: str, body: DesignChatIn) -> Doc:
    provider = require_chat()
    d = get_design(slug)
    await get_session(session_id)
    turn = chat.design_turn(body.message, body.notes)
    key = {"session_id": session_id, "design": slug}
    return await chat_turn(provider, "design_chats", key, chat.build_design_prompt(d), body.message, turn, body.diagram)


@app.delete("/api/sessions/{session_id}/designs/{slug}/chat", status_code=204)
async def clear_design_chat(session_id: str, slug: str) -> None:
    await db().design_chats.delete_one({"session_id": session_id, "design": slug})
