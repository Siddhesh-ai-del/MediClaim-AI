---
id: TASK-04
title: Config and secrets management
assignee: eos-backend-engineer
parallel: yes
dependencies: [TASK-01]
---
# TASK-04 — Config and secrets management

## Description
Implement pydantic-settings config reading all env vars from deployment.md §4; .env.example; secret validation (JWT_SECRET length, etc.).

## Requirements
- backend/app/config.py with settings; validation on startup (fail fast).
- .env.example committed; .env gitignored.

## Expected output
- backend/app/config.py, backend/.env.example

## Acceptance criteria
- [ ] App fails to start if DATABASE_URL/JWT_SECRET missing.
- [ ] All documented env vars recognized.

## Verification method
`cd backend && python -c "from app.config import settings; print(settings)"` with .env present; pytest config tests.

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending