# Typed API contract + problem chat assistant

- **Date:** 2026-09-25
- **Status:** Draft, awaiting review
- **Branch:** `claude/interview-prep-chat-78f70c`

## Goal

1. Give the API one source of truth for its request and response shapes, so the frontend's types are generated rather than hand-copied.
2. Add a chat assistant to the coding workspace that acts like a colleague: you can discuss the problem, ask for hints or more examples, and get feedback on your current code.

These ship as two atomic commits: a behavior-neutral `refactor:` first, then a `feat:` built on top of it.

## Decisions

| Question | Decision | Why |
|---|---|---|
| gRPC vs Pydantic | **Pydantic + OpenAPI → generated TypeScript** | Browsers can't call gRPC without gRPC-Web and a proxy container. FastAPI already emits OpenAPI from Pydantic models, so the only missing piece is typing the responses. |
| Shared "library" | **A generated `frontend/src/api.gen.ts`, committed** | One producer and one consumer, so a published package would be ceremony. A staleness check catches drift. |
| LangGraph vs Anthropic SDK | **Plain Anthropic SDK** | A chat about one problem is a single Messages API call with history. LangGraph only earns its place with multi-step flows (for example a phased mock interview, or tool calls that run code). Revisit then. |
| Examples in the description | **Keep all examples** | User choice. Chat is purely additive. |
| Chat history | **Persisted per session + problem in Mongo** | Same lifecycle as drafts. Deleted along with its session. |
| Bot persona | **Socratic colleague** | Nudges with questions and graduated hints. Never writes solution code unless explicitly asked. |
| Streaming | **Not in v1** | Replies arrive whole after about 3–8 s. This is the first thing to add if the wait bothers you. |

## Part 1: Typed API contract (`refactor:`)

### Backend

