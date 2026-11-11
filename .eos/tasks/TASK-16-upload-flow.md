---
id: TASK-16
title: Upload flow and status polling
assignee: eos-frontend-engineer
parallel: yes
dependencies: [TASK-14, TASK-07]
---
# TASK-16 — Upload flow and status polling

## Description
Build claim creation/upload page: form (claim number, provider), multi-file dropzone, per-file status, polling claim status until terminal, error display.

## Requirements
- multipart upload to POST /claims.
- Per-file status queued/processing/done/failed with error reason (AC-2).
- Poll every 2s until terminal; show extracted result link.
- File validation client-side (size/type/count) mirroring server.

## Expected output
- frontend/app/claims/new/page.tsx, frontend/components/upload/*

## Acceptance criteria
- [ ] Upload valid bundle shows progress and final claim.
- [ ] Invalid file shows reason.
- [ ] Polling stops on terminal status.

## Verification method
`npm run test`; manual E2E.

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending