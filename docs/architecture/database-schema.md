# Database Schema — MediClaim AI (PostgreSQL 16)

- Date: 2026-11-11
- Mode stage: software-dev Stage 3
- Related: ADR-03 (Postgres), ADR-09 (data model), ADR-08 (auth)
- Notation: DDL is the source of truth; SQLAlchemy models mirror it. Migrations via Alembic.

## 1. Design principles

1. **Relational core, JSONB for flexible payloads** (extracted fields, reasons, evidence) — relational for auditability/aggregates, JSONB for evolving extraction schema.
2. **Single-tenant MVP**: `tenant_id` columns retained for forward compat; no RLS in MVP (ADR-09). All demo rows use one seeded tenant.
3. **Append-only audit**: `audit_event` has no UPDATE/DELETE grants for app role; tamper-evidence via hash chain (§6).
4. **Idempotency/retry**: `processing_job` tracks attempts and last error; re-running a completed job is a no-op (idempotency key).
5. **Soft state, not soft delete**: no deletes in MVP except admin purge of synthetic demo data (logged).
6. **Timestamps**: all `*_at` are `timestamptz`, default `now()`. IDs are UUID v4 (gen_random_uuid()).
7. **Money**: `numeric(14,2)` in INR; never float.

## 2. Extensions & enums

```sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- gen_random_uuid
CREATE EXTENSION IF NOT EXISTS "citext";      -- case-insensitive email

CREATE TYPE user_role        AS ENUM ('officer','manager','admin');
CREATE TYPE claim_status     AS ENUM ('queued','processing','extracted','scored','adjudicated','reviewed','failed');
CREATE TYPE file_status      AS ENUM ('queued','processing','done','failed');
CREATE TYPE decision_type    AS ENUM ('approve','reject','partial');
CREATE TYPE flag_type        AS ENUM ('upcoding','phantom_billing','unbundling','duplicate_claim','inflated_charge','diagnosis_procedure_mismatch','provider_outlier');
CREATE TYPE severity         AS ENUM ('low','medium','high');
CREATE TYPE fraud_source     AS ENUM ('rule','stat','ml');
CREATE TYPE job_status       AS ENUM ('queued','running','succeeded','failed','retrying');
CREATE TYPE job_type         AS ENUM ('ocr','extraction','scoring','adjudication');
```

## 3. Tables

### 3.1 tenant

```sql
CREATE TABLE tenant (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name        text NOT NULL,
  slug        text NOT NULL UNIQUE,
  created_at  timestamptz NOT NULL DEFAULT now()
);
```

### 3.2 user_account

```sql
CREATE TABLE user_account (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      uuid NOT NULL REFERENCES tenant(id),
  email          citext NOT NULL,
  password_hash  text NOT NULL,            -- bcrypt, cost >= 12
  full_name      text NOT NULL,
  role           user_role NOT NULL DEFAULT 'officer',
  is_active      boolean NOT NULL DEFAULT true,
  failed_login_count integer NOT NULL DEFAULT 0,
  locked_until       timestamptz,
  last_login_at      timestamptz,
  created_at         timestamptz NOT NULL DEFAULT now(),
  updated_at         timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, email)
);
CREATE INDEX idx_user_tenant_role ON user_account(tenant_id, role);
```

### 3.3 provider

```sql
CREATE TABLE provider (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      uuid NOT NULL REFERENCES tenant(id),
  provider_code  text NOT NULL,            -- hospital/TPA provider id
  name           text NOT NULL,
  provider_type  text,                     -- hospital/clinic/diagnostic
  created_at     timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, provider_code)
);
CREATE INDEX idx_provider_tenant ON provider(tenant_id);
```

### 3.4 claim

```sql
CREATE TABLE claim (
  id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id               uuid NOT NULL REFERENCES tenant(id),
  claim_number            text NOT NULL,                 -- external claim id
  provider_id             uuid REFERENCES provider(id),
  submitted_by            uuid NOT NULL REFERENCES user_account(id),
  assigned_to             uuid REFERENCES user_account(id),
  status                  claim_status NOT NULL DEFAULT 'queued',
  total_claimed_amount    numeric(14,2),
  currency                text NOT NULL DEFAULT 'INR',
  patient_name            text,
  patient_age             integer,
  patient_gender          text,
  policy_number           text,
  admission_date          date,
  discharge_date          date,
  risk_score              integer CHECK (risk_score BETWEEN 0 AND 100),
  risk_confidence_low     integer CHECK (risk_confidence_low BETWEEN 0 AND 100),
  risk_confidence_high    integer CHECK (risk_confidence_high BETWEEN 0 AND 100),
  recommended_decision    decision_type,
  recommended_amount      numeric(14,2),
  recommended_reasons     jsonb NOT NULL DEFAULT '[]'::jsonb,
  override_decision       decision_type,
  override_reason         text,
  override_by             uuid REFERENCES user_account(id),
  override_at             timestamptz,
  final_decision          decision_type,                -- effective decision (override or recommended)
  extraction_version      integer,
  error_reason            text,
  created_at              timestamptz NOT NULL DEFAULT now(),
  updated_at              timestamptz NOT NULL DEFAULT now(),
  processed_at            timestamptz,
  reviewed_at             timestamptz,
  UNIQUE (tenant_id, claim_number)
);
CREATE INDEX idx_claim_tenant_status ON claim(tenant_id, status);
CREATE INDEX idx_claim_provider ON claim(provider_id);
CREATE INDEX idx_claim_created ON claim(tenant_id, created_at DESC);
CREATE INDEX idx_claim_risk ON claim(tenant_id, risk_score DESC) WHERE risk_score IS NOT NULL;
```

### 3.5 claim_file

```sql
CREATE TABLE claim_file (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  claim_id            uuid NOT NULL REFERENCES claim(id) ON DELETE CASCADE,
  original_filename   text NOT NULL,
  content_type        text NOT NULL,
  size_bytes          bigint NOT NULL CHECK (size_bytes > 0 AND size_bytes <= 20971520),
  storage_path        text NOT NULL,         -- server-generated UUID filename; original filename in original_filename only (H-5)
  status              file_status NOT NULL DEFAULT 'queued',
  error_reason        text,
  ocr_engine          text,                 -- 'paddleocr' | 'tesseract' | 'cloud'
  ocr_confidence      numeric(5,4),
  page_count          integer,
  sha256              text NOT NULL,        -- dedup / integrity
  created_at          timestamptz NOT NULL DEFAULT now(),
  processed_at        timestamptz
);
CREATE INDEX idx_claimfile_claim ON claim_file(claim_id);
```

### 3.6 ocr_result

```sql
CREATE TABLE ocr_result (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  claim_file_id  uuid NOT NULL REFERENCES claim_file(id) ON DELETE CASCADE,
  page_number    integer NOT NULL CHECK (page_number >= 1),
  text           text NOT NULL,
  confidence     numeric(5,4),
  engine         text NOT NULL,
  created_at     timestamptz NOT NULL DEFAULT now(),
  UNIQUE (claim_file_id, page_number)
);
```

### 3.7 extraction (versioned)

```sql
CREATE TABLE extraction (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  claim_id         uuid NOT NULL REFERENCES claim(id) ON DELETE CASCADE,
  version          integer NOT NULL,
  extractor_model  text NOT NULL,           -- 'gpt-4o-mini' | 'qwen2.5-vl' | ...
  raw_llm_output   jsonb,                  -- full model output for audit/replay
  created_at       timestamptz NOT NULL DEFAULT now(),
  UNIQUE (claim_id, version)
);
CREATE INDEX idx_extraction_claim ON extraction(claim_id);
```

### 3.8 extraction_field

```sql
CREATE TABLE extraction_field (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  extraction_id    uuid NOT NULL REFERENCES extraction(id) ON DELETE CASCADE,
  field_path       text NOT NULL,          -- e.g. 'patient.name', 'line_items[2].unit_price'
  value_json       jsonb,                  -- null when missing (never hallucinated)
  confidence       numeric(5,4),
  source_quote     text,                   -- quoted evidence from OCR text
  human_corrected  boolean NOT NULL DEFAULT false,
  corrected_by     uuid REFERENCES user_account(id),
  corrected_at     timestamptz,
  corrected_value  jsonb,                  -- original pre-correction value retained
  created_at       timestamptz NOT NULL DEFAULT now(),
  UNIQUE (extraction_id, field_path)
);
CREATE INDEX idx_ef_extraction ON extraction_field(extraction_id);
```

### 3.9 fraud_flag

```sql
CREATE TABLE fraud_flag (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  claim_id     uuid NOT NULL REFERENCES claim(id) ON DELETE CASCADE,
  flag_type    flag_type NOT NULL,
  severity     severity NOT NULL,
  evidence     text NOT NULL,              -- human-readable evidence quote
  source       fraud_source NOT NULL,
  rule_id      text,                       -- e.g. 'RFI-07-upcoding'
  score_impact integer NOT NULL DEFAULT 0,
  created_at   timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_flag_claim ON fraud_flag(claim_id);
CREATE INDEX idx_flag_type ON fraud_flag(flag_type);
```

### 3.10 adjudication (history)

```sql
CREATE TABLE adjudication (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  claim_id        uuid NOT NULL REFERENCES claim(id) ON DELETE CASCADE,
  decision        decision_type NOT NULL,
  amount          numeric(14,2),
  reasons         jsonb NOT NULL DEFAULT '[]'::jsonb,   -- [{text, evidence}]
  engine_version  text NOT NULL,
  is_override     boolean NOT NULL DEFAULT false,
  override_by     uuid REFERENCES user_account(id),
  override_reason text,
  created_at      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_adj_claim ON adjudication(claim_id, created_at DESC);
```

### 3.11 processing_job (retry/idempotency)

```sql
CREATE TABLE processing_job (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  claim_id         uuid NOT NULL REFERENCES claim(id) ON DELETE CASCADE,
  job_type         job_type NOT NULL,
  status           job_status NOT NULL DEFAULT 'queued',
  idempotency_key  text NOT NULL UNIQUE,
  attempts         integer NOT NULL DEFAULT 0,
  max_attempts     integer NOT NULL DEFAULT 3,
  last_error       text,
  started_at       timestamptz,
  finished_at      timestamptz,
  created_at       timestamptz NOT NULL DEFAULT now(),
  updated_at       timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_job_claim ON processing_job(claim_id);
CREATE INDEX idx_job_status ON processing_job(status);
```

### 3.12 tariff_reference (for inflated-charge rule)

```sql
CREATE TABLE tariff_reference (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code         text NOT NULL,              -- procedure/drug code
  description  text,
  max_rate     numeric(14,2) NOT NULL,
  currency     text NOT NULL DEFAULT 'INR',
  source       text,                       -- 'CGHS' | 'PMJAY' | internal
  effective_from date,
  effective_to   date,
  UNIQUE (code, source, effective_from)
);
CREATE INDEX idx_tariff_code ON tariff_reference(code);
```

### 3.13 audit_event (append-only, hash chain)

```sql
CREATE TABLE audit_event (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL REFERENCES tenant(id),
  claim_id      uuid REFERENCES claim(id),          -- null for global events
  actor_user_id uuid REFERENCES user_account(id),   -- null for system
  action        text NOT NULL,                      -- 'claim.created', 'field.corrected', ...
  entity_type   text NOT NULL,                      -- 'claim','extraction_field',...
  entity_id     uuid,
  payload       jsonb NOT NULL DEFAULT '{}'::jsonb,
  payload_hash  text NOT NULL,                      -- SHA-256(canonical payload + metadata)
  prev_hash     text,                               -- previous event's payload_hash (tenant chain)
  chain_seq     bigint NOT NULL,                    -- monotonic per tenant
  created_at    timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, chain_seq)
);
CREATE INDEX idx_audit_tenant_seq ON audit_event(tenant_id, chain_seq);
CREATE INDEX idx_audit_claim ON audit_event(claim_id, created_at);
```

### 3.14 provider aggregate (materialized view)

```sql
CREATE MATERIALIZED VIEW provider_fraud_agg AS
SELECT
  c.tenant_id,
  c.provider_id,
  count(*)::int AS claim_count,
  coalesce(avg(c.risk_score),0)::numeric(6,2) AS avg_risk_score,
  coalesce(sum(CASE WHEN c.risk_score >= 70 THEN c.total_claimed_amount ELSE 0 END),0)::numeric(14,2) AS amount_flagged,
  count(*) FILTER (WHERE c.risk_score >= 70)::int AS high_risk_count,
  max(c.created_at) AS last_claim_at
FROM claim c
WHERE c.provider_id IS NOT NULL AND c.risk_score IS NOT NULL
GROUP BY c.tenant_id, c.provider_id;
CREATE UNIQUE INDEX idx_pfa_pk ON provider_fraud_agg(tenant_id, provider_id);
-- Refresh: REFRESH MATERIALIZED VIEW CONCURRENTLY provider_fraud_agg; (called after scoring batch)
```

## 4. Relationships summary

- tenant 1→* user_account, provider, claim, audit_event
- claim 1→* claim_file, extraction, fraud_flag, adjudication, processing_job; 1→1? latest extraction
- claim_file 1→* ocr_result
- extraction 1→* extraction_field
- claim *→1 provider
- audit_event *→1 claim (nullable), *→1 user_account (nullable)

## 5. Append-only enforcement (audit_event)

```sql
-- App role has INSERT only on audit_event
REVOKE UPDATE, DELETE, TRUNCATE ON audit_event FROM app_role;
-- Optional hardening: trigger that raises on UPDATE/DELETE
CREATE OR REPLACE FUNCTION audit_immutable() RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'audit_event is append-only';
END; $$ LANGUAGE plpgsql;
CREATE TRIGGER trg_audit_no_update BEFORE UPDATE OR DELETE ON audit_event
  FOR EACH ROW EXECUTE FUNCTION audit_immutable();
```

## 6. Audit hash chain algorithm

- **Scope**: one chain per tenant (chain_seq monotonic per tenant). Global events (claim_id null) share the same chain.
- **Hash input (canonical)**: `SHA-256( json.dumps({
    "tenant_id": ..., "chain_seq": ..., "action": ..., "entity_type": ..., "entity_id": ...,
    "actor_user_id": ..., "claim_id": ..., "payload": ..., "prev_hash": ..., "created_at": ISO8601
  }, sort_keys=True, separators=(",",":")) )`
- **prev_hash**: `payload_hash` of the previous event in tenant chain (NULL for first).
- **Writer**: `audit.append(event)` runs in the same transaction as the business write. Concurrency (M-1): acquire `pg_advisory_xact_lock(hashtext(tenant_id::text))` (or a per-tenant DB sequence) to serialize chain_seq allocation; then compute prev_hash by `SELECT payload_hash ... FOR UPDATE`; insert with chain_seq = coalesce(max,0)+1. Retries on unique violation (max 3).
- **Immutability scope (M-2)**: app role has INSERT only + trigger blocks UPDATE/DELETE — protects against application bugs, not against a DB superuser. Production hardening: periodic external hash anchoring (e.g., daily root hash published to immutable store) — documented, not MVP.
- **PII in payload (M-10)**: audit payload must pseudonymize patient identifiers (store patient_ref hash, not name/age) to support right-to-erasure; raw patient name never in audit payload.
- **Verifier**: `audit.verify(tenant_id)` replays all events in chain_seq order, recomputes hashes, checks linkage + sequence contiguity; returns `{ok, broken_at_seq, reason}`. Exposed as admin endpoint and CI test.
- **Failure modes**: hash mismatch → `AUDIT_CHAIN_BROKEN` (critical alert); missing sequence → gap detected; duplicate seq → unique violation.

## 7. Indexes summary (performance)

- Claim lists by tenant+status, tenant+created_at; risk sort; provider FK.
- Flags by claim; adjudication by claim+time.
- Audit by tenant+seq and claim+time.
- Tariff by code.
- Materialized view unique index for concurrent refresh.

## 8. Data retention (DPDP-aligned)

- Synthetic demo data only; no real PII. Retention: demo dataset reset on demand (admin action, logged in audit).
- Audit log retained for the life of the tenant (regulatory evidence); deletion requires documented approval (out of MVP).
- Uploaded files purged with claim deletion (admin only, logged).

## 9. Assumptions (labeled)

- [ASSUMPTION] Single-tenant MVP; `tenant_id` reserved but not enforced via RLS. Multi-tenant migration adds RLS policies + middleware (documented, not implemented).
- [ASSUMPTION] Currency INR only; multi-currency deferred.
- [ASSUMPTION] `patient_age` integer; date-of-birth not stored (minimize PII even in synthetic data).
- [ASSUMPTION] No full-text search index in MVP; LIKE/ILIKE on claim_number/provider name sufficient for demo scale.
- [ASSUMPTION] Materialized view refresh is manual/batch; acceptable for demo; automate if >1k claims.