- New `backend/app/schemas.py` holds every request and response model. `SessionIn`, `SessionPatch`, `CodeIn` and `RunIn` move here from `main.py`. New models:
  - `Session`, `ProblemSummary`, `ProblemList {patterns, problems}`, `Example`, `EditorField` (not `Field`, which would shadow Pydantic's), `ProblemDetail`
  - `CaseResult`, `RunResult`, `FailingCase` (a `CaseResult` plus `index` and `is_example`), `SubmitResult`
  - `Submission`, `Bucket`, `DifficultyBuckets {Easy, Medium, Hard}` (explicit fields, so `stats.by_difficulty.Easy` stays typed), `RecentSubmission`, `SessionStats`
- Every JSON route declares `response_model=`. Helpers and `judge.py` may keep building dicts; FastAPI validates them against the model and serializes them. This keeps the diff small and still checks every response.
- Field names, optionality and HTTP behavior stay exactly as they are today. The TypeScript interfaces in `api.ts` are the reference for what the frontend already relies on.

### Codegen

- `openapi-typescript` is added as a frontend **dev** dependency.
- `make gen-api` does two things:
  1. Dumps `app.openapi()` by importing the app under `uv run --python 3.12 --with-requirements` (the same env the tests use). It needs no Docker, Mongo or runner.
  2. Runs `npx openapi-typescript` to write `frontend/src/api.gen.ts`.
- `make check-api` runs `gen-api`, then `git diff --exit-code` on the generated file. A non-zero exit means the committed copy is stale.
- In `frontend/src/api.ts`, the hand-written interfaces become aliases such as `export type ProblemDetail = components["schemas"]["ProblemDetail"]`. Page components keep their imports unchanged. The `req` helper, the `api` object, `timeAgo` and `TARGET_LABEL` stay as they are.

### Tests

- Add `backend/requirements-dev.txt` with pytest, ruff and mypy. Keep the repo's existing pip/requirements convention.
- `backend/tests/test_openapi.py` asserts that every `2xx` JSON response in `app.openapi()` references a schema. A future route that returns an untyped dict fails this test.
- `npm run build` (which runs `tsc --noEmit`) must pass against the generated types.
- Smoke check: `make up`, then open a problem, then run, submit, view submissions and view stats.
- ruff and mypy (strict) run on the **new** files only (`schemas.py`, `chat.py`, tests). The existing modules predate those tools, and retrofitting them is out of scope.

## Part 2: Chat assistant (`feat:`)

### Config

- `.env.example`, `docker-compose.yml` (api service) and `Settings` gain two variables:
  - `ANTHROPIC_API_KEY` (optional; the app still starts without it)
  - `CHAT_MODEL`, defaulting to `claude-sonnet-5`
- `anthropic` is added to `backend/requirements.txt`.

### Data

- A new `chats` collection holds `{session_id, problem, messages: [{role, content}], updated_at}`. It has a unique index on `(session_id, problem)`.
- `DELETE /api/sessions/{id}` also clears that session's chats.

### API

All routes live under `/api/sessions/{session_id}/problems/{slug}/chat`:

| Method | Body | Response | Notes |
|---|---|---|---|
| GET | — | `ChatHistory {messages: ChatMessage[]}` | Empty list if there's no chat yet |
| POST | `ChatIn {message (1–4000 chars), code (≤ max_code_bytes)}` | `ChatReply {message: ChatMessage}` | Appends the user turn and the assistant turn |
| DELETE | — | 204 | Clears the conversation |

`ChatMessage` is `{role: "user" | "assistant", content: str}`.

Error handling:
- No API key → 503 "Chat is not configured: set ANTHROPIC_API_KEY in .env".
- Anthropic API error → 502 with a short message. Nothing is persisted, so a failed turn leaves the history untouched.
- History sent to the model is capped at the last 40 messages. `ponytail:` a naive cap; switch to summarization if long chats start to matter.

### `backend/app/chat.py`

- `build_system_prompt(problem, examples) -> str` builds the prompt from:
  - the persona rules
  - the problem's title, statement, **all** examples with their expected outputs, constraints and hints
  - the **reference solution**, marked hidden: use it to judge the user's reasoning, never reveal it
- `user_turn(message, code) -> str` attaches the current editor code to the outgoing user turn only. This keeps the system prompt stable per problem, so prompt caching works. Stored history keeps just the typed message.
- `async reply(client, model, system, history, turn) -> str` makes a single `messages.create` call with top-level auto-caching. The client is passed in so tests can fake it. SDK errors and `refusal` stops become `ChatError`.
- The route in `main.py` is thin glue: it loads the history, calls `reply`, persists the result and returns it.

Persona rules in the prompt:
- Act as a friendly senior engineer pairing with the user on an interview problem.
- Start from the user's thinking: ask what they've tried before offering hints.
- Hints are graduated: a nudge first, then more specific help, then the approach.
- Share extra examples or edge cases when asked.
- Give feedback on the user's code when they ask, pointing at the specific line or idea.
- Never write the full solution code unless the user explicitly asks for it.
- Keep replies short and conversational, in Markdown.

### Frontend

- `WorkspacePage` gets a third left-panel tab, **Chat**, alongside Description and Submissions. The tab contains:
  - the message list, rendered with the existing `Markdown` component
  - a textarea (Enter sends, Shift+Enter adds a new line)
  - a "thinking…" indicator and a Clear button
  - errors, shown with the existing `notice fail` style
- The current editor `code` is sent with every message.
- `api.ts` gains `chat`, `sendChat` and `clearChat`, typed from the generated schemas.

### Tests

`backend/tests/test_chat.py`:
- The system prompt includes the statement, every example with its output, the hints and the reference solution. The user turn includes the code.
- `reply` sends the history plus the new message, in order, to a fake client and returns the fake client's text.
- The history cap keeps only the last 40 messages.

A manual end-to-end check with a real key: ask for a hint, ask for another example, and ask "what's wrong with my code?".

## Out of scope

- Streaming responses
- LangGraph and multi-step mock-interview flows
- Hiding examples or hints (an interview mode)
- Retrofitting ruff/mypy onto the existing backend modules
