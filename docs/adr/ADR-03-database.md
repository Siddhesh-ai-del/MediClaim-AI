# ADR-03 — Database

- Status: accepted
- Date: 2026-11-11
- Mode stage: Stage 2/3

## Context
Claims, extracted fields, flags, decisions, audit log, users, provider aggregates.

## Problem
Which database?

## Considered alternatives
1. **PostgreSQL** (Render/Neon) — relational fits claims/audit; JSONB for flexible extracted fields; pgvector optional for similarity; mature.
2. **MongoDB** — flexible schema, but weaker for audit/relational aggregates and ACID audit log.
3. **SQLite** — zero ops for demo, but not credible for multi-user production narrative; migration later.

## Decision
PostgreSQL 16 (managed, Render or Neon free tier). Use SQLAlchemy 2 async + Alembic. Audit log as append-only table with hash chain (tamper-evident).

## Consequences
- Need managed Postgres (~$6-7/mo) — acceptable.
- Schema migrations disciplined (Alembic) from Foundation milestone.