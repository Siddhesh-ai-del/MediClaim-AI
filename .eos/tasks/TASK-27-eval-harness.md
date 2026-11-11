---
id: TASK-27
title: Eval harness
assignee: eos-qa-engineer
parallel: yes
dependencies: [TASK-09, TASK-10, TASK-25]
---
# TASK-27 — Eval harness

## Description
Build evaluation harness: extraction F1, fraud precision/recall, prompt-injection tests, adjudication accuracy on synthetic labeled set. Report metrics with commands+output in STATE.md.

## Requirements
- Eval script runnable in CI.
- Report extraction F1 ≥0.85, fraud precision ≥0.80, recall ≥0.70.
- Injection test cases ≥10.

## Expected output
- backend/eval/run_eval.py, backend/eval/report.json

## Acceptance criteria
- [ ] Eval runs and reports metrics.
- [ ] Targets met or gaps documented.
- [ ] Injection tests pass.

## Verification method
`python backend/eval/run_eval.py` → report; recorded in STATE.md.

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending