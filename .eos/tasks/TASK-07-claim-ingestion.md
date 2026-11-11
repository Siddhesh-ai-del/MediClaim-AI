---
id: TASK-07
title: Claim CRUD and ingestion endpoint
assignee: eos-backend-engineer
parallel: no
dependencies: [TASK-02, TASK-03, TASK-05, TASK-06]
---
# TASK-07 — Claim CRUD and ingestion endpoint

## Description
Implement claim lifecycle + multipart upload endpoint per api-contracts §3 (POST /claims, GET /claims, GET /claims/{id}, PATCH fields, retry, status). Tenant scoping (H-3). Claim ownership (M-18).

## Requirements
- POST /claims creates claim + claim_file rows, stores bytes, enqueues job, returns 202.
- Validation: file type/size/count; claim_number uniqueness (tenant-scoped).
- Sort/filter allowlist (H-6).
- Officer sees own+assigned; manager/admin all (tenant).

## Expected output
- backend/app/claims/router.py, service.py, repo.py, schemas.py

## Acceptance criteria
- [ ] Upload valid bundle → 202 + claim_id; invalid → 413/415/422.
- [ ] GET /claims paginated, filtered, sorted (allowlist).
- [ ] IDOR: officer cannot read another's unassigned claim (404).
- [ ] Duplicate claim_number → 409.

## Verification method
pytest tests/claims/ (integration against test Postgres).

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending