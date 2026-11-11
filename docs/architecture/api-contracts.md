# API Contracts — MediClaim AI

- Date: 2026-11-11
- Mode stage: software-dev Stage 3
- Style: REST over HTTPS, JSON (multipart for uploads). Base path `/api/v1`. See ADR-10.
- Auth: Bearer JWT access token in `Authorization` header (see auth-design.md).
- Versioning: URL prefix `/api/v1`; breaking changes bump to `/api/v2` with deprecation window.
- Content-Type: `application/json` unless noted. Errors: RFC 7807 Problem Details (`application/problem+json`).

## 1. Conventions

### Pagination
List endpoints accept `?page=1&page_size=20` (default 20, max 100) and return:
```json
{ "items": [...], "total": 123, "page": 1, "page_size": 20, "pages": 7 }
```

### Sorting/filtering (H-6 allowlist)
- `sort`: field MUST be in allowlist {`created_at`, `processed_at`, `risk_score`, `total_claimed_amount`, `claim_number`, `status`}; direction `asc|desc` (default `desc`). Any other value → 422. Never interpolate into SQL; map to a fixed `ORDER BY` clause.
- `status`: enum {queued,processing,extracted,scored,adjudicated,failed}.
- `provider_id`, `submitted_by`, `assigned_to`: UUID validated.
- `from`,`to`: ISO date; `from <= to`.
- `search`: max 64 chars; escaped for ILIKE; no wildcards from user.
- Filter values validated (UUID/enum/date) before query; parameterized only.

### Idempotency
Mutating endpoints accept optional `Idempotency-Key` header (UUID). Duplicate key returns cached response with `X-Idempotent-Replayed: true`.

### Timestamps
ISO-8601 UTC (`2026-11-11T10:00:00Z`).

### Error envelope (RFC 7807)
```json
{
  "type": "https://mediclaim.ai/errors/validation",
  "title": "Validation failed",
  "status": 422,
  "detail": "file size exceeds 20MB",
  "instance": "/api/v1/claims",
  "errors": [{"field":"files[0]","message":"..."}],
  "trace_id": "..."
}
```

### Standard error codes

| HTTP | Code (type slug) | When |
|---|---|---|
| 400 | `bad_request` | malformed request |
| 401 | `unauthorized` | missing/invalid/expired token |
| 403 | `forbidden` | role insufficient |
| 404 | `not_found` | resource missing |
| 409 | `conflict` | duplicate claim_number, idempotency mismatch |
| 413 | `payload_too_large` | file >20MB or >10 files |
| 415 | `unsupported_media_type` | bad file type |
| 422 | `validation` | schema validation |
| 429 | `rate_limited` | too many requests |
| 500 | `internal` | unexpected |
| 502 | `upstream_unavailable` | LLM/OCR provider down |
| 503 | `service_unavailable` | DB/dependency down |
| 507 | `insufficient_storage` | disk full |

## 2. Auth endpoints

