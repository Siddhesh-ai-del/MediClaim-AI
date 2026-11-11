# DPDP Posture — MediClaim AI

Resolves security review blocker **M-9**. Applies to the single-tenant demo; escalates to CRITICAL if real patient data is introduced.

## 1. Data classification
- Demo data: **synthetic only**. No real patient PII. NFR-7.
- Production (future): health data = sensitive personal data under DPDP Act 2023; requires DPA, consent, purpose limitation, retention/erasure.

## 2. Principles (DPDP-aligned)
- **Consent:** In production, explicit consent captured at policy purchase / claim submission; purpose = claims processing & fraud detection.
- **Purpose limitation:** Data used only for claims adjudication and fraud detection; no secondary use without consent.
- **Data minimization:** Extract only fields needed (FR-3); no full document retention beyond configured window.
- **Storage limitation:** Retention policy — claims 7 years (IRDAI record-keeping), audit log 7 years, raw uploads 90 days then purged; configurable per tenant.
- **Accuracy:** Human correction path (FR-4) + audit trail.
- **Security safeguards:** Encryption in transit (TLS 1.2+) and at rest (managed Postgres + volume); access control (RBAC); audit logging.
- **Data principal rights:** Access, correction, erasure (subject to statutory retention); erasure procedure pseudonymizes patient identifiers in audit payload (M-10) rather than deleting audit entries.
- **Breach notification:** Documented procedure to notify Data Protection Board + affected principals within 72 hours.

## 3. Demo posture (current)
- All data synthetic; no consent needed for demo.
- Runtime guard refuses non-synthetic data (extraction-contract §6).
- DPDP posture doc published for investor/regulator credibility.

## 4. Real-data escalation
If real data is introduced, the following become CRITICAL and must be closed first: C-1, H-1, H-10, H-11, M-9, M-10. Logged approval required in STATE.md approval-log.