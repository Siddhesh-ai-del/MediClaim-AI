---
id: TASK-18
title: Dashboard and provider aggregates UI
assignee: eos-frontend-engineer
parallel: yes
dependencies: [TASK-14, TASK-13]
---
# TASK-18 — Dashboard and provider aggregates UI

## Description
Build manager dashboard: KPI cards (claims processed, fraud flagged, ₹ at risk, avg TAT, decision rates), provider table with aggregates, date range filter.

## Requirements
- Fetch /dashboard/kpis and /providers.
- Charts (simple: recharts or plain).
- Date range filter.

## Expected output
- frontend/app/dashboard/page.tsx, frontend/app/providers/page.tsx

## Acceptance criteria
- [ ] KPIs render and match backend.
- [ ] Provider table sortable/paginated.

## Verification method
`npm run test`; manual walkthrough.

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending