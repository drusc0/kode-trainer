# KodeTrain

A self-hosted, LeetCode-style practice app for Python coding interviews.

- **53 problems** commonly reported in Google and Meta interviews (7 Easy, 41 Medium, 5 Hard) across 15 patterns: arrays and hashing, two pointers, sliding window, prefix sums, stacks, binary search, linked lists, trees, heaps, graphs, backtracking, dynamic programming, intervals and greedy, design, and tries.
- **Pattern guides**: how to recognise each pattern, a Python template, complexity and common pitfalls, plus a step-by-step guide to approaching any interview question.
- **Sessions**: each session is a clean slate with its own drafts, submissions and progress. You might keep one for Google and another for Meta.
- **Isolated Python runner**: submissions run in a locked-down sandbox service, never in the API process.

```
browser ──► web (nginx + React) ──► api (FastAPI) ──► mongo
                                        │
                                        └──► runner (sandbox)   ← internal network only, no internet
```

## Quick start

Requirements: Docker with Compose v2.

```bash
make up                  # creates .env with a random RUNNER_TOKEN, builds and starts everything
open http://localhost:8080
```

To enable the chat assistant, add your Anthropic key to `.env` (`ANTHROPIC_API_KEY=...`) and run `make up` again.

On first start the API **seeds** the problems: it runs each reference solution in the sandbox to compute expected outputs for the hidden tests, which takes about 10–20 seconds. `GET /api/health` shows progress. Seeding only reruns for problems whose definition changed.

Other commands:

| Command | What it does |
|---|---|
| `make logs` | Follow API and runner logs |
| `make lint` / `make format` | ruff + mypy for the API, Biome + `tsc` for the web app ([backend/TOOLING.md](backend/TOOLING.md), [frontend/TOOLING.md](frontend/TOOLING.md)) |
| `make test` | pytest and Vitest unit tests, no Docker needed |
| `make test-sandbox` | Validate all 53 problems **and** a set of hostile submissions inside the real runner container |
| `make dev-web` | Vite dev server on :5173 with hot reload, proxying `/api` to the dockerized API on :8000 |
| `make down` | Stop everything (Mongo data persists in the `mongo-data` volume) |
| `make gen-api` | Regenerate `frontend/src/api.gen.ts` after changing `backend/app/schemas.py` |
| `make check-api` | Fail if the committed `api.gen.ts` is out of date |

### Chat assistant

The workspace has a **Chat** tab: a colleague powered by Claude that you can talk the problem through with. It sees the problem, every example, the hints, the hidden reference solution and your current code. It asks what you've tried, gives hints in steps and points at the line in your code that's wrong, but won't write the solution unless you ask for it. Conversations are saved per session and problem.

It needs `ANTHROPIC_API_KEY` in `.env`. `CHAT_MODEL` picks the model (default `claude-sonnet-5`). Without a key everything else works and the tab explains how to turn it on.

### API types

`backend/app/schemas.py` is the single source of truth for request and response shapes. FastAPI publishes them as OpenAPI, and `make gen-api` turns that into TypeScript for the frontend, so `frontend/src/api.ts` only aliases the generated types.

## Architecture

| Part | Stack | Notes |
|---|---|---|
| `frontend/` | React 18 + TypeScript + Vite, Monaco editor (bundled locally, Python only), react-router | Served by nginx, which also proxies `/api` |
| `backend/` | FastAPI + Motor (async MongoDB) | Problem catalog, sessions, drafts, submissions, progress, judging |
| `runner/` | Python 3.12 standard library + libseccomp (via ctypes) | Runs untrusted code; knows nothing about the database |
| `mongo` | MongoDB 7 | `sessions`, `drafts`, `submissions`, `progress`, `problem_tests` |

### Data model

- `sessions`: `{name, target: google|meta|general, notes, created_at, last_active_at}`
- `drafts`: one per `(session_id, problem)`; autosaved while you type
- `submissions`: code, verdict, passed/total, runtime and the first failing case, for every Submit
- `progress`: one per `(session_id, problem)`: attempts, solved, first solve time, best runtime
- `problem_tests`: hidden tests and expected outputs, keyed by problem with a fingerprint
- `chats`: one per `(session_id, problem)`; the chat assistant conversation

Deleting a session deletes its drafts, submissions, progress and chats.

### Judging

