# Error Handling Strategy — MediClaim AI

- Date: 2026-11-11
- Mode stage: software-dev Stage 3
- Related: NFR-10, NFR-11, NFR-12, api-contracts §1

## 1. Principles

1. **Validate at the boundary** (Pydantic v2 on backend, zod on frontend); reject early with structured errors.
2. **Typed domain errors** internally; map to HTTP problem details at the edge (no leaky stack traces).
3. **Never swallow errors**; log with context (request id, user, claim id) and rethrow user-friendly message.
4. **Partial failure isolation**: one failed file does not fail the whole claim; claim completes with per-file status.
5. **Idempotent retries**: re-running a job is safe; idempotency keys prevent duplicate side effects.
6. **Graceful degradation**: OCR/LLM outage queues and notifies (NFR-12), doesn't corrupt state.

## 2. Error taxonomy

### 2.1 Validation errors (4xx, client)
- Schema/type/range/format errors → 422 with `errors[]` listing field + message.
- File type/size/count → 415/413 with reason.
- Auth → 401/403.

### 2.2 Domain errors (4xx)
Defined as Python exceptions in `app/common/errors.py`:
- `ClaimNotFound`, `FileNotFound`, `UserNotFound`, `ProviderNotFound`
- `DuplicateClaimNumber`
- `InvalidStatusTransition` (e.g., override on queued claim)
- `ExtractionMissing` (scoring before extraction)
- `OverrideReasonRequired`
- `AuditChainBroken` (critical)
- `TenantMismatch`

Each maps to a problem type slug + HTTP status.

### 2.3 Infrastructure errors (5xx)
- `DatabaseUnavailable`, `StorageUnavailable`, `OcrUnavailable`, `LlmUnavailable`, `RateLimited`.
- Mapped to 503/502/429 with retry-after where applicable.

## 3. Backend error handling pattern

```python
# app/common/errors.py
class DomainError(Exception):
    code: str = "domain_error"
    status: int = 400
    title: str = "Domain error"

class ClaimNotFound(DomainError):
    code = "not_found"; status = 404; title = "Claim not found"

# FastAPI exception handler
@app.exception_handler(DomainError)
async def domain_handler(request, exc):
    return JSONResponse(status_code=exc.status, content=problem_details(exc, request))
```

- All route handlers let domain/infra exceptions propagate to handlers; no bare `except:`. Catch specific exceptions, log, rethrow as domain error.
- DB session rollback on exception; request-scoped session via dependency.
- Background jobs catch exceptions, record `last_error`, set job status `failed`, update claim `error_reason` (for terminal failures) or `retrying`.

## 4. Validation (boundary)

- Pydantic v2 models with strict types, field validators (email, password policy, amount ≥0, date ordering admission≤discharge).
- File validation: content-type allowlist (`application/pdf`, `image/png`, `image/jpeg`); size ≤20MB; count ≤10; magic-byte check (not just extension); reject path traversal in filename.
- Reject unknown fields (`model_config = ConfigDict(extra='forbid')`) on request bodies.
- Frontend zod mirrors for UX; server authoritative.

## 5. Job failure & retry

- Each `processing_job` has `attempts`, `max_attempts=3`, `last_error`.
- Retry policy: exponential backoff 2s, 8s, 32s; on final failure → job `failed`, claim status `failed` with `error_reason` summarizing which step failed; per-file status set.
- Partial extraction: if OCR succeeds but LLM fails, store OCR text, mark claim `failed` with reason `extraction_failed`; officer can retry. No partial `extraction` row without validation.
- Idempotency: re-running `ocr` job checks existing `ocr_result` rows (skip if present & valid) and `extraction` version; re-running scoring replaces flags for that claim (transactional). `idempotency_key` on job prevents duplicate job rows.
- Manual retry: `POST /claims/{id}/retry` resets failed jobs to `queued` (officer+), logged.

## 6. Partial extraction handling

- LLM may return partial JSON or low confidence. Pydantic validation requires all mandatory fields? Strategy: extraction schema has all fields optional (nullable) with confidence; missing → `null` (AC-3, never hallucinated). If LLM returns a field not in schema → drop (extra='forbid' on extraction schema) and log warning.
- If LLM output fails JSON parse → retry once with stricter prompt; if still fails → job failed, no extraction row.
- Confidence band: if overall extraction confidence <0.6 → flag claim for manual review (adjudication reason "low extraction confidence").

## 7. User-facing messages

- Never expose stack traces, SQL, or secrets. Map errors to plain-language messages:
  - Upload: "We couldn't read this file. Please upload a clear PDF or image under 20MB."
  - OCR failure: "Text extraction failed for {filename}. You can retry or remove this file."
  - LLM timeout: "Extraction is taking longer than expected. We'll notify you when it's ready." (queued)
  - Auth: "Your session expired. Please sign in again."
- Frontend shows toast + inline field errors; preserves user input on validation failure.

## 8. Concurrency & data integrity

- Claim status transitions guarded by DB-level check (application enforces allowed transitions; optimistic concurrency via `updated_at` version check on PATCH).
- Audit writes in same transaction as business write; if audit fails, business write rolls back (no silent state change without audit).
- File storage write then DB insert; on DB failure, delete stored file (compensating action) — best-effort, logged.

## 9. Observability of errors

- Structured logs: `{"level":"error","request_id":"...","user_id":"...","claim_id":"...","error":"...","trace":"..."}` (trace only server-side).
- Sentry (optional) captures unhandled exceptions with PII scrubbing (no patient fields, no tokens).
- Audit log remains source of truth for business events even if logs rotate.

## 9.1 Security-relevant handling (H-5, H-6, H-10)
- File storage: server-generated UUID filename; original filename stored as metadata only. Path constructed as `${STORAGE_PATH}/${tenant_id}/${claim_id}/${uuid}`; reject any `..`/separator in original filename; validate magic bytes + basic PDF structure; enforce size limits before parsing; per-file processing timeout (M-15).
- Sort/filter: allowlist enforced before query; invalid → 422 `validation` (H-6).
- CSV export: sanitize cells prefixed with `=`,`+`,`-`,`@` (prepend tab); manager+ only; audit the export (H-10).
- No stack traces/secrets/SQL in responses (L-2); verified by tests.

## 10. Assumptions (labeled)

- [ASSUMPTION] No distributed tracing (OpenTelemetry) in MVP; request-id propagation only.
- [ASSUMPTION] Retry backoff in-process; if process restarts mid-job, job stays `running` → stale-job reaper resets to `queued` after 5 min.
- [ASSUMPTION] LLM JSON parse retry once; more retries risk cost blowup.
