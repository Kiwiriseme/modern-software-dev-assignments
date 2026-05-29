# Week 4 Project Guidance

## How to run
- Start app: `make run` (from week4/ directory)
- Run tests: `make test`
- Format: `make format`
- Lint: `make lint`

## Project structure
- `backend/app/main.py` — FastAPI entry point
- `backend/app/routers/` — API route definitions (notes, action_items)
- `backend/app/services/` — Business logic (extract)
- `backend/app/models.py` — SQLAlchemy models (Note, ActionItem)
- `backend/app/schemas.py` — Pydantic request/response schemas
- `backend/app/db.py` — Database engine, session, seeding
- `backend/tests/` — pytest test files
- `frontend/` — Static HTML/JS/CSS
- `data/seed.sql` — Initial seed data

## Code style
- Python: black for formatting, ruff for linting
- Use clear, descriptive variable names
- Type annotations on function signatures

## Workflow rules
- When adding a new endpoint: first write a failing test, then implement, then verify tests pass
- After any code change, run `make format` and `make lint`
- Prefer running single test files with `pytest -q backend/tests/<file>.py` instead of the full suite
- Use `pre-commit install` to enable automatic checks before each commit
