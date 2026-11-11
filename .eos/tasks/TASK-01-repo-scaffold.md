---
id: TASK-01
title: Repo scaffolding and tooling
assignee: eos-backend-engineer
parallel: no
dependencies: []
---
# TASK-01 — Repo scaffolding and tooling

## Description
Create backend (FastAPI) and frontend (Next.js) skeletons, Dockerfile, .env.example, lint/typecheck/test configs, git init. Verify Python 3.14 + PaddleOCR installability (R02).

## Requirements
- Backend: FastAPI 0.141, Pydantic v2, SQLAlchemy 2 async, Alembic, pytest, ruff, mypy/pyright.
- Frontend: Next.js 15 App Router, TS, Tailwind, shadcn/ui, eslint, vitest/jest.
- Dockerfile installs tesseract + hin + paddleocr deps; non-root user; healthcheck.
- .env.example with all backend/frontend vars (placeholders only).
- Verify `import paddleocr` works on chosen Python; if not, pin Python 3.12 and document.

## Expected output
- backend/, frontend/, docker-compose.yml (dev postgres), .env.example, .gitignore (already has .eos/memory/session/)
- backend/requirements.txt (pinned), backend/pyproject.toml

## Acceptance criteria
- [ ] `cd backend && python -m pytest` runs (0 tests OK).
- [ ] `cd frontend && npm run build` succeeds.
- [ ] `docker build backend` succeeds.
- [ ] `python -c "import paddleocr"` succeeds OR documented fallback to Py 3.12.
- [ ] No secrets committed (security-audit clean).

## Verification method
`cd backend && ruff check . && mypy app && pytest -q`; `cd frontend && npm run lint && npm run build`; `docker build -t mediclaim-backend backend`.

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending