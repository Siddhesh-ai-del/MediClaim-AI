---
id: TASK-12
title: Audit module (append-only hash chain)
assignee: eos-backend-engineer
parallel: yes
dependencies: [TASK-02]
---
# TASK-12 — Audit module

## Description
Implement audit writer + verifier per database-schema §6 (hash chain, advisory lock for concurrency M-1, pseudonymized payload M-10). Export endpoint (CSV/JSON) with sanitization (H-10). Admin verify endpoint.

## Requirements
- append() in same transaction as business write; computes prev_hash under advisory lock; chain_seq monotonic per tenant.
- verify(tenant_id) replays and checks linkage/contiguity.
- Export streams CSV/JSON (manager+); sanitize cells; audit the export.
- Immutable: app role INSERT only + trigger.

## Expected output
- backend/app/audit/writer.py, verifier.py, router.py

## Acceptance criteria
- [ ] Hash chain verifies on clean data (AC-10).
- [ ] Tampering with a row makes verify() report broken seq.
- [ ] Concurrent writes don't break chain (load test).
- [ ] Export works (CSV/JSON).

## Verification method
pytest tests/audit/ (unit+integration); concurrency test.

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending