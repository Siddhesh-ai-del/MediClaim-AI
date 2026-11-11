---
id: TASK-11
title: Adjudication decision engine
assignee: eos-backend-engineer
parallel: yes
dependencies: [TASK-10]
---
# TASK-11 — Adjudication decision engine

## Description
Implement decision engine mapping score/flags → approve/reject/partial + amount + ≥1 reason citing evidence. Override flow with mandatory reason + audit. Rescore endpoint.

## Requirements
- Recommended decision rules (thresholds documented).
- Partial-approve includes amount.
- Override requires reason ≥10 chars; logged.
- Rescore recomputes on corrected extraction.

## Expected output
- backend/app/adjudication/engine.py, router endpoints

## Acceptance criteria
- [ ] Every scored claim gets recommended_decision + ≥1 reason (AC-8).
- [ ] Override persists decision+reason in audit log (AC-9).
- [ ] Rescore updates score/decision.

## Verification method
pytest tests/adjudication/.

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending