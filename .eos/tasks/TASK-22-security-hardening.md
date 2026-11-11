---
id: TASK-22
title: Security hardening
assignee: eos-security-reviewer
parallel: no
dependencies: [TASK-20]
---
# TASK-22 — Security hardening

## Description
Close security review findings: CSP/headers, tenant scoping enforcement, sort allowlist, path safety, seeded creds, lockout persistence, demo reset guards, CSV sanitization, real-data guard, DPDP posture (already authored). Run ecc:security-audit.

## Requirements
- Implement remaining M/H items from design-review §8 (already design-level blockers resolved; this task implements them).
- Add security test suite: injection, IDOR, XSS, path traversal, brute-force, header checks.

## Expected output
- Hardened middleware, tests, security-audit report.

## Acceptance criteria
- [ ] All blockers implemented or risk-accepted with log.
- [ ] security-audit clean.
- [ ] Security test suite passes.

## Verification method
`ecc:security-audit`; pytest tests/security/.

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending