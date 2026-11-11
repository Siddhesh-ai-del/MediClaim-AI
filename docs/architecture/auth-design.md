# Auth Design — MediClaim AI

- Date: 2026-11-11
- Mode stage: software-dev Stage 3
- Related: ADR-08 (auth model), ADR-01 (FastAPI), database-schema §3.2
- NFR: NFR-8 (auth required, RBAC, secrets in env)

## 1. Model summary

- **Mechanism**: Stateless JWT (access token) + rotating refresh token. Passwords hashed with bcrypt (cost ≥12). RBAC by role claim in token. Single-tenant demo (no SSO/OAuth in MVP).
- **Roles**: `officer`, `manager`, `admin` (hierarchical: admin ⊃ manager ⊃ officer).
- **Transport**: HTTPS only; tokens in `Authorization: Bearer`.
- **Refresh token storage (MVP decision, H-1)**: stored in `localStorage` for SPA simplicity **only** under the CSP in §7.1. Hardening path before any real patient data: httpOnly Secure SameSite cookie + CSRF token. Risk-accepted for demo; logged in STATE.md approval-log.>

## 2. Token lifecycle

| Token | Lifetime | Storage (client) | Purpose |
|---|---|---|---|
| Access | 15 min | memory (React state) | API auth |
| Refresh | 7 days (sliding) | localStorage (MVP) / httpOnly cookie (hardening) | obtain new access |

- **Issue**: on login, issue access+refresh; store refresh token hash in DB (`refresh_token` table or column on user) for revocation. MVP: in-memory blocklist + DB row (see §7).
- **Refresh rotation**: each refresh issues new refresh, revokes old (reuse detection → revoke all user tokens).
- **Logout**: revoke refresh token (add to blocklist / delete DB row).
- **Expiry handling**: 401 on expired access → client refreshes transparently; if refresh invalid → redirect to login.

### JWT claims (access)
```json
{
  "sub": "<user_uuid>",
  "tenant_id": "<tenant_uuid>",
  "role": "officer",
  "email": "officer@demo.med",
  "iat": 1731312000,
  "exp": 1731312900,
  "jti": "<uuid>",          // for revocation/blacklist
  "iss": "mediclaim-ai",
  "aud": "mediclaim-api"
}
```
- Signed with HS256 using `JWT_SECRET` (env, ≥32 bytes random). RS256 optional later for multi-service (not MVP).
- Refresh token is an opaque random string (not JWT) stored hashed in DB; rotation tracked.

## 3. Password storage

- bcrypt via passlib, cost factor 12 (tunable via env `BCRYPT_ROUNDS`, min 12).
- Minimum password policy: ≥10 chars, ≥1 digit, ≥1 letter (validated with zod on frontend + Pydantic on backend).
- No plaintext ever logged. Password reset: admin-only reset in MVP (no self-service email) [ASSUMPTION]. Email-based reset deferred.
- Account lockout: 5 failed logins / 15 min → temporary lock (in-memory for MVP; Redis later). Logged.

## 4. RBAC

### Roles & permissions

| Capability | officer | manager | admin |
|---|---|---|---|
| Login / view own claims | ✅ | ✅ | ✅ |
| Create/upload claim | ✅ | ✅ | ✅ |
| Edit extracted fields | ✅ | ✅ | ✅ |
| Override recommendation | ✅ | ✅ | ✅ |
| View all claims (tenant) | ✅ (own+assigned) | ✅ (all) | ✅ |
| Provider aggregates | ❌ | ✅ | ✅ |
| Dashboard KPIs | basic | full | full |
| Audit export | ❌ | ✅ | ✅ |
| User management | ❌ | ❌ | ✅ |
| Demo reset | ❌ | ❌ | ✅ |
| Audit verify | ❌ | ❌ | ✅ |

### Enforcement
- FastAPI dependency `require_role(*roles)` checks `request.state.user.role` against allowed set; hierarchical check (`admin` passes any).
- Applied per-route via `Depends(require_role("manager"))`.
- Frontend mirrors for UX but server is authoritative (NFR-8).

### Claim ownership policy (M-18)
- `claim.submitted_by` (user_id, NOT NULL) records the creating officer.
- `claim.assigned_to` (user_id, nullable) records the officer assigned to review; manager/admin can assign/reassign.
- Officer visibility: claims where `submitted_by = self` OR `assigned_to = self`.
- Manager/admin visibility: all claims in tenant.
- Access to a claim not visible to the caller returns **404** (not 403) to avoid enumeration (M-19).
- Tests: IDOR suite asserts officer cannot read/modify another officer's unassigned claim.

## 5. Session handling (MVP)

- No server-side sessions for access token (stateless JWT).
- Refresh tokens stored in DB table `refresh_token` (id, user_id, token_hash, issued_at, expires_at, revoked_at, replaced_by) for rotation/reuse detection.
- Concurrency: a user may have multiple active refresh tokens (multiple devices) up to 5; oldest revoked on overflow [ASSUMPTION].

## 7.1 CSP & security headers (H-1, H-9)

Exact header set emitted by backend middleware (and mirrored in Next.js `next.config.js` headers):

```
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' https://api.openai.com; object-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Strict-Transport-Security: max-age=63072000; includeSubDomains
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

- No `dangerouslySetInnerHTML` in frontend; React default escaping only.
- No third-party scripts in MVP.
- CSP verified by automated header checks in CI (M-12).

## 7.2 DB-backed revocation & lockout (H-8)
- Revocation is authoritative in `refresh_token` table (`revoked_at`). Logout sets `revoked_at = now()`.
- Account lockout counters stored in `user_account.failed_login_count` + `locked_until` (persisted), not in-memory. Survives restart.
- Reuse detection: if a revoked refresh token is presented, revoke all tokens for that user.

## 7.3 Seeded credentials (H-4)
- Bootstrap admin created on first startup only if no admin exists.
- Credentials sourced from env `ADMIN_EMAIL` + `ADMIN_PASSWORD` (placeholders in `.env.example` only).
- If `ADMIN_PASSWORD` unset, generate a cryptographically random password, print once to stdout (never log to file), and require change on first login.
- Password policy enforced; default passwords forbidden (reject `admin`, `password`, etc.).
- `DEMO_MODE`-seeded demo users (`officer@demo`, `manager@demo`) created only when `DEMO_MODE=true` AND `APP_ENV != production`; documented in deployment.

## 7.4 Auth event audit (M-7)
- Login success/failure, lockout, token reuse, logout recorded as security audit events (actor, IP, UA, timestamp) in `audit_event` (separate from claim audit log) or structured security log.

### refresh_token table (addition to schema)
```sql
CREATE TABLE refresh_token (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      uuid NOT NULL REFERENCES user_account(id) ON DELETE CASCADE,
  token_hash   text NOT NULL UNIQUE,   -- SHA-256 of opaque token
  issued_at    timestamptz NOT NULL DEFAULT now(),
  expires_at   timestamptz NOT NULL,
  revoked_at   timestamptz,
  replaced_by  uuid REFERENCES refresh_token(id),
  user_agent   text,
  ip_address   inet
);
CREATE INDEX idx_rt_user ON refresh_token(user_id);
```

## 6. Multi-tenant posture (single-tenant demo)

- MVP: one tenant row seeded; all users/claims belong to it. `tenant_id` in JWT and enforced in every query (filter by `tenant_id` from token, never from request body) to prevent cross-tenant access if data ever added.
- No RLS in MVP; application-level scoping. Documented migration to RLS for multi-tenant production (ADR-09).
- Assumption: no tenant self-provisioning; admin seeds users.

## 7. Security controls

- CORS: allow only frontend origin(s) from env `CORS_ORIGINS`.
- CSRF: not applicable for bearer-token SPA (no cookies) in MVP; if cookies used later, enable CSRF tokens.
- Rate limiting: slowapi or custom middleware (see api-contracts §7).
- Security headers: HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy via middleware.
- Input validation: Pydantic v2 at boundary; file type/size enforced server-side (NFR-10).
- Secrets: `JWT_SECRET`, `DATABASE_URL`, `OPENAI_API_KEY` from env only; never committed. `.env.example` committed, `.env` gitignored.
- Token storage XSS risk: localStorage is XSS-exposed; mitigation: strict CSP, no third-party scripts, sanitize all rendered HTML. Hardening path: httpOnly cookie + CSRF (documented, not MVP) [ASSUMPTION].

## 8. Failure modes

| Failure | Behavior |
|---|---|
| Expired access token | 401 `unauthorized`; client refreshes |
| Invalid refresh token | 401; force re-login |
| Refresh reuse detected | revoke all user tokens; 401 |
| Account locked | 423 Locked with retry-after |
| Insufficient role | 403 `forbidden` |
| Missing tenant in token | 401 (malformed) |

## 9. Testability

- Unit tests: password hash/verify, JWT encode/decode + expiry, role hierarchy checks, refresh rotation/reuse detection.
- Integration tests: login flow, protected route 401/403, token refresh, logout revocation.
- Security tests: brute-force lockout, SQL injection on login, token tampering rejection.

## 10. Assumptions (labeled)

- [ASSUMPTION] No SSO/OAuth/SAML in MVP; email+password only.
- [ASSUMPTION] No MFA in MVP; documented as P1.
- [ASSUMPTION] No self-service password reset; admin resets.
- [ASSUMPTION] Refresh token in localStorage for MVP simplicity; httpOnly cookie is the hardening path.
