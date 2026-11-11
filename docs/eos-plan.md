# Implementation Plan — MediClaim AI

- Mode: software-dev Stage 4
- Date: 2026-11-11
- Related: product/*, docs/architecture/*, docs/adr/ADR-01..ADR-10, docs/security/design-review.md

## Objective & success definition
Build MediClaim AI MVP (web SaaS) per product-brief.md: ingest claim bundles, OCR+LLM extract, fraud score with explainable flags, adjudicate with reasons, immutable audit trail, dashboard. Success = primary workflow completes end-to-end on synthetic data within 30s per 5-page bundle; acceptance criteria AC-1..AC-15 green; 80% coverage on critical paths; live demo URL for pitch (30 Nov 2026).

## Milestones

### M1 — Foundation
- Tasks: TASK-01, TASK-02, TASK-03, TASK-04, TASK-05, TASK-06
- Dependencies: none → TASK-01 first; TASK-02/04/05/06 after TASK-01; TASK-03 after TASK-02
- Acceptance criteria: repo builds; migrations apply; auth login/refresh works; files stored with UUID names; job runner processes a dummy job.
- Tests: unit (auth, config), integration (DB migration, storage round-trip, job execution).
- Deliverables: backend/ + frontend/ skeletons, Dockerfile, .env.example, Alembic migrations, seed script.
- Time budget: 2 weeks.

### M2 — Core functionality
- Tasks: TASK-07, TASK-08, TASK-09, TASK-10, TASK-11, TASK-12, TASK-13
- Dependencies: M1 complete.
- Acceptance criteria: upload→OCR→extract→score→adjudicate→audit completes on synthetic claim; extraction F1≥0.85; fraud precision≥0.80 on eval set.
- Tests: unit (rules, scoring, decision, hash chain), integration (full pipeline on synthetic claims).
- Deliverables: ingestion, OCR, extraction, fraud, adjudication, audit, reporting modules.
- Time budget: 3 weeks.

### M3 — UI
- Tasks: TASK-14, TASK-15, TASK-16, TASK-17, TASK-18, TASK-19
- Dependencies: M2 (API contracts stable); TASK-14 before others.
- Acceptance criteria: officer can upload, review/edit extraction, see score/flags, adjudicate; manager sees dashboard/providers; admin manages users.
- Tests: component tests (RTL), a11y basics.
- Deliverables: Next.js pages, components, API client.
- Time budget: 2 weeks.

### M4 — Integration
- Tasks: TASK-20, TASK-21
- Dependencies: M2 + M3.
- Acceptance criteria: E2E primary workflow passes; exports work; polling status.
- Tests: Playwright E2E (e2e-runner).
- Deliverables: wired app, E2E suite.
- Time budget: 1 week.

### M5 — Security & reliability
- Tasks: TASK-22, TASK-23, TASK-24
- Dependencies: M4.
- Acceptance criteria: security blockers (H-*, M-*) closed or risk-accepted; coverage ≥80% critical; perf ≤30s/5-page bundle; a11y keyboard.
- Tests: security test suite, load test, a11y.
- Deliverables: hardened build, coverage report, perf report.
- Time budget: 1 week.

### M6 — Release prep
- Tasks: TASK-25, TASK-26, TASK-27
- Dependencies: M5.
- Acceptance criteria: demo data seeded; docs/release checklist; eval harness report; deployed live URL.
- Tests: fresh-install verification, release checklist.
- Deliverables: deployed demo, release/ docs, eval report.
- Time budget: 1 week.

## Task board summary
See `.eos/tasks/TASK-*.md`. Parallel sets: M1 {TASK-02, TASK-04, TASK-05, TASK-06} (after TASK-01); M2 {TASK-08, TASK-12} (after their deps); M3 {TASK-15, TASK-16, TASK-17, TASK-18} (after TASK-14); M6 {TASK-25, TASK-26, TASK-27}.

## Risks
| Risk | Likelihood | Mitigation | Owner |
|---|---|---|---|
| OCR accuracy on real Indian bills | Medium | Eval harness; fallback chain; human review gate | extraction owner |
| No real labeled fraud data | High | Synthetic data + injected anomalies; honest labeling (R09) | fraud owner |
| Scope creep | High | Scope fence binding (S3); approval for expansion | PM |
| PaddleOCR install on Py 3.14 | Medium | Verify in TASK-01; fallback Tesseract+LLM | backend |
| Student time constraints | High | Prioritize P0 ACs; defer P1/P2 | PM |
| Medical data privacy perception | Medium | Synthetic-only demo; DPDP posture doc | security |

## Scope fence
Out of scope (binding until approved): live insurer integration, real patient data, regulatory certification, payments, mobile app, multi-tenancy, multi-language OCR beyond EN+HI, SSE push (P1), PDF reports (P2).

## Approval record
- 2026-11-11 — user approved scope: "Approve scope" (Stage 1).
- 2026-11-11 — user approved research: "Approve" (Stage 2).
- 2026-11-11 — user approved architecture: "Approve" (Stage 3).
- Stage 4 plan pending user approval.