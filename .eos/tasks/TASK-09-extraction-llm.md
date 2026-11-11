---
id: TASK-09
title: Extraction module (LLM structured extraction)
assignee: eos-backend-engineer
parallel: no
dependencies: [TASK-08]
---
# TASK-09 — Extraction module

## Description
Implement Extractor interface + GPT-4o-mini extraction per docs/architecture/extraction-contract.md: prompt contract (injection defenses), schema validation, evidence quoting, input caps, real-data guard, versioned extraction rows.

## Requirements
- Extractor interface (swap to self-hosted Qwen).
- Prompt delimits document as data; JSON mode; max_tokens 2000; timeout 30s; retries 2.
- Pydantic schema extra='forbid'; amount/date/ICD validation; null for missing.
- source_quote + confidence per field; verifier checks quote substring.
- Real-data guard refuses non-synthetic (H-11).
- Adversarial injection test cases in eval.

## Expected output
- backend/app/extraction/llm.py, extractor.py, schemas.py, normalizer.py

## Acceptance criteria
- [ ] Extraction F1 ≥0.85 on synthetic eval set (AC-3, NFR-4).
- [ ] Injection payloads do not alter output (extraction-contract §7).
- [ ] Missing fields → null, never hallucinated.
- [ ] Versioned extraction rows created; corrections retained.

## Verification method
pytest tests/extraction/ (unit+integration); eval harness report.

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending