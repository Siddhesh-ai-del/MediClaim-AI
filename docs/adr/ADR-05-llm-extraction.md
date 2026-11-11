# ADR-05 — LLM for structured extraction

- Status: accepted
- Date: 2026-11-11
- Mode stage: Stage 2/3

## Context
OCR text → structured claim JSON (patient, provider, procedures, ICD, line items, totals).

## Problem
Which LLM and deployment?

## Considered alternatives
1. **OpenAI GPT-4o-mini (API)** — cheap, accurate, fast, JSON mode; data leaves perimeter (acceptable for synthetic demo).
2. **Anthropic Claude Haiku (API)** — comparable; slightly different cost/quality.
3. **Self-hosted Qwen2.5-VL / InternVL (on-prem)** — privacy-preserving, aligns with DPDP/medical data; needs GPU (we have one) but ops burden and slower iteration.

## Decision
GPT-4o-mini via API for MVP, abstracted behind an `Extractor` interface so we can swap to a self-hosted model (Qwen) for production/on-prem without touching callers. Document the migration path in architecture. Demo uses synthetic data only (no real PII).

## Consequences
- Recurring API cost ~cents/claim; acceptable for demo.
- Must not send real patient data; enforce synthetic-only in demo + DPDP posture doc.
- Interface abstraction adds small upfront cost; pays off for investor narrative (data sovereignty).