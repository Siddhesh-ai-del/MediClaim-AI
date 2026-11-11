---
id: TASK-21
title: Audit export and verification
assignee: eos-backend-engineer
parallel: yes
dependencies: [TASK-12, TASK-20]
---
# TASK-21 — Audit export and verification

## Description
Finalize audit export (CSV/JSON) sanitization, admin verify endpoint, and frontend export button. Verify hash chain end-to-end.

## Requirements
- Export sanitized CSV (H-10); manager+ only; audit the export.
- Admin verify endpoint returns {ok, broken_at_seq, reason}.
- Frontend download button.

## Expected output
- backend/app/audit/export.py; frontend export button.

## Acceptance criteria
- [ ] Export downloads valid CSV/JSON.
- [ ] Verify endpoint returns ok on clean data.

## Verification method
pytest tests/audit/export/; manual download.

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending