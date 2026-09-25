# Typed API Contract + Problem Chat Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Pydantic models the single source of truth for the API contract, generate the frontend's TypeScript types from them, then add a Socratic chat assistant to the coding workspace.

**Architecture:** `backend/app/schemas.py` defines every request and response model. Routes declare `response_model=`, so `/openapi.json` fully describes the API, and `openapi-typescript` turns that into `frontend/src/api.gen.ts`. The chat is a single Anthropic Messages API call per turn: a stable system prompt (persona + problem + hidden reference solution) plus the stored history and a user turn carrying the current editor code. It is persisted per `(session_id, problem)` in Mongo.

**Tech Stack:** FastAPI + Pydantic v2, Motor/MongoDB, `anthropic` Python SDK 1.x (`AsyncAnthropic`), React 18 + TypeScript, `openapi-typescript` 7, `uv` for running backend tooling locally, pytest, ruff, mypy.

**Spec:** `docs/superpowers/specs/2026-09-25-typed-api-and-chat-design.md`

## Global Constraints

- Two logical changes: typed-contract work lands as `refactor:` commits with **no behavior change**; the chat lands as `feat:` commits.
- Keep the repo's pip `requirements.txt` convention; dev tools go in `backend/requirements-dev.txt`.
- Run backend tooling with `uv run -q --python 3.12 --with-requirements requirements.txt --with-requirements requirements-dev.txt` from `backend/` (wrapped by `make test-api` / `make gen-api`).
- ruff + `mypy --strict` apply to **new** files only: `app/schemas.py`, `app/chat.py`, `tests/`. Existing modules are not retrofitted.
- `ANTHROPIC_API_KEY` is optional: the app must start and work without it; only chat returns 503.
- `CHAT_MODEL` defaults to `claude-sonnet-5`.
- Chat persona: Socratic colleague; never writes the full solution code unless explicitly asked; never reveals the reference solution.
- History sent to the model is capped at the last 40 messages.
- All examples stay visible in the description (no interview mode).
- Commit messages follow Conventional Commits and end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **Chat with no `ANTHROPIC_API_KEY`**: expect a 503 that says how to fix it, and everything else keeps working. Pinned in Task 4 (`test_chat_without_key_returns_503`).
2. **Whitespace-only chat message**: expect a 422, with no model call and nothing stored. Pinned in Task 4 (`test_blank_message_is_rejected`).
3. **Model refusal or API failure**: expect a readable error in the chat, with history left untouched and the user's text restored to the input. Pinned in Task 3 (`test_reply_refusal_raises_chat_error`). "Nothing persisted" holds by construction (persist happens after `reply` returns); Task 6 checks it manually.
4. **Long conversations**: expect only the last 40 messages to be sent, still starting with a `user` turn. Pinned in Task 3 (`test_reply_caps_history`).
5. **Empty editor**: an empty or whitespace-only editor adds no code block to the turn. Pinned in Task 3 (`test_user_turn_without_code_is_just_the_message`).

---

## File Map

| File | Change | Responsibility |
|---|---|---|
| `backend/app/schemas.py` | create | Every API request/response model |
| `backend/app/main.py` | modify | Routes declare response models; `example_views` helper; chat routes |
| `backend/app/chat.py` | create | Persona, prompt building, the Claude call |
| `backend/app/core.py` | modify | `anthropic_api_key`, `chat_model` settings; `chats` index |
| `backend/requirements.txt` | modify | add `anthropic` |
| `backend/requirements-dev.txt` | create | pytest, ruff, mypy |
| `backend/pytest.ini`, `backend/ruff.toml` | create | test path + line length |
| `backend/tests/test_openapi.py` | create | No untyped responses |
| `backend/tests/test_chat.py` | create | Prompt, reply, route validation |
| `frontend/src/api.gen.ts` | generated | Types from OpenAPI (committed) |
| `frontend/src/api.ts` | modify | Aliases to generated types; chat calls |
| `frontend/src/components/ChatPanel.tsx` | create | Chat tab UI |
| `frontend/src/pages/WorkspacePage.tsx` | modify | Third left tab |
| `frontend/src/styles.css` | modify | Chat styles |
| `frontend/package.json` | modify | `openapi-typescript` dev dep |
| `Makefile`, `.env.example`, `docker-compose.yml`, `README.md` | modify | Targets, env vars, docs |

---

### Task 1: Pydantic schemas for the existing API

**Files:**
- Create: `backend/app/schemas.py`, `backend/requirements-dev.txt`, `backend/pytest.ini`, `backend/ruff.toml`, `backend/tests/__init__.py` (empty), `backend/tests/test_openapi.py`
- Modify: `backend/app/main.py` (models section, `problem_detail`, every JSON route decorator), `Makefile`

**Interfaces:**
- Produces: `app.schemas` with `Target`, `Difficulty`, `SessionIn`, `SessionPatch`, `CodeIn`, `RunIn`, `Session`, `ProblemSummary`, `ProblemList`, `EditorField`, `Example`, `ProblemDetail`, `CaseResult`, `RunResult`, `FailingCase`, `SubmitResult`, `Submission`, `Bucket`, `DifficultyBuckets`, `RecentSubmission`, `SessionStats`, `SeedState`, `Health`.
- Produces: `main.example_views(p: Problem) -> list[Example]` (used by Task 4).
- Produces: `make test-api`.

- [ ] **Step 1: Add dev tooling config**

`backend/requirements-dev.txt`:
```text
pytest>=8,<9
ruff>=0.6
mypy>=1.11
```

`backend/pytest.ini`:
```ini
[pytest]
pythonpath = .
testpaths = tests
```

`backend/ruff.toml`:
```toml
line-length = 120
```

Create an empty `backend/tests/__init__.py`.

Append to `Makefile`, and add `test-api` to the `.PHONY` line:
```make
PY = cd backend && uv run -q --python 3.12 --with-requirements requirements.txt --with-requirements requirements-dev.txt
TYPED = app/schemas.py app/chat.py

test-api:      ## backend unit tests + ruff/mypy on the typed modules
	$(PY) pytest -q
	$(PY) ruff check $(TYPED) tests
	$(PY) ruff format --check $(TYPED) tests
	$(PY) mypy --strict --follow-imports=silent $(TYPED)
```
(`app/chat.py` doesn't exist until Task 3. Until then, run the tools directly, as the steps below do.)

- [ ] **Step 2: Write the failing test**

`backend/tests/test_openapi.py`:
```python
from app.main import app


def test_every_json_response_has_a_schema() -> None:
    untyped = []
    for path, methods in app.openapi()["paths"].items():
        for method, op in methods.items():
            for code, resp in op["responses"].items():
                if code.startswith("2") and code != "204":
                    schema = resp.get("content", {}).get("application/json", {}).get("schema")
                    if not schema:
                        untyped.append(f"{method.upper()} {path} -> {code}")
    assert untyped == []
```

- [ ] **Step 3: Run it to verify it fails**

Run: `cd backend && uv run -q --python 3.12 --with-requirements requirements.txt --with-requirements requirements-dev.txt pytest -q`
Expected: FAIL. The list names every current route, for example `GET /api/health -> 200` and `GET /api/problems -> 200`.

- [ ] **Step 4: Create `backend/app/schemas.py`**

```python
"""Request and response models: the API contract. The frontend's types are generated from these."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from .core import settings

Target = Literal["google", "meta", "general"]
Difficulty = Literal["Easy", "Medium", "Hard"]


# ---------------------------------------------------------------- requests
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


# ---------------------------------------------------------------- responses
class SeedState(BaseModel):
    status: str
    done: int
    total: int
    errors: list[str]


class Health(BaseModel):
    ok: bool
    seeding: SeedState


class Session(BaseModel):
    id: str
    name: str
    target: Target
    notes: str
    created_at: datetime
    last_active_at: datetime | None
    solved: int
    attempted: int


class ProblemSummary(BaseModel):
    slug: str
    title: str
    difficulty: Difficulty
    pattern: str
    topics: list[str]
    companies: list[str]
    status: Literal["solved", "attempted"] | None
    attempts: int


class ProblemList(BaseModel):
    patterns: list[str]
    problems: list[ProblemSummary]


class EditorField(BaseModel):
    name: str
    type: str


class Example(BaseModel):
    args: list[str]
    output: str | None
    note: str | None = None


class ProblemDetail(ProblemSummary):
    statement: str
    constraints: list[str]
    hints: list[str]
    kind: Literal["function", "design"]
    fields: list[EditorField]
    examples: list[Example]
    default_cases: list[list[str]]
    starter_code: str
    draft: str | None


class CaseResult(BaseModel):
    args: list[str]
    ok: bool | None = None
    output: str | None = None
    expected: str | None = None
    stdout: str | None = None
    error: str | None = None
    ms: float | None = None
    input_error: str | None = None


class RunResult(BaseModel):
    verdict: str
    compile_error: str | None
    cases: list[CaseResult]
    passed: int
    runtime_ms: float | None


class FailingCase(CaseResult):
    index: int
    is_example: bool


class SubmitResult(BaseModel):
    submission_id: str
    verdict: str
    passed: int
    total: int
    compile_error: str | None
    runtime_ms: float | None
    failing: FailingCase | None


class Submission(BaseModel):
    id: str
    verdict: str
    passed: int
    total: int
    runtime_ms: float | None
    created_at: datetime
    code: str


class Bucket(BaseModel):
    solved: int
    total: int


class DifficultyBuckets(BaseModel):
    Easy: Bucket
    Medium: Bucket
    Hard: Bucket


class RecentSubmission(BaseModel):
    id: str
    problem: str
    title: str
    verdict: str
    created_at: datetime
    runtime_ms: float | None


class SessionStats(BaseModel):
    by_difficulty: DifficultyBuckets
    by_pattern: dict[str, Bucket]
    submissions: int
    accepted: int
    recent: list[RecentSubmission]
```

- [ ] **Step 5: Wire the models into `main.py`**

1. Replace the `from pydantic import BaseModel, Field` import and the whole `# ---- models` section (`Target`, `SessionIn`, `SessionPatch`, `CodeIn`, `RunIn`) with:
```python
from .schemas import (
    CodeIn, Example, Health, ProblemDetail, ProblemList, RunIn, RunResult, Session, SessionIn, SessionPatch,
    SessionStats, Submission, SubmitResult,
)
```
Also drop `Literal` from the `typing` import if it is now unused.

2. Extract the example-building loop from `problem_detail` into a helper placed above it:
```python
async def example_views(p: Problem) -> list[Example]:
    tests = await db().problem_tests.find_one({"_id": p.slug}, {"tests": {"$slice": len(p.examples)}, "fingerprint": 1})
    out = []
    for i, ex in enumerate(p.examples):
        exp = tests["tests"][i]["expected"] if tests and i < len(tests["tests"]) else None
        out.append(Example(args=[judge.preview(v) for v in judge.to_editor(p, ex["args"])],
                           output=judge.preview(exp) if tests else None, note=ex.get("note")))
    return out
```
Then in `problem_detail`, delete the `tests = …` line and the loop, and set `"examples": await example_views(p),` in the returned dict.

3. Add `response_model=` to each JSON route decorator:

| Route | `response_model=` |
|---|---|
| `GET /api/health` | `Health` |
| `GET /api/problems` | `ProblemList` |
| `GET /api/problems/{slug}` | `ProblemDetail` |
| `GET /api/sessions` | `list[Session]` |
| `POST /api/sessions` | `Session` (keep `status_code=201`) |
| `PATCH /api/sessions/{session_id}` | `Session` |
| `GET /api/sessions/{session_id}/stats` | `SessionStats` |
| `POST …/run` | `RunResult` |
| `POST …/submit` | `SubmitResult` |
| `GET …/submissions` | `list[Submission]` |

Route bodies keep returning dicts. FastAPI validates and serializes them through the model.

- [ ] **Step 6: Run tests and linters**

Run (from `backend/`, with the `uv run …` prefix from Step 3):
- `pytest -q` → PASS
- `ruff check app/schemas.py tests && ruff format --check app/schemas.py tests` → clean (run `ruff format app/schemas.py tests` first if needed)
- `mypy --strict --follow-imports=silent app/schemas.py` → `Success`

- [ ] **Step 7: Smoke-check that behavior is unchanged**

Run `make up`, then open http://localhost:8080. Create a session, open Two Sum, click Run, click Submit, open the Submissions tab, then go back to the Sessions page to see its stats. Expected: everything renders as before and `make logs` shows no 500s. Any `ResponseValidationError` in the logs means a model doesn't match a real response. Fix the model, not the route.

- [ ] **Step 8: Commit**

```bash
git add backend Makefile
git commit -m "refactor: declare Pydantic response models for every API route"
```

---

### Task 2: Generate frontend types from OpenAPI

**Files:**
- Create: `frontend/src/api.gen.ts` (generated)
- Modify: `frontend/package.json`, `frontend/src/api.ts:1-86` (interfaces block and `api` request bodies), `Makefile`

**Interfaces:**
- Consumes: the schemas from Task 1 (`components["schemas"]["<ModelName>"]`).
- Produces: `api.ts` keeps exporting `Difficulty`, `Target`, `Status`, `Session`, `ProblemSummary`, `ProblemDetail`, `CaseResult`, `RunResult`, `SubmitResult`, `Submission`, `Bucket`, `SessionStats`, now as aliases. Produces `make gen-api` / `make check-api`.

- [ ] **Step 1: Add the generator**

Run: `cd frontend && npm install -D openapi-typescript@^7.13.0`

Append to `Makefile`, and add `gen-api check-api` to `.PHONY`:
```make
gen-api:       ## regenerate frontend/src/api.gen.ts from the FastAPI models
	$(PY) python -c "import json; from app.main import app; print(json.dumps(app.openapi()))" > ../frontend/openapi.json
	cd frontend && npx openapi-typescript openapi.json -o src/api.gen.ts && rm openapi.json

check-api:     ## fail if api.gen.ts is stale
	$(MAKE) gen-api
	git diff --exit-code frontend/src/api.gen.ts
```

- [ ] **Step 2: Generate**

Run: `make gen-api`
Expected: `frontend/src/api.gen.ts` exists and contains `export interface components` with `ProblemDetail`, `SessionStats` and the other models.

- [ ] **Step 3: Replace the hand-written interfaces in `api.ts`**

Replace everything from `export type Difficulty` down to the end of `interface SessionStats` with:
```ts
import type { components } from "./api.gen";

type Schemas = components["schemas"];

export type Session = Schemas["Session"];
export type ProblemSummary = Schemas["ProblemSummary"];
export type ProblemDetail = Schemas["ProblemDetail"];
export type CaseResult = Schemas["CaseResult"];
export type RunResult = Schemas["RunResult"];
export type SubmitResult = Schemas["SubmitResult"];
export type Submission = Schemas["Submission"];
export type Bucket = Schemas["Bucket"];
export type SessionStats = Schemas["SessionStats"];
export type Difficulty = ProblemSummary["difficulty"];
export type Target = Session["target"];
export type Status = ProblemSummary["status"];
```

Type the request bodies from the same schemas. In the `api` object, replace these three entries:
```ts
  createSession: (body: Schemas["SessionIn"]) =>
    req<Session>("/sessions", { method: "POST", body: JSON.stringify(body) }),
  updateSession: (id: string, body: Schemas["SessionPatch"]) =>
    req<Session>(`/sessions/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  run: (sessionId: string, slug: string, code: string, cases: unknown[][]) =>
    req<RunResult>(`${sp(sessionId, slug)}/run`, { method: "POST", body: JSON.stringify({ code, cases } satisfies Schemas["RunIn"]) }),
```
and in `problems`, change the return type to `req<Schemas["ProblemList"]>`.

- [ ] **Step 4: Type-check and build**

Run: `cd frontend && npm install && npm run build`
Expected: PASS. If `tsc` reports a mismatch, the generated type is now the truth. Adjust the *component* only when the generated type is more accurate (for example, a field that is really nullable). Otherwise fix the Pydantic model and re-run `make gen-api`. Do not re-add hand-written interfaces.

- [ ] **Step 5: Verify the staleness check**

Run: `make check-api` → exit 0.
Then add a throwaway field to `Bucket` in `schemas.py`, run `make check-api` → non-zero exit with a diff. Revert the field and run `make gen-api` again.

- [ ] **Step 6: Commit**

```bash
git add Makefile frontend/package.json frontend/src/api.ts frontend/src/api.gen.ts
git commit -m "refactor: generate frontend API types from the OpenAPI schema"
```

---

### Task 3: Chat core (`chat.py`)

**Files:**
- Create: `backend/app/chat.py`, `backend/tests/test_chat.py`
- Modify: `backend/requirements.txt`, `backend/app/core.py` (Settings)

**Interfaces:**
- Consumes: `app.schemas.Example` (Task 1), `app.catalog.Problem`.
- Produces (used by Task 4):
  - `chat.ChatError(RuntimeError)`
  - `chat.HISTORY_LIMIT = 40`
  - `chat.build_system_prompt(p: Problem, examples: list[Example]) -> str`
  - `chat.user_turn(message: str, code: str) -> str`
  - `async chat.reply(client: AsyncAnthropic, model: str, system: str, history: list[ChatMessage], turn: str) -> str`
  - `chat.client() -> AsyncAnthropic`
- Produces in `schemas.py`: `ChatMessage {role: Literal["user","assistant"], content: str}`
- Produces in `core.Settings`: `anthropic_api_key: str`, `chat_model: str`

- [ ] **Step 1: Dependencies and settings**

Append to `backend/requirements.txt`:
```text
anthropic>=1.8,<2
```

In `core.py`, add to `Settings`:
```python
    anthropic_api_key: str = os.environ.get("ANTHROPIC_API_KEY", "")
    chat_model: str = os.environ.get("CHAT_MODEL", "claude-sonnet-5")
```

Append to `schemas.py`:
```python
# ---------------------------------------------------------------- chat
class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
```

- [ ] **Step 2: Write the failing tests**

`backend/tests/test_chat.py`:
```python
import asyncio
from types import SimpleNamespace
from typing import Any, cast

import pytest
from anthropic import AsyncAnthropic

from app import chat
from app.catalog import BY_SLUG
from app.schemas import ChatMessage, Example

TWO_SUM = BY_SLUG["two-sum"]
EXAMPLES = [
    Example(args=["[2, 7, 11, 15]", "9"], output="[0, 1]", note="nums[0] + nums[1] = 9."),
    Example(args=["[3, 2, 4]", "6"], output="[1, 2]"),
]


class FakeMessages:
    def __init__(self, response: Any) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []

    async def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        return self.response


def fake_client(text: str, stop_reason: str = "end_turn") -> tuple[AsyncAnthropic, FakeMessages]:
    messages = FakeMessages(SimpleNamespace(stop_reason=stop_reason, content=[SimpleNamespace(type="text", text=text)]))
    return cast(AsyncAnthropic, SimpleNamespace(messages=messages)), messages


def test_system_prompt_carries_the_whole_problem() -> None:
    prompt = chat.build_system_prompt(TWO_SUM, EXAMPLES)
    assert TWO_SUM.statement.strip()[:60] in prompt
    assert "nums = [2, 7, 11, 15], target = 9 → [0, 1]" in prompt
    assert "nums = [3, 2, 4], target = 6 → [1, 2]" in prompt
    assert all(h in prompt for h in TWO_SUM.hints)
    assert TWO_SUM.reference.strip() in prompt


def test_user_turn_attaches_code() -> None:
    turn = chat.user_turn("why does this fail?", "def f():\n    return 1\n")
    assert "<my_current_code>" in turn and "return 1" in turn
    assert turn.endswith("why does this fail?")


def test_user_turn_without_code_is_just_the_message() -> None:
    assert chat.user_turn("hint please", "   \n") == "hint please"


def test_reply_sends_history_then_turn_and_returns_text() -> None:
    client, messages = fake_client("Try a hash map.")
    history = [ChatMessage(role="user", content="hi"), ChatMessage(role="assistant", content="hello")]
    out = asyncio.run(chat.reply(client, "claude-sonnet-5", "SYSTEM", history, "a hint?"))
    assert out == "Try a hash map."
    call = messages.calls[0]
    assert call["model"] == "claude-sonnet-5"
    assert call["system"] == "SYSTEM"
    assert call["messages"] == [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
        {"role": "user", "content": "a hint?"},
    ]


def test_reply_caps_history() -> None:
    client, messages = fake_client("ok")
    history = [ChatMessage(role="user" if i % 2 == 0 else "assistant", content=str(i)) for i in range(100)]
    asyncio.run(chat.reply(client, "m", "S", history, "latest"))
    sent = messages.calls[0]["messages"]
    assert len(sent) == chat.HISTORY_LIMIT + 1
    assert sent[0] == {"role": "user", "content": "60"}
    assert sent[-1] == {"role": "user", "content": "latest"}


def test_reply_refusal_raises_chat_error() -> None:
    client, _ = fake_client("", stop_reason="refusal")
    with pytest.raises(chat.ChatError):
        asyncio.run(chat.reply(client, "m", "S", [], "x"))
```

- [ ] **Step 3: Run to verify failure**

Run: `cd backend && uv run -q --python 3.12 --with-requirements requirements.txt --with-requirements requirements-dev.txt pytest tests/test_chat.py -q`
Expected: FAIL with `ImportError: cannot import name 'chat' from 'app'`.

- [ ] **Step 4: Implement `backend/app/chat.py`**

```python
"""The problem chat assistant: a Socratic interview colleague backed by Claude."""

import anthropic
from anthropic import AsyncAnthropic
from anthropic.types import MessageParam

from .catalog import Problem
from .core import settings
from .schemas import ChatMessage, Example

# ponytail: plain cap on what we resend; summarize older turns if long chats start to matter.
# History is stored in user/assistant pairs, so an even cap always starts on a user turn.
HISTORY_LIMIT = 40

PERSONA = """\
You are a friendly senior software engineer pairing with the user while they practise a coding \
interview problem in Python. You are their colleague, not their examiner.

How to help:
- Start from their thinking. If they ask for help without saying what they've tried, ask what \
approach they're considering first.
- Give hints in steps: a gentle nudge first, then a more specific pointer, and the full approach \
only if they're still stuck or ask for it. The problem's official hints below are a good guide.
- When they ask for more examples or edge cases, give concrete inputs with the expected output, \
checked against the reference solution.
- When they ask about their code (it arrives inside <my_current_code>), point to the specific \
line or idea that is wrong and why. Don't rewrite it for them.
- Discuss time and space complexity, trade-offs between approaches and likely interviewer \
follow-ups when that helps.
- Never write the full solution code unless they explicitly ask for it (for example "show me the \
solution"). A short snippet illustrating one idea is fine.
- The reference solution is for your eyes only. Use it to check their reasoning and your own \
claims; don't quote or paraphrase it line by line.
- Keep replies short and conversational (a few sentences or a short list), in Markdown."""


class ChatError(RuntimeError):
    pass


_client: AsyncAnthropic | None = None


def client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


def build_system_prompt(p: Problem, examples: list[Example]) -> str:
    names = [n for n, _ in p.params]
    lines = []
    for i, ex in enumerate(examples, 1):
        inputs = ", ".join(f"{n} = {v}" for n, v in zip(names, ex.args))
        line = f"Example {i}: {inputs} → {ex.output or '(not computed yet)'}"
        lines.append(f"{line}  ({ex.note})" if ex.note else line)
    constraints = "\n".join(f"- {c}" for c in p.constraints)
    hints = "\n".join(f"{i}. {h}" for i, h in enumerate(p.hints, 1))
    return f"""{PERSONA}

<problem title="{p.title}" difficulty="{p.difficulty}" pattern="{p.pattern}">
{p.statement.strip()}

Examples:
{chr(10).join(lines)}

Constraints:
{constraints}
</problem>

<official_hints>
{hints}
</official_hints>

<reference_solution hidden="true">
```python
{p.reference.strip()}
```
</reference_solution>"""


def user_turn(message: str, code: str) -> str:
    if not code.strip():
        return message
    return f"<my_current_code>\n```python\n{code.rstrip()}\n```\n</my_current_code>\n\n{message}"


async def reply(client: AsyncAnthropic, model: str, system: str, history: list[ChatMessage], turn: str) -> str:
    messages: list[MessageParam] = [{"role": m.role, "content": m.content} for m in history[-HISTORY_LIMIT:]]
    messages.append({"role": "user", "content": turn})
    try:
        resp = await client.messages.create(
            model=model,
            max_tokens=16000,
            system=system,
            messages=messages,
            cache_control={"type": "ephemeral"},
        )
    except anthropic.RateLimitError as e:
        raise ChatError("The assistant is busy right now. Try again in a moment.") from e
    except anthropic.APIStatusError as e:
        raise ChatError(f"The assistant returned an error ({e.status_code}).") from e
    except anthropic.APIConnectionError as e:
        raise ChatError("Couldn't reach the assistant. Check your internet connection.") from e
    if resp.stop_reason == "refusal":
        raise ChatError("The assistant declined to answer that. Try rephrasing.")
    return "".join(b.text for b in resp.content if b.type == "text")
```

`test_reply_sends_history_then_turn_and_returns_text` checks `call["messages"]` by equality, so the extra `cache_control` kwarg doesn't affect it.

- [ ] **Step 5: Run tests and linters**

From `backend/`, with the `uv run …` prefix:
- `pytest -q` → all PASS
- `ruff check app/schemas.py app/chat.py tests && ruff format --check app/schemas.py app/chat.py tests` → clean
- `mypy --strict --follow-imports=silent app/schemas.py app/chat.py` → `Success`. If mypy rejects `cache_control=` as an unknown kwarg for the installed SDK, check `python -c "import anthropic, inspect; print(inspect.signature(anthropic.AsyncAnthropic().messages.create))"`. If the parameter isn't there, drop it and put `cache_control` on the system block instead: `system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]`.

- [ ] **Step 6: Commit**

```bash
git add backend/requirements.txt backend/app/core.py backend/app/schemas.py backend/app/chat.py backend/tests/test_chat.py
git commit -m "feat: chat core that prompts Claude as a Socratic interview colleague"
```

---

### Task 4: Chat API routes, persistence and config

**Files:**
- Modify: `backend/app/schemas.py`, `backend/app/main.py` (imports, `delete_session`, new chat section), `backend/app/core.py` (`ensure_indexes`), `.env.example`, `docker-compose.yml` (api `environment`), `backend/tests/test_chat.py`, `frontend/src/api.gen.ts` (regenerated)

**Interfaces:**
- Consumes: `chat.*` from Task 3, `main.example_views` from Task 1.
- Produces: `GET/POST/DELETE /api/sessions/{session_id}/problems/{slug}/chat`, and schemas `ChatIn {message, code}`, `ChatHistory {messages}`, `ChatReply {message}` (used by Task 5 via the generated types).

- [ ] **Step 1: Write the failing tests** (append to `backend/tests/test_chat.py`)

```python
from fastapi.testclient import TestClient

from app.core import settings
from app.main import app

CHAT_URL = "/api/sessions/000000000000000000000000/problems/two-sum/chat"


def test_chat_without_key_returns_503(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "anthropic_api_key", "")
    resp = TestClient(app).post(CHAT_URL, json={"message": "hint?", "code": ""})
    assert resp.status_code == 503
    assert "ANTHROPIC_API_KEY" in resp.json()["detail"]


def test_blank_message_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "anthropic_api_key", "test-key")
    resp = TestClient(app).post(CHAT_URL, json={"message": "   ", "code": ""})
    assert resp.status_code == 422
```
Both tests pass without Mongo: `TestClient(app)` used outside a `with` block skips the lifespan. The key check runs before any DB call, and body validation runs before the handler.

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/test_chat.py -q` (with the `uv run …` prefix)
Expected: both new tests FAIL with 404 (the route doesn't exist yet).

- [ ] **Step 3: Add the request/response schemas** (append to `schemas.py`, after `ChatMessage`)

```python
class ChatIn(BaseModel):
    message: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]
    code: str = Field(default="", max_length=settings.max_code_bytes)


class ChatHistory(BaseModel):
    messages: list[ChatMessage]


class ChatReply(BaseModel):
    message: ChatMessage
```
Update the imports at the top of `schemas.py`: `from typing import Annotated, Any, Literal` and `from pydantic import BaseModel, Field, StringConstraints`.

- [ ] **Step 4: Add the routes to `main.py`**

Imports: change `from . import judge` to `from . import chat, judge`. Add `ChatHistory, ChatIn, ChatMessage, ChatReply` to the `.schemas` import.

In `delete_session`, change the tuple to `("submissions", "drafts", "progress", "chats")`.

Append a new section at the end of the file:
```python
# ---------------------------------------------------------------- chat
@app.get("/api/sessions/{session_id}/problems/{slug}/chat", response_model=ChatHistory)
async def get_chat(session_id: str, slug: str):
    await get_session(session_id)
    get_problem(slug)
    doc = await db().chats.find_one({"session_id": session_id, "problem": slug})
    return {"messages": doc["messages"] if doc else []}


@app.post("/api/sessions/{session_id}/problems/{slug}/chat", response_model=ChatReply)
async def send_chat(session_id: str, slug: str, body: ChatIn):
    if not settings.anthropic_api_key:
        raise HTTPException(503, "Chat is not configured: set ANTHROPIC_API_KEY in .env")
    await get_session(session_id)
    p = get_problem(slug)
    key = {"session_id": session_id, "problem": slug}
    doc = await db().chats.find_one(key)
    history = [ChatMessage(**m) for m in doc["messages"]] if doc else []
    system = chat.build_system_prompt(p, await example_views(p))
    try:
        text = await chat.reply(chat.client(), settings.chat_model, system, history, chat.user_turn(body.message, body.code))
    except chat.ChatError as e:
        raise HTTPException(502, str(e))
    answer = ChatMessage(role="assistant", content=text)
    await db().chats.update_one(
        key,
        {"$push": {"messages": {"$each": [{"role": "user", "content": body.message}, answer.model_dump()]}},
         "$set": {"updated_at": now()}},
        upsert=True)
    return {"message": answer}


@app.delete("/api/sessions/{session_id}/problems/{slug}/chat", status_code=204)
async def clear_chat(session_id: str, slug: str):
    await db().chats.delete_one({"session_id": session_id, "problem": slug})
```

In `core.ensure_indexes`, add:
```python
    await d.chats.create_index([("session_id", 1), ("problem", 1)], unique=True)
```

- [ ] **Step 5: Config**

Append to `.env.example`:
```text

# Optional: enables the chat assistant in the workspace. Get a key at https://console.anthropic.com
ANTHROPIC_API_KEY=
# CHAT_MODEL=claude-sonnet-5
```

In `docker-compose.yml`, add to the `api` service's `environment`:
```yaml
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:-}
      CHAT_MODEL: ${CHAT_MODEL:-claude-sonnet-5}
```

- [ ] **Step 6: Run everything**

Run: `make test-api` → all tests pass; ruff and mypy are clean.
Run: `make gen-api`, then `git diff --stat frontend/src/api.gen.ts` → it now includes `ChatIn`, `ChatHistory`, `ChatReply` and `ChatMessage`.

- [ ] **Step 7: Commit**

```bash
git add backend .env.example docker-compose.yml frontend/src/api.gen.ts
git commit -m "feat: chat API persisted per session and problem"
```

---

### Task 5: Chat tab in the workspace

**Files:**
- Create: `frontend/src/components/ChatPanel.tsx`
- Modify: `frontend/src/api.ts` (types + `api` object), `frontend/src/pages/WorkspacePage.tsx:33,164-199`, `frontend/src/styles.css` (append)

**Interfaces:**
- Consumes: the generated `ChatMessage`, `ChatHistory`, `ChatReply`, `ChatIn` (Task 4).
- Produces: `api.chat(sessionId, slug)`, `api.sendChat(sessionId, slug, message, code)`, `api.clearChat(sessionId, slug)`, and `<ChatPanel sessionId slug code />`.

- [ ] **Step 1: API client**

In `api.ts`, next to the other aliases:
```ts
export type ChatMessage = Schemas["ChatMessage"];
```
In the `api` object, after `submissions`:
```ts
  chat: (sessionId: string, slug: string) => req<Schemas["ChatHistory"]>(`${sp(sessionId, slug)}/chat`),
  sendChat: (sessionId: string, slug: string, message: string, code: string) =>
    req<Schemas["ChatReply"]>(`${sp(sessionId, slug)}/chat`, {
      method: "POST", body: JSON.stringify({ message, code } satisfies Schemas["ChatIn"]),
    }),
  clearChat: (sessionId: string, slug: string) => req<void>(`${sp(sessionId, slug)}/chat`, { method: "DELETE" }),
```

- [ ] **Step 2: `frontend/src/components/ChatPanel.tsx`**

```tsx
import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import { api, type ChatMessage } from "../api";
import Markdown from "./Markdown";

export default function ChatPanel({ sessionId, slug, code }: { sessionId: string; slug: string; code: string }) {
  const [messages, setMessages] = useState<ChatMessage[] | null>(null);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;
    api.chat(sessionId, slug).then(
      (h) => !cancelled && setMessages(h.messages),
      (e: Error) => !cancelled && setError(e.message),
    );
    return () => { cancelled = true; };
  }, [sessionId, slug]);

  useEffect(() => endRef.current?.scrollIntoView({ block: "end" }), [messages, busy]);

  const send = async () => {
    const text = draft.trim();
    if (!text || busy) return;
    setBusy(true);
    setError(null);
    setDraft("");
    setMessages((m) => [...(m ?? []), { role: "user", content: text }]);
    try {
      const { message } = await api.sendChat(sessionId, slug, text, code);
      setMessages((m) => [...(m ?? []), message]);
    } catch (e) {
      setMessages((m) => (m ?? []).slice(0, -1));
      setDraft(text);
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void send();
    }
  };

  const clear = async () => {
    await api.clearChat(sessionId, slug);
    setMessages([]);
  };

  return (
    <div className="chat">
      {messages === null && !error && <p className="muted">Loading chat…</p>}
      {messages?.length === 0 && (
        <p className="muted">
          Talk the problem through: ask for a hint, another example, edge cases, or feedback on your code.
          Your current code is shared with every message.
        </p>
      )}
      {messages?.map((m, i) => (
        <div key={i} className={`chat-msg ${m.role}`}>
          {m.role === "assistant" ? <Markdown>{m.content}</Markdown> : m.content}
        </div>
      ))}
      {busy && <p className="muted">Thinking…</p>}
      {error && <div className="notice fail">{error}</div>}
      <div ref={endRef} />
      <div className="chat-compose">
        <textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Ask your colleague… (Enter to send, Shift+Enter for a new line)"
          aria-label="Message"
          disabled={busy}
        />
        <div className="chat-actions">
          <button className="btn primary" onClick={() => void send()} disabled={busy || !draft.trim()}>Send</button>
          <div className="grow" />
          {!!messages?.length && <button className="linkish" onClick={() => void clear()} disabled={busy}>Clear chat</button>}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Wire the tab into `WorkspacePage.tsx`**

- Add the import: `import ChatPanel from "../components/ChatPanel";`
- Line 33: `useState<"description" | "submissions" | "chat">("description")`
- After the Submissions tab button, add:
```tsx
          <button className={leftTab === "chat" ? "on" : ""} onClick={() => setLeftTab("chat")}>Chat</button>
```
- Replace the `) : (` … `<SubmissionsList …/>` … `)}` branch of the left panel with:
```tsx
          ) : leftTab === "submissions" ? (
            <SubmissionsList subs={submissions} onLoad={(c) => setCode(c)} />
          ) : (
            <ChatPanel key={slug} sessionId={sessionId} slug={slug} code={code} />
          )}
```

- [ ] **Step 4: Styles** (append to `styles.css`)

```css
/* ---------------------------------------------------------------- chat */
.chat { display: flex; flex-direction: column; gap: 10px; min-height: 100%; }
.chat-msg { padding: 10px 12px; border-radius: var(--radius); border: 1px solid var(--line); }
.chat-msg.user { align-self: flex-end; max-width: 85%; background: var(--panel-2); white-space: pre-wrap; }
.chat-msg.assistant { background: var(--panel); }
.chat-compose { position: sticky; bottom: 0; margin-top: auto; display: flex; flex-direction: column; gap: 6px; padding-top: 8px; background: var(--panel); }
.chat-compose textarea { width: 100%; min-height: 64px; resize: vertical; font: inherit; padding: 8px 10px; border: 1px solid var(--line); border-radius: 6px; background: var(--panel); color: var(--ink); }
.chat-actions { display: flex; align-items: center; gap: 8px; }
```

- [ ] **Step 5: Build**

Run: `cd frontend && npm run build` → PASS.

- [ ] **Step 6: Commit**

```bash
git add frontend/src
git commit -m "feat: chat tab in the coding workspace"
```

---

### Task 6: End-to-end verification and docs

**Files:**
- Modify: `README.md` (Quick start + Data model + Commands table), `docs/superpowers/specs/2026-09-25-typed-api-and-chat-design.md` (Status line)

- [ ] **Step 1: Run the full stack without a key**

Leave `ANTHROPIC_API_KEY` empty in `.env`, then run `make up`, open Two Sum, go to Chat and send "hint?". Expected: the red notice "Chat is not configured: set ANTHROPIC_API_KEY in .env", with the message restored to the input. Run and Submit still work.

- [ ] **Step 2: Run with a key**

Set `ANTHROPIC_API_KEY` in `.env`, then `docker compose up -d --build api`. In the Two Sum chat:
1. "I'm thinking nested loops, is that ok?" → it should discuss O(n²) and nudge toward a faster idea without writing code.
2. "Can you give me another example?" → a concrete input with the correct output.
3. Type a buggy solution in the editor, then ask "what's wrong with my code?" → it should point to the specific line.
4. Reload the page → the history is still there. Click Clear chat → empty. Delete the session → the `chats` docs for it are gone (`docker compose exec mongo mongosh kodetrain --eval 'db.chats.countDocuments()'`).
5. Temporarily set `CHAT_MODEL=not-a-model` and restart the api → sending shows "The assistant returned an error (404)." and a reload shows no new messages stored. Revert.

- [ ] **Step 3: Final checks**

Run: `make test-api && make check-api && (cd frontend && npm run build)` → all green.

- [ ] **Step 4: Update docs**

In `README.md`:
- Quick start: after `make up`, add a line: `# optional: add ANTHROPIC_API_KEY to .env to enable the chat assistant`.
- Add rows to the Commands table: `make test-api` (backend tests, ruff, mypy), `make gen-api` (regenerate `frontend/src/api.gen.ts` after changing `backend/app/schemas.py`) and `make check-api` (fail if the generated types are stale).
- Data model: add a bullet: `` `chats`: one per `(session_id, problem)`; the chat assistant conversation ``.
- Add a short **Chat assistant** section: a Socratic colleague powered by Claude that sees the problem, the hidden reference solution and your current code, and won't write the solution unless asked. Configure it with `ANTHROPIC_API_KEY` and optionally `CHAT_MODEL`.
- Update "Deleting a session deletes its drafts, submissions and progress" to include "and chats".

In the spec, change `**Status:** Draft, awaiting review` to `**Status:** Implemented`.

- [ ] **Step 5: Commit**

```bash
git add README.md docs
git commit -m "docs: chat assistant and typed API workflow"
```
