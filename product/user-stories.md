# User Stories — MediClaim AI

## Epic E1 — Claim ingestion
- US-1.1 As a claims officer, I upload a claim bundle (bill + discharge summary + prescription + diagnostics) as PDF/images so the system processes it. AC: FR-1, AC-1.
- US-1.2 As a claims officer, I see upload progress and per-file status so I know what succeeded/failed. AC: FR-2, AC-2.

## Epic E2 — Extraction
- US-2.1 As a claims officer, I see extracted fields (patient, provider, policy, dates, procedures, ICD codes, line items, totals) so I don't retype. AC: FR-3, AC-3.
- US-2.2 As a claims officer, I can correct extracted fields so errors don't propagate. AC: FR-4, AC-4.

## Epic E3 — Fraud detection
- US-3.1 As a claims officer, I see a fraud risk score (0–100) per claim so I prioritize review. AC: FR-5, AC-5.
- US-3.2 As a claims officer, I see each flagged anomaly with type, evidence, and severity so I understand why. AC: FR-6, AC-6.
- US-3.3 As a claims manager, I see provider-level fraud aggregates so I spot bad actors. AC: FR-7, AC-7.

## Epic E4 — Adjudication
- US-4.1 As a claims officer, I get a recommended decision (approve / reject / partial) with reasons so I act quickly. AC: FR-8, AC-8.
- US-4.2 As a claims officer, I override the recommendation and record my reason so audit trail is complete. AC: FR-9, AC-9.

## Epic E5 — Audit & reporting
- US-5.1 As a claims manager, I export an audit log of all decisions with evidence so I satisfy IRDAI/audit. AC: FR-10, AC-10.
- US-5.2 As a claims manager, I see dashboard KPIs (claims processed, fraud caught, ₹ saved, TAT) so I measure ROI. AC: FR-11, AC-11.