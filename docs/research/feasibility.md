# Research & Feasibility — MediClaim AI

- Date: 2026-11-11
- Mode stage: Stage 2 (software-dev)
- Decision informed: tech stack, OCR/LLM choice, hosting, fraud approach, data strategy.

## Question (so-what test)
Can a 4-student team build a credible, demo-able AI claims-fraud platform by 30 Nov 2026, and which stack minimizes risk/cost while remaining defensible to investors?

## Sub-questions & findings

### 1. Is there a real, quantified market problem?
- Yes. Health insurance fraud/leakage in India ~10–15% of claims value (industry reports; [UNVERIFIED] exact figure not independently verified by us).
- IRDAI Insurance Fraud Monitoring Framework Guidelines 2025 (effective 01 Apr 2026) mandate insurers/TPAs to deploy fraud detection, Red Flag Indicators, Fraud Monitoring Units — creating a regulatory tailwind and a buyer with budget.
- NHCX (National Health Claims Exchange) + ABDM/ABHA standardize FHIR-based e-claims → machine-readable claims become available; AI adjudication aligns with this direction.
- BCG: AI for automated checks, anomaly scoring, ICD mapping, fraud prediction is explicitly recommended for Indian health insurance.
- [Cited] IRDAI circular 09 Oct 2025; NHCX sandbox sbxhcx.abdm.gov.in; ABDM developer docs.

### 2. Can we get data to build/train on?
- Real labeled fraud data: unlikely for MVP (insurers won't share). [ASSUMPTION]
- Mitigation: synthetic claim generator with injected anomalies (upcoding, phantom billing, unbundling, duplicates, inflated charges, dx-procedure mismatch, provider outliers) + public/sample claim forms. Demo runs on synthetic data; labeled "synthetic" (R09).
- NHCX FHIR profiles give us a real schema to mirror → credible data model.

### 3. OCR feasibility for Indian medical bills (English + Hindi)?
- Tesseract 5.5 (installed) with `hin+eng` handles Devanagari at ~1% CER on clean text but struggles with noisy phone photos and mixed-script; digits read better with English model paired.
- PaddleOCR (PP-OCR) better accuracy on Indian docs; self-hosted, free; needs GPU/CPU; not currently installed (verify install).
- Compact multimodal LLMs (Qwen2.5-VL, InternVL, Phi-4 MM) significantly outperform classical/neural OCR on noisy clinical docs (CER 0.03–0.04 vs 0.11–0.19) but cost more compute.
- Cloud OCR (Google Document AI / Azure) highest accuracy on tables/layout but per-page cost (~$1.50/1000 pages) and data-residency conversation.
- Decision: PaddleOCR primary + Tesseract fallback (free, self-hosted, privacy-friendly); optional cloud OCR for hard cases. See ADR-04.

### 4. LLM/extraction feasibility?
- LLM-based structured extraction from OCR text is mature and cheap (GPT-4o-mini / Claude Haiku ~ cents per claim).
- Privacy: DPDP Act + medical data sensitivity → for production, on-prem/self-hosted model preferred; for MVP demo on synthetic data, API is acceptable with documented migration path.
- Decision: OpenAI GPT-4o-mini for MVP extraction (cost/accuracy), abstracted behind an interface to swap to self-hosted (Qwen) later. See ADR-05.

### 5. Fraud detection approach?
- Rule-based Red Flag Indicators (IRDAI-aligned) + statistical anomaly (provider outlier, amount z-score, duplicate detection) is credible, explainable, and buildable in 5 months.
- ML classifier (logistic/XGBoost) on synthetic labeled data adds lift but needs careful eval; keep as enhancement, not dependency for MVP.
- Explainability mandatory (NFR-6): every flag cites type + evidence + severity.
- Decision: rules + stats first; ML classifier as P1. See ADR-07.

### 6. Stack & hosting?
- Backend: FastAPI (Python) — team knows Python, async, Pydantic; great for OCR/ML integration. Installed v0.141.
- Frontend: Next.js + React + Tailwind (team full-stack) — Vercel hobby free for demo.
- DB: PostgreSQL (Render/Neon) — relational fits claims; pgvector optional.
- Hosting: Render starter ($7/mo) for FastAPI + managed Postgres ($6/mo) ≈ $13/mo; Vercel hobby for frontend. Fits student budget.
- See ADR-01/02/03/06.

### 7. Regulatory/compliance posture?
- DPDP Act: consent, purpose limitation, retention; document in architecture. Demo uses synthetic data → no real PII.
- IRDAI Fraud Monitoring Framework 2025: position MediClaim AI as a "Red Flag Indicator engine + Fraud Monitoring Unit support tool" — aligns with mandatory insurer obligations (effective Apr 2026) → strong buyer narrative.
- NHCX/FHIR: mirror e-claim schema → integration-ready roadmap; credible to investors.

### 8. Feasibility verdict
- Feasible for a 4-student team in 5 months: yes, if scope held to MVP (FR-1..FR-12 P0, P1 deferred where marked).
- Biggest risks: (a) OCR accuracy on real Indian bills, (b) no real labeled fraud data → synthetic-only demo must be honestly labeled, (c) medical-data privacy perception → keep demo synthetic + document DPDP posture, (d) scope creep.
- Mitigations recorded in risk table (Stage 4).

## Alternatives discipline summary
Each level-one choice compared ≥2 options in ADRs under docs/adr/.

## Sources (accessed 2026-11-11)
- IRDAI Insurance Fraud Monitoring Framework Guidelines 2025 (irdai.gov.in)
- NHCX / ABDM developer docs (docs.abdm.gov.in, sbxhcx.abdm.gov.in)
- BCG "Rebuilding Trust: Combating Fraud, Waste, and Abuse in India's Health Insurance Ecosystem"
- ACL Anthology 2026: compact multimodal LLMs vs OCR on noisy Indian clinical docs
- MindT best Indian-language OCR guide 2026
- IDPA / PaliGemma bilingual medical record digitization (IET 2025)
- Vercel/Render/Railway pricing 2026
- Self-hosted OCR cost analysis 2026
- DocsAPI multilingual OCR benchmark 2026