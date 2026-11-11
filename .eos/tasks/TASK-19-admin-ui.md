---
id: TASK-19
title: Admin UI
assignee: eos-frontend-engineer
parallel: yes
dependencies: [TASK-14, TASK-03]
---
# TASK-19 — Admin UI

## Description
Build admin pages: user list/create/edit/deactivate, usage stats, demo reset button (guarded).

## Requirements
- Calls /admin/* (admin role only).
- Demo reset requires confirm token; disabled unless DEMO_MODE.

## Expected output
- frontend/app/admin/* 

## Acceptance criteria
- [ ] Admin can manage users.
- [ ] Non-admin cannot access (redirect/403).

## Verification method
`npm run test`; manual walkthrough.

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending