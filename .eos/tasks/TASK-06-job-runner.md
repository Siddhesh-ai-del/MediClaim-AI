---
id: TASK-06
title: Job runner skeleton
assignee: eos-backend-engineer
parallel: yes
dependencies: [TASK-01]
---
# TASK-06 — Job runner skeleton

## Description
Implement in-process job runner (asyncio + ProcessPoolExecutor) with processing_job table, idempotency keys, retry/backoff, stale-job reaper (error-handling §5).

## Requirements
- Enqueue/dequeue; status transitions; attempts/max_attempts; last_error.
- Concurrency caps (5/user, 20 global); queue depth cap 100/tenant (H-2).
- Stale-job reaper resets `running`→`queued` after 5 min.

## Expected output
- backend/app/ingestion/jobs.py, backend/app/ingestion/worker.py

## Acceptance criteria
- [ ] Dummy job executes and status transitions queued→running→succeeded.
- [ ] Failed job retries 3x then failed.
- [ ] Idempotency key prevents duplicate job rows.

## Verification method
pytest tests/ingestion/jobs/ (unit+integration).

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending