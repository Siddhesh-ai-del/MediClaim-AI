---
id: TASK-20
title: End-to-end integration
assignee: eos-integration-engineer
parallel: no
dependencies: [TASK-15, TASK-16, TASK-17, TASK-18, TASK-19]
---
# TASK-20 — End-to-end integration

## Description
Wire frontend↔backend; verify CORS, polling, exports; run Playwright E2E primary workflow (upload→extract→score→adjudicate→audit).

## Requirements
- E2E suite via e2e-runner/Playwright.
- Covers loading/error/empty states, invalid input, failure recovery (Stage 7 prep).
- Fix integration bugs found.

## Expected output
- e2e/ tests, bug fixes.

## Acceptance criteria
- [ ] Primary workflow E2E passes.
- [ ] CORS configured; no console errors.
- [ ] Status polling works.

## Verification method
`npx playwright test` (all green).

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending