.PHONY: up down logs dev-api dev-web test-sandbox test-api gen-api check-api

up:            ## build and start everything at http://localhost:8080
	@test -f .env || (cp .env.example .env && sed -i.bak "s/change-me/$$(openssl rand -hex 32)/" .env && rm -f .env.bak)
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f api runner

dev-web:       ## hot-reload frontend on :5173 against the dockerized API
	cd frontend && npm install && npm run dev

test-sandbox:  ## run every reference solution + attack cases through the real runner container
	docker compose run --rm --entrypoint python3 -v $$(pwd)/backend:/backend:ro -v $$(pwd)/scripts:/scripts:ro runner /scripts/validate_catalog.py

PY = cd backend && uv run -q --python 3.12 --with-requirements requirements.txt --with-requirements requirements-dev.txt
TYPED = app/schemas.py app/chat.py

test-api:      ## backend unit tests + ruff/mypy on the typed modules
	$(PY) pytest -q
	$(PY) ruff check $(TYPED) tests
	$(PY) ruff format --check $(TYPED) tests
	$(PY) mypy --strict --follow-imports=silent $(TYPED)

gen-api:       ## regenerate frontend/src/api.gen.ts from the FastAPI models
	$(PY) python -c "import json; from app.main import app; print(json.dumps(app.openapi()))" > ../frontend/openapi.json
	cd frontend && npx openapi-typescript openapi.json -o src/api.gen.ts && rm openapi.json

check-api:     ## fail if api.gen.ts is stale
	$(MAKE) gen-api
	git diff --exit-code frontend/src/api.gen.ts
