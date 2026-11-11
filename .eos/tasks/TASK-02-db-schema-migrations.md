---
id: TASK-02
title: DB schema and migrations
assignee: eos-backend-engineer
parallel: no
dependencies: [TASK-01]
---
# TASK-02 — DB schema and migrations

## Description
Implement PostgreSQL schema per docs/architecture/database-schema.md (all tables, enums, indexes, materialized view, append-only triggers) via SQLAlchemy models + Alembic migration. Seed tenant + admin via bootstrap.

## Requirements
- Models mirror DDL; async engine; Alembic `upgrade head` on startup.
- Include user_account failed_login_count/locked_until, claim submitted_by/assigned_to.
- Append-only trigger on audit_event; app role INSERT only.
- Seed script (idempotent) for demo tenant.

## Expected output
- backend/app/models/*.py, backend/alembic/versions/0001_initial.py
- backend/app/db.py, backend/app/seed.py

## Acceptance criteria
- [ ] `alembic upgrade head` applies cleanly on fresh Postgres.
- [ ] `alembic downgrade base` then upgrade works (reversible).
- [ ] All tables/indexes present (query pg_catalog).
- [ ] Append-only trigger rejects UPDATE on audit_event.

## Verification method
`docker compose up -d db && cd backend && alembic upgrade head && alembic downgrade base && alembic upgrade head`; pytest integration test checks tables.

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending