---
id: TASK-25
title: Synthetic demo data generator
assignee: eos-backend-engineer
parallel: yes
dependencies: [TASK-10]
---
# TASK-25 — Synthetic demo data generator

## Description
Build generator producing synthetic claim bundles with injected anomalies (all 7 flag types) for demo and eval. Includes ground-truth labels for precision/recall. Seed script for demo dataset.

## Requirements
- Generate ≥50 claims across ≥5 providers.
- Inject anomalies with known labels.
- Seed script idempotent; reset via admin endpoint.

## Expected output
- backend/scripts/gen_demo_data.py, backend/scripts/seed.py
- tests/fixtures/ sample bills

## Acceptance criteria
- [ ] Seed creates demo dataset; reset works.
- [ ] Ground-truth labels available for eval.

## Verification method
`python backend/scripts/seed.py`; verify counts.

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending