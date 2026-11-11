---
id: TASK-23
title: Test suite and coverage
assignee: eos-qa-engineer
parallel: no
dependencies: [TASK-22]
---
# TASK-23 — Test suite and coverage

## Description
Build comprehensive test suite: unit, integration, security, E2E; reach 80% coverage on critical paths (extraction, fraud, adjudication, audit, auth). Independent review (R06).

## Requirements
- pytest --cov-fail-under=80 on critical modules.
- Playwright E2E for primary workflow + a11y basics.
- Coverage report committed.

## Expected output
- tests/ (unit/integration/security), e2e/, coverage.xml

## Acceptance criteria
- [ ] Coverage ≥80% on critical paths (AC-14).
- [ ] All tests green.
- [ ] Independent QA sign-off (R06).

## Verification method
`cd backend && pytest --cov=app --cov-fail-under=80`; `npx playwright test`.

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending