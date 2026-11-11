# Non-Functional Requirements — MediClaim AI

## Performance
- NFR-1 Extraction + scoring for a 5-page claim bundle completes in < 30s on demo hardware (P0).
- NFR-2 Dashboard first paint < 2s; claim detail < 1s after data load (P1).
- NFR-3 System handles 50 concurrent claim uploads without failure (P1; demo load test).

## Accuracy
- NFR-4 Field extraction F1 ≥ 0.85 on our synthetic eval set (P0).
- NFR-5 Fraud rule detection precision ≥ 0.80 on synthetic labeled set (P0; recall target ≥ 0.70).
- NFR-6 Every automated decision includes ≥1 human-readable reason (P0, explainability).

## Security & privacy
- NFR-7 No real patient data in demo; synthetic data only. DPDP-aligned: consent, purpose limitation, retention policy documented (P0).
- NFR-8 Auth required for all endpoints; role-based access; secrets in env vars; no hardcoded secrets (P0).
- NFR-9 Audit log immutable (append-only) (P0).
- NFR-10 Input validation at API boundary (zod); file type/size enforced server-side (P0).

## Reliability
- NFR-11 Failed jobs retryable; partial failures don't corrupt claim state (P0).
- NFR-12 Graceful degradation: if OCR/LLM unavailable, queue and notify (P1).

## Usability & accessibility
- NFR-13 Keyboard navigable; visible focus; labeled inputs; WCAG 2.2 AA basics (S8).
- NFR-14 New claims officer completes first claim review in < 5 min without training (product validation).

## Maintainability
- NFR-15 80% test coverage on critical paths (extraction, scoring, adjudication) (R05).
- NFR-16 ADR for every level-one tech choice (Stage 2/3).