# ADR-01 — Backend framework

- Status: accepted
- Date: 2026-11-11
- Mode stage: Stage 2/3

## Context
We need a backend that integrates OCR, LLM extraction, fraud rules, and a claims API, buildable by a 4-student team in 5 months.

## Problem
Which backend framework?

## Considered alternatives
1. **FastAPI (Python)** — native async, Pydantic validation, first-class for ML/OCR libs (PaddleOCR, OpenAI SDK), auto OpenAPI docs. Con: Python GIL for CPU-bound OCR (mitigated by process pool/queue).
2. **Node.js/Express (TypeScript)** — team full-stack capable, but ML/OCR ecosystem weaker; would need Python sidecar anyway.
3. **Django** — batteries included (auth, admin) but heavier; slower iteration; ORM overhead for our simple model.

## Decision
FastAPI (Python 3.14) with Pydantic v2 schemas, SQLAlchemy 2 async, Alembic migrations. OCR/LLM calls run in a background task queue (asyncio + process pool) to avoid blocking.

## Consequences
- ML/OCR integration is direct; no sidecar.
- Must implement auth ourselves (JWT) — acceptable for MVP single tenant.
- CPU-bound OCR must be offloaded; plan job queue from Foundation milestone.