### POST /auth/login
Request:
```json
{ "email": "officer@demo.med", "password": "••••••••" }
```
Response 200:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": { "id": "uuid", "email": "...", "full_name": "...", "role": "officer" }
}
```
Errors: 401 invalid credentials; 429 rate limited (5/min/IP).

### POST /auth/refresh
Request: `{ "refresh_token": "..." }` → new access+refresh (rotation). Errors: 401.

### POST /auth/logout
Revokes refresh token (server-side blocklist in DB or in-memory for MVP). 204.

### GET /auth/me
Returns current user. 200 user object.

## 3. Claims endpoints

### POST /claims  (multipart/form-data) — create claim + upload bundle
Fields: `claim_number` (text), `provider_code` (text, optional), `files` (file[], max 10, ≤20MB each, PDF/PNG/JPEG).
Response 202:
```json
{
  "id": "uuid",
  "claim_number": "CLM-2026-0001",
  "status": "queued",
  "files": [{"id":"uuid","filename":"bill.pdf","status":"queued"}],
  "created_at": "..."
}
```
Errors: 401, 403 (officer+), 413, 415, 409 duplicate claim_number, 422.
RBAC: officer, manager, admin.

### GET /claims
Query: page, page_size, status, provider_id, from, to, sort, search (claim_number/provider).
Response 200 paginated list of ClaimSummary:
```json
{
  "items": [{
    "id":"uuid","claim_number":"...","provider_name":"...",
    "status":"scored","risk_score":72,"risk_band":"high",
    "recommended_decision":"partial","total_claimed_amount":125000.00,
    "created_at":"...","processed_at":"..."
  }],
  "total":..., "page":..., "page_size":..., "pages":...
}
```

### GET /claims/{id}
Full claim detail:
```json
{
  "id":"uuid","claim_number":"...","status":"adjudicated",
  "provider": {"id":"...","name":"...","code":"..."},
  "patient": {"name":"...","age":45,"gender":"M"},
  "policy_number":"POL-123",
  "admission_date":"2026-09-01","discharge_date":"2026-09-05",
  "total_claimed_amount":125000.00,"currency":"INR",
  "risk_score":72,"risk_confidence_low":65,"risk_confidence_high":79,
  "recommended_decision":"partial","recommended_amount":98000.00,
  "recommended_reasons":[{"text":"...","evidence":"..."}],
  "override_decision":null,"final_decision":"partial",
  "extraction": { "version":2, "model":"gpt-4o-mini", "fields":[
      {"field_path":"patient.name","value":"...","confidence":0.98,"human_corrected":false,"source_quote":"..."}
  ]},
  "flags":[{"type":"upcoding","severity":"high","evidence":"...","source":"rule","rule_id":"RFI-03"}],
  "files":[{"id":"...","filename":"...","status":"done","ocr_engine":"paddleocr","page_count":3}],
  "adjudication":{"decision":"partial","amount":98000.00,"reasons":[...],"created_at":"..."},
  "created_at":"...","processed_at":"...","reviewed_at":null
}
```

### PATCH /claims/{id}/fields  (human correction)
Request:
```json
{ "corrections": [{"field_path":"patient.name","value":"Corrected Name"}] }
```
Response 200 updated extraction fields. Side effects: sets `human_corrected=true`, writes audit event, recomputes score? [ASSUMPTION] corrections do NOT auto-recompute score in MVP; officer clicks "re-score" (POST /claims/{id}/rescore) to recompute. Reason: avoid surprising score changes.
RBAC: officer (own/assigned), manager, admin. 403 otherwise.

### POST /claims/{id}/rescore
Re-runs fraud scoring + adjudication on current (possibly corrected) extraction. Response 200 claim detail. Idempotent-ish.

### POST /claims/{id}/override
Request:
```json
{ "decision": "approve", "amount": 125000.00, "reason": "Verified with hospital; charges justified" }
```
Validation: reason required (min 10 chars). Response 200 claim detail with override. Audit event written.
RBAC: officer, manager, admin.

### GET /claims/{id}/files/{file_id}/status
Per-file status. (Also included in claim detail.)

### POST /claims/{id}/retry  (retry failed job)
Response 202. RBAC: officer+.

### GET /claims/{id}/audit
Paginated audit events for this claim. Response:
```json
{ "items":[{"seq":1,"action":"claim.created","actor":{"id":"...","name":"..."},"created_at":"...","payload":{...}}], "total":... }
```

### GET /claims/{id}/export?format=csv|json
Audit export (manager+). Streams file. (H-10) CSV cells sanitized (prefix `=`,`+`,`-`,`@` with tab); export action audited; only claim-scoped fields included; no PII beyond what the claim already holds.

## 4. Fraud / reporting endpoints

### GET /providers
Paginated provider list with aggregates (from materialized view). Query: window (days), sort.

### GET /providers/{id}
Provider detail + claim list.

### GET /providers/{id}/fraud-summary?from=&to=
```json
{ "provider_id":"...", "claim_count":42, "avg_risk_score":61.5, "amount_flagged":450000.00, "high_risk_count":7, "top_flags":[{"type":"upcoding","count":3}] }
```

### GET /dashboard/kpis?from=&to=
```json
{
  "claims_processed": 120,
  "claims_pending": 8,
  "fraud_flagged_count": 14,
  "amount_at_risk": 620000.00,
  "avg_tat_seconds": 18.4,
  "decision_rates": {"approve":0.55,"reject":0.20,"partial":0.25}
}
```

## 5. Admin endpoints (admin role only)

### GET /admin/users
### POST /admin/users  `{email, full_name, role, password}`
### PATCH /admin/users/{id}  `{role?, is_active?}`
### DELETE /admin/users/{id}  (soft: is_active=false; logged)
### GET /admin/usage  (counts, storage)
### POST /admin/demo/reset  (purges synthetic data; logged; requires confirm token)

## 6. System endpoints

### GET /healthz  → 200 `{"status":"ok"}`
### GET /readyz  → 200 `{"status":"ready","db":true,"ocr":true,"llm":true}` or 503.
### GET /metrics  (optional, P2) Prometheus text.

## 7. Rate limits

- Global: 100 req/min/IP (unauth), 300 req/min/user (auth).
- `/auth/login`: 5/min/IP.
- Upload: 10/min/user, max 5 concurrent jobs per user.
- 429 with `Retry-After` header.

## 8. Webhooks (P2, not MVP)

None in MVP. Future: claim status callbacks to insurer core (out of scope).

## 9. OpenAPI

FastAPI auto-generates OpenAPI at `/openapi.json` and Swagger UI at `/docs`. **Disabled in production** (`DOCS_ENABLED=false` → 404); committed spec generated in CI and used for typed client generation. (M-5) `/readyz` returns minimal status only, no versions/dependency details (M-6).

## 10. Assumptions (labeled)

- [ASSUMPTION] No real-time push; frontend polls claim status every 2s until terminal. SSE optional P1.
- [ASSUMPTION] Export formats CSV/JSON only; PDF reports deferred.
- [ASSUMPTION] Admin demo reset is a destructive action requiring confirm token + audit; allowed only in demo environment (env flag `DEMO_MODE=true`).
- [ASSUMPTION] `claim_number` is supplied by client (insurer's id); if absent, server generates `CLM-<tenant>-<seq>`.
