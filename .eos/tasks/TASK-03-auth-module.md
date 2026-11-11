---
id: TASK-03
title: Auth module (JWT, passwords, RBAC, refresh tokens, lockout)
assignee: eos-backend-engineer
parallel: no
dependencies: [TASK-02]
---
# TASK-03 — Auth module

## Description
Implement auth per docs/architecture/auth-design.md: login, refresh (rotation), logout, /me, RBAC dependency, password hashing (bcrypt≥12), account lockout persisted, refresh_token table, seeded admin bootstrap (env-based), auth event logging.

## Requirements
- JWT access 15m (HS256, JWT_SECRET env); refresh opaque 7d stored hashed; rotation + reuse detection.
- `require_role(*roles)` dependency; hierarchical.
- Bootstrap admin via ADMIN_EMAIL/ADMIN_PASSWORD; random password printed once if unset.
- Lockout counters persisted in user_account (H-8).
- CSP/security headers middleware (auth-design §7.1).

## Expected output
- backend/app/auth/*.py, backend/app/common/deps.py, backend/app/common/middleware.py

## Acceptance criteria
- [ ] Login returns access+refresh; refresh rotates; reuse revokes all.
- [ ] Protected route 401 without token; 403 wrong role.
- [ ] Lockout persists across restart (test).
- [ ] Bootstrap admin created on first run; no default passwords.
- [ ] Security headers present in responses.

## Verification method
`pytest tests/auth/ -q` (unit+integration); manual curl login/refresh.

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending