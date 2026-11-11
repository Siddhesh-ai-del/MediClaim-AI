# User Personas — MediClaim AI

## P1 — Claims Officer (Primary buyer user)
- Role: Processes 80–150 claims/day at a TPA or insurer claims desk.
- Pain: Manual data entry from scanned bills; inconsistent fraud judgment; pressure to clear backlog; fear of approving fraud.
- Goal: Clear claims faster with confidence; reduce manual entry; have defensible reasons for reject/partial.
- Tech comfort: Web apps, Excel; not ML. Needs plain-language explanations, not model internals.

## P2 — Claims Manager / Head of Claims (Decision maker / buyer)
- Role: Owns claims cost ratio, fraud loss, TAT.
- Pain: No visibility into fraud patterns by provider/hospital; can't quantify leakage; vendor tools are black boxes.
- Goal: Reduce claims ratio 2–4 points; audit trail for IRDAI; ROI in <6 months.
- Buys on: explainability, measurable fraud catch rate, integration roadmap.

## P3 — Hospital Billing Staff (Indirect user)
- Role: Submits claims; wants faster, fewer rejections.
- Pain: Rejections due to missing fields / coding errors; rework.
- Goal: Clean claim submission first time; clear feedback on why rejected.

## P4 — Patient / Policyholder (End beneficiary)
- Role: Insured individual.
- Pain: Delayed settlements; opaque rejections.
- Goal: Faster settlement; transparent status. [ASSUMPTION] patient-facing surface is out of MVP scope; included for roadmap.

## Developer assumptions (labeled)
- [ASSUMPTION] Claims officers will upload full claim bundles (not just bills) — if only bills available, extraction coverage drops.
- [ASSUMPTION] Insurers will share historical labeled fraud data for model training — likely not for MVP; we use synthetic + public datasets and rule-based detection first.
- [ASSUMPTION] English + Hindi OCR covers 90% of our demo hospitals; regional-language bills deferred.