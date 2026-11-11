# ADR-08 — Auth model

- Status: accepted
- Date: 2026-11-11
- Mode stage: Stage 3

## Context
We need authentication and role-based access for officers/managers/admins in a single-tenant demo, buildable by a 4-student team, with no real patient data and DPDP-aligned posture. Backend is FastAPI (ADR-01).

## Problem
Which auth mechanism (session cookies vs JWT vs OAuth/SSO)?

## Considered alternatives
1. **Stateless JWT (access 15m) + rotating refresh token (7d) + bcrypt passwords + RBAC** — self-contained, scales horizontally, simple for SPA, no server session store. Con: token revocation needs DB-backed refresh tokens; XSS risk if stored in localStorage (mitigated by CSP + hardening path).
2. **Server-side sessions (cookie + Redis/DB)** — easy revocation, CSRF protection built-in, but adds Redis/DB session table and stateful infra; more moving parts for MVP.
3. **OAuth2/OIDC + SSO (Auth0/Clerk)** — offloads security and gives SSO, but external dependency/cost, overkill for demo tenant, and data-residency questions.

## Decision
Stateless JWT access + rotating opaque refresh token (DB-backed) + bcrypt (cost ≥12) + role-based access control (officer/manager/admin). Single-tenant demo; no SSO in MVP. See auth-design.md.

## Consequences
- Must implement auth ourselves (FastAPI deps) — acceptable, well-scoped.
- Need refresh_token table + rotation/reuse detection.
- XSS mitigation relies on CSP + no third-party scripts; hardening path to httpOnly cookie documented.
- Multi-tenant/SSO is a future migration, not MVP.
