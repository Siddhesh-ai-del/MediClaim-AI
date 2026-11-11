# Acceptance Criteria — MediClaim AI

Verifiable statements per FR. Format: AC-n (FR-x) — condition → observable result.

- AC-1 (FR-1): Given a valid PDF/image bundle ≤20MB/≤10 files, when uploaded, then claim record created and processing starts within 3s; invalid files rejected with reason.
- AC-2 (FR-2): Given processing, then each file shows status transitioning queued→processing→done/failed with timestamp; failed file shows error reason.
- AC-3 (FR-3): Given a sample claim bundle, then extracted JSON contains all listed fields with ≥0.85 field-level accuracy on eval set; missing fields marked null (not hallucinated).
- AC-4 (FR-4): Given extracted fields, when user edits and saves, then value updates, "human-corrected" flag set, audit log entry created.
- AC-5 (FR-5): Given a processed claim, then risk score 0–100 displayed with confidence band; re-running yields identical score (deterministic given same input).
- AC-6 (FR-6): Given a claim with injected anomaly, then flag appears with correct type, evidence quote, severity; no false flag on clean claim (precision target).
- AC-7 (FR-7): Given ≥5 claims across ≥2 providers, then provider aggregate view shows counts, avg risk, ₹ flagged, sortable.
- AC-8 (FR-8): Given a processed claim, then recommended decision + ≥1 reason citing evidence; partial-approve includes amount.
- AC-9 (FR-9): Given a recommendation, when user overrides, then override requires reason text; decision + reason persisted in audit log.
- AC-10 (FR-10): Given any claim action, then audit log entry appended with actor, action, timestamp, payload hash; log cannot be edited via UI/API.
- AC-11 (FR-11): Given processed claims, then dashboard KPIs render and match recomputed aggregates.
- AC-12 (FR-12): Given unauthenticated request, then 401; officer cannot access manager-only views (403).
- AC-13 (NFR-1): Given 5-page bundle, then end-to-end processing ≤30s (measured, recorded).
- AC-14 (NFR-4/5): Given eval set, then extraction F1 ≥0.85 and fraud precision ≥0.80 reported with command+output in STATE.md.
- AC-15 (NFR-13): Given keyboard-only navigation, then all primary actions reachable and focus visible.