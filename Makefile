COMPOSE := docker compose -p finance-control
TEST_DATABASE_ADMIN_URL := postgresql+psycopg://finance_control:finance_control@postgres:5432/postgres

.PHONY: up down restart status logs migrate seed backend frontend test test-integration frontend-check check sync-server sync-login-flash sync-login-itau sync-login-nubank

up:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) restart

status:
	$(COMPOSE) ps

logs:
	$(COMPOSE) logs --follow --tail=200

migrate:
	$(COMPOSE) run --build --rm backend alembic upgrade head

seed:
	$(COMPOSE) run --build --rm backend python seed.py

backend:
	$(COMPOSE) up --build backend

frontend:
	$(COMPOSE) up --build frontend

test:
	$(COMPOSE) run --build --rm -e PYTHONPATH=/app -e TEST_DATABASE_ADMIN_URL=$(TEST_DATABASE_ADMIN_URL) backend pytest -q

test-integration:
	$(COMPOSE) run --build --rm -e PYTHONPATH=/app -e TEST_DATABASE_ADMIN_URL=$(TEST_DATABASE_ADMIN_URL) backend pytest -q -m integration

frontend-check:
	docker run --rm -v "$(CURDIR)/frontend:/app" -v /app/node_modules -v /app/.next -w /app node:20-alpine sh -c "npm ci && npm run lint && npm run typecheck && npm run build"

check: test frontend-check

scrapers/.venv:
	python3 -m venv scrapers/.venv
	scrapers/.venv/bin/python -m pip install -q -r scrapers/requirements.txt

sync-server: scrapers/.venv
	cd scrapers && .venv/bin/uvicorn sync_server:app --host 0.0.0.0 --port 8001 --reload

sync-login-flash: scrapers/.venv
	cd scrapers && .venv/bin/python flash_scraper.py --login

sync-login-itau: scrapers/.venv
	cd scrapers && .venv/bin/python itau_scraper.py --login

sync-login-nubank: scrapers/.venv
	cd scrapers && .venv/bin/python nubank_scraper.py --login
