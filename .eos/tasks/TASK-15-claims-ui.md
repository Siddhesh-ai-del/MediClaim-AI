---
id: TASK-15
title: Claims list and detail UI
assignee: eos-frontend-engineer
parallel: yes
dependencies: [TASK-14, TASK-07]
---
# TASK-15 — Claims list and detail UI

## Description
Build claims list (paginated, filtered, sorted) and claim detail pages: extracted fields view/edit, risk score + confidence band, flags list with evidence, recommended decision, override dialog, audit timeline.

## Requirements
- Edit fields → PATCH /claims/{id}/fields; human-corrected flag.
- Override requires reason ≥10 chars.
- Audit timeline from /claims/{id}/audit.
- a11y: keyboard nav, focus visible, labels (S8).

## Expected output
- frontend/app/claims/*, frontend/components/claim/*

## Acceptance criteria
- [ ] List renders paginated claims.
- [ ] Detail shows extraction, score, flags, decision.
- [ ] Field edit saves and marks corrected.
- [ ] Override works with reason.
- [ ] Keyboard-only navigation works (AC-15).

## Verification method
`npm run test` (RTL); manual walkthrough.

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending