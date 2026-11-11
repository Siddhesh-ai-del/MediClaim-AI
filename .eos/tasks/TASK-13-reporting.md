---
id: TASK-13
title: Reporting aggregates and KPIs
assignee: eos-backend-engineer
parallel: yes
dependencies: [TASK-10, TASK-12]
---
# TASK-13 — Reporting aggregates and KPIs

## Description
Implement reporting endpoints: GET /providers, /providers/{id}, /providers/{id}/fraud-summary, GET /dashboard/kpis per api-contracts §4. Refresh materialized view after scoring batch.

## Requirements
- SQL aggregates by tenant+window.
- Provider list paginated, sortable.
- Dashboard KPIs match recomputed aggregates (AC-11).

## Expected output
- backend/app/reporting/router.py, service.py

## Acceptance criteria
- [ ] KPIs render and match recomputed aggregates.
- [ ] Provider aggregates sort/filter work.

## Verification method
pytest tests/reporting/.

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending