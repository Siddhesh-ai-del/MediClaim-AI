# ADR-04 — OCR engine

- Status: accepted
- Date: 2026-11-11
- Mode stage: Stage 2/3

## Context
Indian medical bills are mixed Hindi/English, often phone photos, with tables. Accuracy target NFR-4 (extraction F1 ≥0.85).

## Problem
Which OCR engine?

## Considered alternatives
1. **PaddleOCR (PP-OCRv4)** — free, self-hosted, strong on Indian scripts, better than Tesseract on noisy docs; needs install verification on Py 3.14. Con: heavier install, CPU slower.
2. **Tesseract 5.5 (`hin+eng`)** — already installed, free, privacy-friendly; weaker on noisy/mixed-script phone photos; digits read better paired with English.
3. **Cloud OCR (Google Document AI / Azure)** — highest accuracy on tables/layout; per-page cost (~$1.50/1000 pages) and data-residency conversation; requires network.

## Decision
PaddleOCR primary (verify install; fallback plan Tesseract) + Tesseract fallback for environments where PaddleOCR unavailable. Cloud OCR (Google Document AI) as optional premium path for hard cases, gated behind config flag. Always score English fields and vernacular fields separately (mixed-script trap).

## Consequences
- Must verify PaddleOCR installs on Python 3.14 early in Foundation milestone; if not, fall back to Tesseract + multimodal LLM OCR (Qwen2.5-VL) for extraction.
- No per-page cloud cost in demo unless explicitly enabled.
- Need OCR eval harness on synthetic Indian bills.