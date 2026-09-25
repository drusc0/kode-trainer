.PHONY: up down logs dev-web lint format test test-sandbox

PNPM := corepack pnpm

up:            ## build and start everything at http://localhost:8080
	@test -f .env || (cp .env.example .env && sed -i.bak "s/change-me/$$(openssl rand -hex 32)/" .env && rm -f .env.bak)
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f api runner

dev-web:       ## hot-reload frontend on :5173 against the dockerized API
	cd frontend && $(PNPM) install && $(PNPM) dev

lint:          ## ruff for all Python, mypy for the API and runner, Biome for the web app
	uv run --project backend ruff check . && uv run --project backend ruff format --check .
	cd backend && uv run mypy && uv run mypy --platform linux ../runner
	cd frontend && $(PNPM) install --frozen-lockfile && $(PNPM) lint && $(PNPM) exec tsc --noEmit

format:        ## auto-fix formatting and safe lint fixes on both sides
	uv run --project backend ruff format . && uv run --project backend ruff check --fix .
	cd frontend && $(PNPM) format

test:          ## unit tests (no Docker needed); see test-sandbox for the full runner check
	cd backend && uv run pytest
	cd frontend && $(PNPM) test

test-sandbox:  ## run every reference solution + attack cases through the real runner container
	docker compose run --rm --entrypoint python3 -v $$(pwd)/backend:/backend:ro -v $$(pwd)/scripts:/scripts:ro runner /scripts/validate_catalog.py
