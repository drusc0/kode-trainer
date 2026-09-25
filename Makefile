.PHONY: up down logs dev-api dev-web test-sandbox

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
