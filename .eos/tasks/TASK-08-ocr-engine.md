---
id: TASK-08
title: OCR engine integration
assignee: eos-backend-engineer
parallel: yes
dependencies: [TASK-06, TASK-07]
---
# TASK-08 — OCR engine integration

## Description
Implement OCR module: PaddleOCR primary + Tesseract fallback, per-page text+confidence, process-pool execution, timeout, mixed-script scoring (ADR-04). Store ocr_result rows.

## Requirements
- Engine selection via OCR_PRIMARY/OCR_FALLBACK env.
- Score English and vernacular fields separately (mixed-script trap).
- Timeout per file (M-15); fallback on failure.
- Handle PDF (pdf2image) + images.

## Expected output
- backend/app/extraction/ocr/ (paddle.py, tesseract.py, runner.py)

## Acceptance criteria
- [ ] Clean English bill OCR CER ≤0.05 on sample.
- [ ] Hindi+English mixed bill processes without crash.
- [ ] Engine failure falls back and logs.
- [ ] Per-file timeout kills stuck worker.

## Verification method
pytest tests/extraction/ocr/ with sample bills in tests/fixtures/.

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending