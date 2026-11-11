# Functional Requirements — MediClaim AI

Numbered, each testable. Priority: P0 = MVP must, P1 = should, P2 = could.

## Ingestion
- FR-1 (P0) System accepts claim bundle upload (PDF/PNG/JPEG, max 20MB, up to 10 files) via web UI.
- FR-2 (P0) System shows per-file upload status (queued/processing/done/failed) with error reason.
- FR-3 (P0) System extracts structured fields: patient name/age/gender, policy no., provider name + ID, admission/discharge dates, claim amount, line items (description, qty, unit price, total), ICD-10 codes if present, prescribed drugs.

## Review & correction
- FR-4 (P0) User can view and edit any extracted field; edits are saved and flagged as "human-corrected".
- FR-5 (P0) System computes a fraud risk score 0–100 per claim with a confidence band.

## Fraud detection
- FR-6 (P0) System flags anomalies with type, evidence (quoted text/field), severity (low/med/high), and rule/model source. Types: upcoding, phantom billing, unbundling, duplicate claim, inflated charge vs tariff, diagnosis–procedure mismatch, provider outlier.
- FR-7 (P1) System aggregates fraud metrics by provider (count, avg risk, ₹ flagged) over a selectable window.

## Adjudication
- FR-8 (P0) System recommends a decision (approve / reject / partial-approve with amount) with ≥1 reason citing evidence.
- FR-9 (P0) User can override recommendation; override reason is mandatory and logged.

## Audit & reporting
- FR-10 (P0) System maintains an immutable audit log per claim: uploads, extraction, score, flags, recommendation, human actions, timestamps, user id.
- FR-11 (P1) Dashboard shows KPIs: claims processed, fraud flagged count, ₹ at risk, avg TAT, approval/reject/partial rates.

## Auth & tenancy
- FR-12 (P0) User authentication (email+password, role-based: officer/manager/admin) for the demo tenant. [ASSUMPTION] single-tenant demo; multi-tenancy deferred.
- FR-13 (P1) Admin can manage users and view usage.

## Out of scope (not in MVP)
- Live insurer API integration, real patient data, mobile app, payments, regulatory filing.