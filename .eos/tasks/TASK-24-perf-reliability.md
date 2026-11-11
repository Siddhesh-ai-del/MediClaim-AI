---
id: TASK-24
title: Performance and reliability
assignee: eos-backend-engineer
parallel: yes
dependencies: [TASK-23]
---
# TASK-24 — Performance and reliability

## Description
Verify NFR-1 (≤30s for 5-page bundle), NFR-3 (50 concurrent uploads), retry/backoff, stale-job reaper, graceful degradation. Tune OCR timeouts, concurrency caps, DB pooling.

## Requirements
- Load test 50 concurrent uploads.
- Measure end-to-end time on 5-page synthetic bundle (record in STATE.md).
- Fix bottlenecks.

## Expected output
- Perf report in docs/ or STATE.md verification log.

## Acceptance criteria
- [ ] 5-page bundle ≤30s (AC-13).
- [ ] 50 concurrent uploads no failure (NFR-3).
- [ ] Retry/backoff verified.

## Verification method
Load test script + timing measurement recorded.

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending