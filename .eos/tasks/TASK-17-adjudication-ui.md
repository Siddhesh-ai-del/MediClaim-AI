---
id: TASK-17
title: Adjudication UI
assignee: eos-frontend-engineer
parallel: yes
dependencies: [TASK-14, TASK-11]
---
# TASK-17 — Adjudication UI

## Description
Build adjudication panel: recommended decision display, override dialog with reason, rescore button, final decision badge, adjudication history.

## Requirements
- Override dialog validates reason ≥10 chars.
- Rescore triggers POST /claims/{id}/rescore.
- Show adjudication history list.

## Expected output
- frontend/components/adjudication/*, integration in claim detail

## Acceptance criteria
- [ ] Override flow works end-to-end.
- [ ] Rescore updates UI.
- [ ] History renders.

## Verification method
`npm run test`; manual walkthrough.

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending