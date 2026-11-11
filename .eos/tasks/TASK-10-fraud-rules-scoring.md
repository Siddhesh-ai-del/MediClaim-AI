---
id: TASK-10
title: Fraud rules engine and scoring
assignee: eos-backend-engineer
parallel: yes
dependencies: [TASK-09]
---
# TASK-10 — Fraud rules engine and scoring

## Description
Implement rule-based RFIs (IRDAI-aligned) + statistical anomaly + risk score 0-100 + confidence band per ADR-07. Flags with type, evidence, severity, source. Provider aggregates.

## Requirements
- Rule catalog: upcoding, phantom billing, unbundling, duplicate claim, inflated charge vs tariff, dx-procedure mismatch, provider outlier.
- Statistical: amount z-score, duplicate detection (claim_number/patient/date), provider outlier (avg risk, volume).
- Score aggregation; confidence band.
- Provider materialized view refresh after scoring batch.
- ML classifier deferred (P1, experimental).

## Expected output
- backend/app/fraud/rules.py, stats.py, scorer.py, catalog.py

## Acceptance criteria
- [ ] Injected anomaly in synthetic claim produces correct flag type+evidence+severity.
- [ ] Clean claim produces no false flags (precision target ≥0.80).
- [ ] Risk score deterministic for same input (AC-5).
- [ ] Provider aggregates render.

## Verification method
pytest tests/fraud/ (unit+integration on synthetic eval set).

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending