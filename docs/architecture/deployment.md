# Deployment Architecture — MediClaim AI

- Date: 2026-11-11
- Mode stage: software-dev Stage 3
- Related: ADR-06 (hosting), ADR-01/02/03

## 1. Topology

```
Users ──HTTPS──► Vercel (Next.js frontend, hobby)
                    │  NEXT_PUBLIC_API_URL
                    ▼
            Render Web Service (FastAPI, Docker, starter $7/mo)
                    │
                    ├──► Render Managed Postgres (starter $6/mo)
                    ├──► Render Disk (uploaded files, 1GB+)
                    ├──► OpenAI API (external)
                    └──► (optional) Sentry
```

- Frontend and backend are separate deployables; CORS configured for Vercel origin.
- Backend long-lived ASGI process (uvicorn) — required for OCR jobs and process pool (ADR-06 rejects serverless).

## 2. Environments

| Env | Purpose | Backend | DB | Frontend |
|---|---|---|---|---|
| local | dev | uvicorn reload | docker postgres / sqlite | next dev |
| staging | integration | Render (optional) | Render (optional) | Vercel preview |
| production (demo) | pitch/demo | Render starter | Render managed | Vercel hobby |

MVP ships local + production (demo). Staging optional [ASSUMPTION].

## 3. Build & runtime

### Backend Dockerfile (planned)
- Base: `python:3.12-slim` (or 3.14 if available; ADR-01 says 3.14 — verify at build [R02]).
- Install system deps: `tesseract-ocr`, `tesseract-ocr-hin`, `libgl1`, `libglib2.0-0` (PaddleOCR), `poppler-utils` (pdf2image).
- `pip install -r requirements.txt` (pinned).
- Copy app; `alembic upgrade head` on startup (entrypoint); `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- Non-root user; healthcheck on `/healthz`.

### Frontend
- Next.js build on Vercel; env `NEXT_PUBLIC_API_URL` set in Vercel project settings.

## 4. Environment variables

### Backend (Render)
| Var | Required | Notes |
|---|---|---|
| `DATABASE_URL` | yes | Render-provided Postgres URL (async driver: `postgresql+asyncpg://...`) |
| `JWT_SECRET` | yes | ≥32 bytes random; rotate invalidates sessions |
| `BCRYPT_ROUNDS` | no | default 12 |
| `OPENAI_API_KEY` | yes (if LLM enabled) | secret |
| `LLM_PROVIDER` | no | `openai` (default) |
| `LLM_MODEL` | no | `gpt-4o-mini` |
| `OCR_PRIMARY` | no | `paddleocr` (default) / `tesseract` |
| `OCR_FALLBACK` | no | `tesseract` |
| `CLOUD_OCR_ENABLED` | no | `false` default |
| `CORS_ORIGINS` | yes | Vercel URL(s), comma-separated |
| `STORAGE_PATH` | yes | `/var/data/uploads` (Render disk mount) |
| `STORAGE_BACKEND` | no | `local` (default) / `s3` |
| `SENTRY_DSN` | no | optional |
| `DEMO_MODE` | no | `false` default; enables demo reset endpoint (H-7) |
| `APP_ENV` | no | `production` in prod; `demo`/`dev` otherwise |
| `ADMIN_EMAIL` | yes (first boot) | bootstrap admin email (H-4) |
| `ADMIN_PASSWORD` | no | if unset, random password printed once (H-4) |
| `DOCS_ENABLED` | no | `false` in production (M-5) |
| `LOG_LEVEL` | no | `info` |
| `MAX_UPLOAD_MB` | no | 20 |
| `MAX_FILES_PER_CLAIM` | no | 10 |

### Frontend (Vercel)
| Var | Required | Notes |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | yes | Render backend URL |
| `NEXT_PUBLIC_APP_ENV` | no | `production` |

## 5. Secrets management

- Secrets only in Render/Vercel env settings and local `.env` (gitignored). `.env.example` committed with placeholders.
- No secrets in repo, Docker image, or client bundle. `NEXT_PUBLIC_*` only non-secret config.
- Rotation procedure: update env var → redeploy; document in runbook. JWT_SECRET rotation logs out all users.

## 6. CI/CD

- Repo (when created) on GitHub. [ASSUMPTION] GitHub Actions:
  - On PR: lint (ruff, eslint), typecheck (mypy/pyright, tsc), tests (pytest, jest), security audit (`ecc:security-audit` or gitleaks).
  - On merge to main: build Docker image, push to Render (deploy hook) and Vercel (auto).
- Database migrations: `alembic upgrade head` in Render start command; failed migration blocks deploy (Render keeps previous).
- Coverage gate: pytest `--cov-fail-under=80` on critical modules (extraction, fraud, adjudication, audit, auth).

## 6.1 Security headers & middleware (H-1, H-9)
- Backend middleware emits the exact header set in auth-design §7.1 (CSP, HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy).
- Frontend `next.config.js` sets matching headers for static assets.
- Verified by automated header checks in CI (M-12).

## 6.2 Seeded credentials & demo reset (H-4, H-7)
- Bootstrap admin via `ADMIN_EMAIL`/`ADMIN_PASSWORD` (see auth-design §7.3).
- `POST /admin/demo/reset`: refused unless `DEMO_MODE=true` AND `APP_ENV != production`; requires admin role + confirm token; audit event written. Integration test asserts 404 when disabled.
- Encryption at rest (M-8): Render managed Postgres encrypted at rest (verify + document); file volume encryption status documented; app-level encryption not required for synthetic demo.

## 7. Observability

- Logs: Render captures stdout; structured JSON. Retention ~7 days on starter (export if needed).
- Health: `/healthz`, `/readyz` polled by Render (restart on failure).
- Error tracking: Sentry (optional) with PII scrubbing.
- Uptime: UptimeRobot (free) on `/healthz` + frontend.
- Audit log is business source of truth; not a substitute for app logs.

## 8. Backups & recovery

- Render managed Postgres: daily automated backups (7-day retention on starter); manual backup before demo via `pg_dump` to local + cloud drive.
- File storage: Render disk is NOT backed up automatically [ASSUMPTION] → backup uploads via `rsync`/script before pitch; for production migrate to S3 with versioning.
- Recovery: restore DB from backup; re-point `DATABASE_URL`; redeploy; verify `/readyz` + audit verify endpoint.
- RTO target: 4 hours; RPO: 24 hours (acceptable for demo).

## 9. Scaling notes (future)

- Horizontal: move job processing to Celery+Redis; add replicas behind Render load balancer. Not MVP.
- OCR CPU: Render starter has limited CPU; if OCR slower than 30s, upgrade instance or move OCR to a worker dyno.
- DB: upgrade Render Postgres tier; add read replica for reporting if needed.

## 10. Assumptions (labeled)

- [ASSUMPTION] GitHub + GitHub Actions for CI; if team uses another, adapt.
- [ASSUMPTION] Render disk backups manual; production would use S3.
- [ASSUMPTION] Python 3.12 in Docker if 3.14 image unavailable (verify at build).
- [ASSUMPTION] No CDN/WAF in MVP; Vercel provides edge for frontend.
