# Project Brief — MediClaim AI

> Target competition: Startup Expo 2027, IIT Guwahati (UDGAM). Pitch deck deadline 30 Nov 2026; virtual pitch 3–10 Dec 2026; finals 24 Jan 2027. Team of 4.

## Objective
Build MediClaim AI — an AI platform that ingests Indian health-insurance claims (bills, discharge summaries, prescriptions, diagnostics), extracts structured data, detects fraud/anomalies, and auto-adjudicates with explainable reasons — sold as SaaS to health insurers and TPAs, with a fraud-recovery revenue share.

## Problem
Health-insurance fraud and claims leakage in India are estimated at 10–15% of claims value. Review is manual, slow, inconsistent, and expensive; TPAs are overwhelmed, genuine claims get delayed, and insurers bleed money. [ASSUMPTION] exact fraud rate for the Indian market is taken from industry reports; not independently verified by us.

## In scope (scope fence)
- Claim ingestion (PDF/image upload, batch)
- OCR + LLM structured extraction (patient, provider, procedures, ICD codes, amounts, dates)
- Fraud/anomaly detection (upcoding, phantom billing, unbundling, duplicates, inflated charges, diagnosis–procedure mismatch, provider outliers)
- Auto-adjudication suggestion (approve / reject / partial) with explainable reasons
- Claims-officer dashboard with risk score, explanations, audit trail
- Synthetic/public dataset demo (no real patient data)
- Web app only

## Out of scope (changes require logged approval)
- Live integration with insurer/TPA core systems
- Real patient data / production deployment
- Regulatory certification (IRDAI sandbox approval)
- Payment processing / settlement
- Mobile native app
- Multi-language OCR beyond English + Hindi [ASSUMPTION]

## Constraints
- Time: launch-ready demo by 30 Nov 2026 (pitch deck); hard deadline 24 Jan 2027
- Team: 4 members (AI/ML+CV, full-stack, health & finance domain)
- Environment: web-first, cloud-hosted demo; offline-capable not required
- Non-negotiables: no real patient data in demo (synthetic only); DPDP Act compliance posture; explainability for every decision (R09)
- DPIIT: not registered yet [ASSUMPTION] — can apply during build; not blocking demo

## Success definition
A working demo where a claims officer uploads a claim bundle and within seconds sees extracted fields, a fraud risk score, flagged anomalies with explanations, and a recommended adjudication decision — plus a dashboard showing aggregate fraud metrics. Primary workflow completes end-to-end without manual intervention. Acceptance criteria in `acceptance-criteria.md` all green.

## EOS state header
```yaml
mode: software-dev
phase: 1
updated: 2026-11-11
tasks:
  completed: 0
  pending: 0
  blocked: 0
verification: []
approval-log: []
next-action: "Stage 1 product discovery drafted; awaiting user scope approval before Stage 2."
context:
  - product/product-brief.md
```