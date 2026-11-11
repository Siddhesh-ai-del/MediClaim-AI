# ADR-09 — Data model

- Status: accepted
- Date: 2026-11-11
- Mode stage: Stage 3

## Context
Claims, extracted fields, flags, decisions, audit log, users, provider aggregates. Need auditability, explainability, and a credible path to NHCX/FHIR integration.

## Problem
Relational vs document vs hybrid; multi-tenancy now or later; audit log tamper-evidence?

## Considered alternatives
1. **PostgreSQL relational core + JSONB for flexible payloads (chosen)** — ACID audit log, strong aggregates, JSONB for evolving extraction schema, pgvector optional. Con: schema migrations discipline.
2. **MongoDB document store** — flexible extraction schema, but weaker for audit/relational aggregates and ACID audit log; harder tamper-evidence.
3. **SQLite** — zero ops for demo, but not credible for multi-user production narrative; migration later.

## Decision
PostgreSQL 16 relational core with JSONB for extracted fields/reasons/evidence; `tenant_id` reserved for forward compat but no RLS in MVP (single-tenant demo); audit_event append-only with hash chain (SHA-256 + prev_hash). See database-schema.md. Provider aggregates via materialized view.

## Consequences
- Need managed Postgres (~$6-7/mo) — acceptable.
- Alembic migrations from Foundation milestone.
- Multi-tenant enforcement (RLS + middleware) documented as future migration, not implemented.
- NHCX/FHIR mirroring at field level for credibility (not certified integration).
