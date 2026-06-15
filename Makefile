.PHONY: up down migrate seed backend frontend test

up:
	docker compose up --build

down:
	docker compose down

migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python seed.py

backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

test:
	PYTHONPATH=backend .venv/bin/python -m pytest -s backend/tests -q
