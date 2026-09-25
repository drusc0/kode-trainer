# Backend tooling

**Status:** adopted 2026-09-25 · **Scope:** `backend/` (the FastAPI service); ruff also covers `runner/` and `scripts/`

| Job | Tool | Command |
|---|---|---|
| Python, venv, dependencies, lockfile | [uv](https://docs.astral.sh/uv/) | `uv sync` · `uv add <pkg>` · `uv add --dev <pkg>` |
| Lint + import sorting | [ruff](https://docs.astral.sh/ruff/) | `uv run ruff check ..` (`--fix` to autofix) |
| Formatting | ruff | `uv run ruff format ..` |
| Type checking | [mypy](https://mypy.readthedocs.io/) `--strict` | `uv run mypy` |
| Tests | [pytest](https://docs.pytest.org/) | `uv run pytest` |

From the repo root, `make lint` and `make test` run all of these (plus the frontend's checks).

## Why these

### uv, not pip + `requirements.txt`, Poetry or pdm
- **Reproducible builds.** `requirements.txt` only held version ranges, so every Docker build could resolve different versions. `uv.lock` pins the whole dependency tree, and the Dockerfile installs it with `uv sync --frozen`.
- **One tool for Python itself, venvs, dependencies and running commands.** `.python-version` pins 3.12, matching the Docker base image and the runner's Python.
- **Speed.** Resolving and installing is 10–100× faster than pip or Poetry, which matters in Docker layers and CI.
- **Standards-based.** Dependencies live in `[project]` in `pyproject.toml` (PEP 621), with dev tools in `[dependency-groups]` (PEP 735), so nothing is locked to uv.
- Rejected alternatives:
  - **Poetry** is slower, uses its own non-standard sections, and doesn't manage Python versions.
  - **pdm** is fine technically but has much less momentum than uv.

### ruff, not flake8 + black + isort
- One Rust binary replaces three or four tools and a pile of plugins, and it checks this codebase in milliseconds.
- Enabled rule sets:
  - `E`, `F`, `W`: pycodestyle and pyflakes basics.
  - `I`: import sorting.
  - `UP`: pyupgrade, which enforces 3.12 syntax.
  - `B`: bugbear, likely bugs. For example, it caught missing `raise ... from e` in exception handlers.
  - `SIM`: simplifications.
  - `RUF`: ruff's own rules.
  - `ASYNC`: blocking calls inside async code, which matters in a FastAPI and Motor service.
- Deliberate exceptions:
  - **`E501` (line length)** is off because the formatter owns wrapping. Long problem statements inside string literals can't be wrapped without changing their content.
  - **`RUF001` (ambiguous unicode)** is off because problem statements intentionally use `×`, `≤` and `–`.
  - **`W293` in `app/catalog/*`** is off because design-problem starter code keeps indented blank lines, so the editor cursor lands inside each method.
- Line length is 120, matching the existing code's density and the frontend's Biome setting.
- The config lives in the repo-root `ruff.toml`, so one ruleset covers the API, the runner and the scripts. The dev tools are installed in the backend's venv, which is why commands run from `backend/` (or via `uv run --project backend` from the root).
- `src = ["backend", "runner"]` tells import sorting that `app` and the runner modules are first-party. `*.md` is excluded because ruff would otherwise reformat the code samples in the pattern guides.

### mypy `--strict`, not pyright or ty
- It's the house standard (see the root `CLAUDE.md`) and the reference implementation of Python typing. It also works well with the Pydantic models FastAPI relies on.
- Rejected alternatives:
  - **pyright / basedpyright** are faster and have better inference. Switching costs only config if mypy becomes a bottleneck.
  - **ty** (Astral's checker) is promising but still young. Revisit once it's stable.
- Mongo documents and runner payloads are typed as `Doc = dict[str, Any]` (in `app/core.py`). Anything stricter would mean modelling every collection, which the code doesn't need yet.

### pytest
- It's the de facto standard, and FastAPI's `TestClient` plugs straight into it.
- Current tests need neither Docker, Mongo nor the runner:
  - `tests/test_judge.py` covers verdict mapping, editor ↔ stored case conversion, output truncation, and that every problem's hidden-test generator is deterministic. Seeding depends on that, because expected outputs are stored once per fingerprint.
  - `tests/test_api.py` checks that the HTTP boundary rejects bad input (malformed ids, unknown problems, oversized code or too many cases, invalid session targets) before anything reaches the database or the sandbox.
- `make test-sandbox` is still the end-to-end check. It runs every reference solution and the hostile submissions in the real runner container.

## Consequences and follow-ups
- The first `ruff format` rewrote some problem `gen` lambdas. Their source is part of `problem_fingerprint`, so the API reseeds those problems once on its next start (about 10–20 s, automatic).
- `runner/` is type-checked with the same strict settings, as Linux (`mypy --platform linux ../runner`), because it only runs in its Linux container and uses Linux-only process and seccomp APIs. It has no third-party dependencies, so the backend's venv can check it. Untrusted user values and JSON payloads are typed as `Any`, which keeps the checks focused on the runner's own logic. The harness's star-imports live inside the `PRELUDE` string that's executed for user code, so they don't trip ruff.
- `scripts/validate_catalog.py` is linted but not type-checked. It's a small test driver that imports both the runner and the backend by path.
- In the runner, `zip()` over user-influenced lengths (argument lists, design ops) is explicitly `strict=False` to keep the existing behavior. Where lengths are already checked, it's `strict=True`. `make test-sandbox` passed after the change.
- pytest shows a Starlette deprecation warning about `httpx` in `TestClient`. It comes from the framework and needs no action until FastAPI or Starlette change their testing extra.
