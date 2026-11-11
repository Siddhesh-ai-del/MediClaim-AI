---
id: TASK-14
title: Frontend scaffolding
assignee: eos-frontend-engineer
parallel: no
dependencies: [TASK-01]
---
# TASK-14 — Frontend scaffolding

## Description
Set up Next.js 15 app: auth pages (login), layout, navigation, API client (typed from OpenAPI), auth context (token storage in memory + localStorage refresh), protected routes, security headers in next.config.js.

## Requirements
- API client generated from committed OpenAPI spec (or hand-typed).
- Auth context: access token in memory, refresh in localStorage (per auth-design §7.1 CSP).
- Protected route wrapper; role-based UI gating (server authoritative).
- CSP + security headers in next.config.js (H-1/H-9).

## Expected output
- frontend/app/*, frontend/lib/api.ts, frontend/lib/auth.tsx, frontend/next.config.js

## Acceptance criteria
- [ ] `npm run build` succeeds.
- [ ] Login flow works against backend.
- [ ] Protected routes redirect unauthed users.
- [ ] Security headers present.

## Verification method
`cd frontend && npm run lint && npm run build`; manual login.

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending