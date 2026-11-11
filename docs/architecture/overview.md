# Architecture Overview — MediClaim AI

- Date: 2026-11-11
- Mode stage: software-dev Stage 3 (Architecture)
- Status: proposed for user approval (R08)
- Related ADRs: ADR-01..ADR-10

## 1. Purpose and scope

MediClaim AI is a web SaaS that ingests Indian health-insurance claim bundles (PDF/images), extracts structured fields via OCR + LLM, computes a fraud risk score with explainable flags, and recommends an adjudication decision, with an immutable audit trail. MVP is a single-tenant demo on synthetic data only (no real patient data). This document describes the system architecture for the MVP build; live insurer integration, multi-tenancy, and production hardening are deferred (see product-brief out-of-scope).

## 2. High-level component diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  Browser (Claims Officer / Manager / Admin)                                   │
│  Next.js 15 (App Router) + React + TS + Tailwind + shadcn/ui                 │
└──────────────────────────────┬───────────────────────────────────────────────┘
                               │ HTTPS (JSON + multipart)
                               ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  Vercel (frontend)  ────  Render Web Service (FastAPI, ASGI/uvicorn)          │
│  /app/* routes        │   /api/v1/*                                         │
│                       │                                                     │
│                       ├─► Auth module (JWT issue/verify, RBAC)               │
│                       ├─► Claims module (CRUD, upload orchestration)         │
│                       ├─► Extraction module (OCR + LLM, async job)           │
│                       ├─► Fraud module (rules + stats, scoring)              │
│                       ├─► Adjudication module (decision + reasons)           │
│                       ├─► Audit module (append-only hash chain)             │
│                       ├─► Reporting module (aggregates, KPIs)               │
│                       └─► Admin module (users, usage)                        │
│                               │                                             │
│                               ├─► PostgreSQL 16 (Render managed)            │
│                               ├─► Object storage (local disk / Render volume │
│                               │    for uploaded files; S3-compatible later)  │
│                               ├─► OpenAI API (GPT-4o-mini, abstracted)       │
│                               └─► OCR engines (PaddleOCR primary, Tesseract  │
│                                    fallback) in-process process pool         │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 3. Components

| Component | Responsibility | Owner module | Tech |
|---|---|---|---|
| Web UI | Dashboards, upload, review/edit, flags, adjudication, audit export | frontend (Next.js) | Next.js 15 App Router |
| API Gateway | Routing, auth, validation, rate limiting, CORS | `app/main.py` | FastAPI |
| Auth | Login, JWT issue/refresh, RBAC, password hashing | `app/auth/` | python-jose, passlib[bcrypt] |
| Claims | Claim lifecycle, bundle/file records, status | `app/claims/` | SQLAlchemy 2 async |
| Ingestion | Multipart upload, file validation, storage, job enqueue | `app/ingestion/` | FastAPI UploadFile |
| Extraction | OCR (PaddleOCR/Tesseract), LLM structured extraction, normalization | `app/extraction/` | paddleocr, pytesseract, OpenAI SDK |
| Fraud | Rule-based RFIs, statistical anomaly, risk score | `app/fraud/` | pure Python + numpy/pandas |
| Adjudication | Decision recommendation + reasons from score/flags | `app/adjudication/` | pure Python |
| Audit | Append-only events with hash chain | `app/audit/` | SQLAlchemy |
| Reporting | Aggregates by provider/window, KPIs | `app/reporting/` | SQL aggregates |
| Admin | User CRUD, usage | `app/admin/` | FastAPI |
| DB | Persistence | Postgres 16 | managed |
| File store | Uploaded bytes | Render disk/volume (MVP) | local FS; S3-compatible adapter later |
| Job runner | Async processing of claim bundles | in-process (asyncio + ProcessPoolExecutor) | Python stdlib |
| LLM provider | Structured extraction | OpenAI (abstracted) | GPT-4o-mini |

## 4. Data flow — claim lifecycle (happy path)

1. **Upload** (sync, ≤3s): Officer selects bundle → frontend POSTs multipart to `POST /api/v1/claims` → API validates auth, file type/size/count → creates `claim` (status `queued`) + `claim_file` rows → stores bytes → enqueues background job → returns `claim_id` + `202 Accepted`.
2. **OCR** (async, process pool): worker picks job → status `processing` → runs PaddleOCR (fallback Tesseract) per file → stores `ocr_result` (text + confidence + engine) → updates file status `done/failed`.
3. **Extraction** (async, LLM): OCR text → `Extractor` interface → GPT-4o-mini JSON mode → validates against Pydantic schema → stores `extraction` (structured fields) + `extraction_field` (per-field value, confidence, human-corrected flag). Missing fields → `null` (never hallucinated; AC-3).
4. **Fraud scoring** (sync-ish, CPU light): rules + stats compute flags + risk score (0–100) + confidence band → stores `fraud_flag` rows + `risk_score`.
5. **Adjudication** (sync): decision engine maps score/flags → `approve/reject/partial` + amount + ≥1 reason citing evidence → stores `adjudication`.
6. **Review** (sync): Officer views claim detail → can edit fields (FR-4) → edits persisted with `human_corrected=true` + audit entry; override recommendation requires reason (FR-9).
7. **Audit** (every step): each state transition appends an `audit_event` row with actor, action, timestamp, payload hash, prev-hash (chain).
8. **Reporting**: manager queries aggregates (SQL) → dashboard KPIs.

End-to-end target ≤30s for 5-page bundle (NFR-1).

## 5. Sync vs async boundaries

- **Synchronous (request/response, ≤3s):** auth (login/refresh), claim create (metadata + enqueue), claim read, field edit, override, audit export, reporting aggregates, admin CRUD.
- **Asynchronous (background job, polled via status):** OCR, LLM extraction, fraud scoring (may be folded into extraction job), adjudication. Frontend polls `GET /claims/{id}` (status field) or SSE stream (optional P1) every 1–2s; job status transitions `queued → processing → done/failed` per file (AC-2).
- **Rationale:** OCR/LLM are CPU/IO heavy and exceed HTTP timeouts; Render web service stays responsive; retries isolated (NFR-11).

Job runner choice: in-process `asyncio` + `ProcessPoolExecutor` for MVP (no extra infra). Exit criteria to move to Celery+Redis: if concurrency > 50 claims or need horizontal scale (NFR-3). Documented as reversible (see ADR-06/01).

## 6. External services

| Service | Purpose | Failure mode | Degradation |
|---|---|---|---|
| OpenAI API (GPT-4o-mini) | Structured extraction | timeout/5xx/rate limit | retry 3x exponential; if exhausted → claim status `failed_extraction`, notify; queue for retry (NFR-12) |
| PaddleOCR (self-hosted) | Primary OCR | import/runtime error | fallback to Tesseract; if both fail → file status `failed` with reason |
| Tesseract (self-hosted) | Fallback OCR | binary missing | mark unavailable; surface in health check |
| PostgreSQL | Persistence | connection loss | pool retry; 503 on health; no data loss |
| Render disk | File storage | full/unavailable | 507; alert |
| Vercel | Frontend hosting | outage | static cached? N/A; status page |

No other external services in MVP (no payments, no insurer APIs).

## 7. Multi-tenant posture (single-tenant demo, H-3)

- MVP is **single-tenant**: one demo tenant (`tenant_id` reserved). All users belong to the single demo tenant.
- **Enforced scoping (H-3):** a FastAPI dependency `TenantScope` extracts `tenant_id` from the JWT and stores it in `request.state.tenant_id`; a base repository/query helper applies `WHERE tenant_id = :tenant_id` to every read/write. No endpoint may accept `tenant_id` from the request body. Cross-tenant access returns 404 (not 403) to avoid enumeration (M-19).
- RLS is deferred but the migration path is documented (ADR-09); app-level scoping is the MVP control. Tests include cross-tenant isolation cases.
- Assumption: demo users are seeded; no self-signup in MVP (admin creates users).

## 8. Security & compliance posture

- DPDP-aligned (synthetic demo data): no real PII; consent/purpose/retention documented in `docs/compliance/dpdp-posture.md` (authored Stage 3). Data retention: synthetic demo data purged on reset; audit log retained.
- LLM extraction hardening: prompt-injection defenses, schema validation, evidence quoting, input caps, real-data guard — see `docs/architecture/extraction-contract.md` (C-1, H-2, H-11).
- Security headers (CSP etc.) specified in auth-design §7.1.
- IRDAI Fraud Monitoring Framework alignment: rules map to Red Flag Indicators; audit log supports Fraud Monitoring Unit evidence (RFI). See fraud module rule catalog.
- NHCX/FHIR: extraction schema mirrors FHIR Claim/ExplanationOfBenefit fields where practical (patient, provider, coverage, item, diagnosis, total) for credibility; documented as "mirroring", not certified integration.
- Secrets in env vars only; no hardcoded secrets (R08). Security audit before commit.

## 9. Observability

- Structured JSON logs (request id, user id, claim id) via Python `logging` + uvicorn access log.
- Health endpoints: `/healthz` (liveness), `/readyz` (DB + OCR + LLM reachability).
- Error tracking: Sentry (optional, free tier) — gated behind `SENTRY_DSN` env; not required for demo.
- Metrics: basic request counts/latency via FastAPI middleware; Prometheus endpoint optional (P2).
- Audit log is the source of truth for "what happened"; logs are operational.

## 10. Testability hooks

- Every module exposes pure functions for core logic (scoring, decision, hash chain) → unit testable without DB.
- Repositories behind interfaces → integration tests against test Postgres (docker) or sqlite for speed (with caveats).
- Coverage target 80% on critical paths: extraction normalization, fraud rules/scoring, adjudication, audit hash chain, auth (NFR-15).

## 11. Directory layout (backend, planned Stage 5)

```
backend/
  app/
    main.py              # FastAPI app, routers, middleware
    config.py            # pydantic-settings env
    db.py                # async engine/session
    models/              # SQLAlchemy models (one file per aggregate)
    schemas/             # Pydantic request/response
    auth/                # jwt, passwords, rbac, deps
    claims/              # router + service + repo
    ingestion/           # upload, storage, jobs
    extraction/          # ocr/, llm/, normalizer, extractor interface
    fraud/               # rules/, stats/, scorer
    adjudication/        # decision engine
    audit/               # append-only writer + verifier
    reporting/           # aggregates
    admin/               # users
    common/              # errors, pagination, ids
  alembic/               # migrations
  tests/                 # pytest
  Dockerfile
frontend/
  (Next.js app)
```

Label: this layout is a plan; actual creation happens in Stage 5 (TDD). No code written in Stage 3.