- **Run** executes your code on the test cases you edit in the UI. The expected output comes from running the reference solution on the same input.
- **Submit** runs every hidden test (examples first, then generated edge cases and large inputs) and stops at the first failure.
- Verdicts: Accepted, Wrong Answer, Time Limit Exceeded, Memory Limit Exceeded, Runtime Error, Compile Error.
- Where several answers are valid (Two Sum, Find Peak Element, Minimum Window Substring, Longest Palindromic Substring, Minimum Remove to Make Valid Parentheses, "any order" outputs), a problem-specific checker accepts any correct answer.
- `ListNode` and `TreeNode` arguments use LeetCode's array format. Design problems (LRU Cache, TimeMap, Trie) use the operations/arguments format.

## Security model

User code is untrusted. The defences are layered so that no single failure exposes the host:

1. **Separate service on an isolated network.** The runner only joins an `internal: true` Docker network shared with the API. It has no internet access and no route to MongoDB.
2. **Hardened container.** Read-only root filesystem, a small `/tmp` tmpfs, all Linux capabilities dropped except `SETUID`/`SETGID`/`KILL` (needed to drop privileges and clean up), `no-new-privileges`, a PID limit, memory and CPU limits, and an init process to reap orphans.
3. **Per-job process isolation.** Each job runs in a fresh process under a **dedicated unprivileged uid per slot**, in its own session and process group. It gets a clean environment (`PATH`, `LANG`, `HOME` only — secrets aren't visible), `python -I` isolated mode, and a working directory it can't write to.
4. **Resource limits (rlimits).** Address space 512 MB, CPU time, 1 MB max file size, 64 open files, 16 processes (stops fork bombs), no core dumps.
5. **seccomp filter** installed by the harness before any user code runs. `socket`, `connect`, `execve`, `ptrace`, `mount`, `unshare`, `bpf`, `io_uring`, `setrlimit` and similar calls fail with `EPERM`.
6. **Timeouts and cleanup.** A per-test time limit (SIGALRM), a wall-clock limit for the whole job, an output size cap, then `killpg` plus a sweep that kills every remaining process owned by the job's uid and deletes any files it left in `/tmp` or `/dev/shm`.
7. **Authenticated runner API.** Requests need the shared `RUNNER_TOKEN`.
8. **Host allowlist on the API.** It only answers to the hostnames in `ALLOWED_HOSTS` (default `localhost,127.0.0.1`), so a web page can't use DNS rebinding to reach your local instance.

`make test-sandbox` checks this with hostile submissions: network access, subprocess/exec, infinite loops, memory bombs, fork bombs, writes to the code directory, and reading environment secrets.

**Known limits.**
- The harness and your code share one Python process. A determined user could tamper with *their own* results, which only affects their own practice.
- The container shares the host kernel. For stronger isolation on Linux, install [gVisor](https://gvisor.dev) and uncomment `runtime: runsc` in `docker-compose.yml`. This is recommended before exposing KodeTrain beyond your own machine.
- There's no authentication yet. The ports bind to `127.0.0.1` only. Add auth before hosting it for other people.

## Adding a problem

Problems live in `backend/app/catalog/problems_*.py` as `Problem(...)` entries:

```python
Problem(
    slug="my-problem", title="My Problem", difficulty="Medium", pattern="two-pointers",
    topics=["Array"], companies=["google"],
    statement="Markdown statement…",
    entry="methodName", params=[("nums", "List[int]")], returns="int",
    examples=[{"args": [[1, 2, 3]], "note": "optional"}],
    constraints=["1 ≤ len(nums) ≤ 10⁵"], hints=["…"],
    reference="""
class Solution:
    def methodName(self, nums):
        ...
""",
    gen=lambda r: [[ints(r, 50, -10, 10)] for _ in range(20)],   # deterministic hidden tests
    compare="exact",   # or sorted / nested_sorted / float / a custom checker in runner/harness.py
)
```

Then run `make test-sandbox` and restart the API. The fingerprint change triggers reseeding for that problem only.

## Local development without Docker

```bash
# runner (Linux only, needs root to switch uids; or RUNNER_DROP_PRIVILEGES=0 RUNNER_REQUIRE_SECCOMP=0 for a quick, unsafe run)
cd runner && RUNNER_TOKEN=dev python3 server.py
# api
cd backend && RUNNER_TOKEN=dev RUNNER_URL=http://localhost:8080 uv run uvicorn app.main:app --reload
# web
cd frontend && corepack pnpm install && corepack pnpm dev
```

Local tooling needs [uv](https://docs.astral.sh/uv/) and Node 24 (which ships `corepack`, so pnpm needs no separate install).

Note that the unsafe runner flags remove the sandbox's main protections. Use them only with your own code.
