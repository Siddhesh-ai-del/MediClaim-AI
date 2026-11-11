# ADR-06 — Hosting & deployment

- Status: accepted
- Date: 2026-11-11
- Mode stage: Stage 2/3

## Context
Student budget; need a live demo URL for pitch; backend runs OCR/LLM; frontend is dashboard.

## Problem
Where to host?

## Considered alternatives
1. **Render (backend $7/mo) + Render Postgres ($6/mo) + Vercel hobby (frontend free)** — predictable ~$13/mo, long-lived ASGI process (good for OCR jobs), managed Postgres.
2. **Railway (usage-based)** — cheaper at low traffic but variable bill; risk of surprise.
3. **Vercel serverless for backend** — cold starts, 60s timeout breaks OCR; not suitable.

## Decision
Render starter web service + managed Postgres for backend/API; Vercel hobby for Next.js frontend. Dockerfile for reproducible build. GPU not needed in prod for MVP (OCR runs on CPU; multimodal LLM only if enabled).

## Consequences
- ~$13/mo infra cost; acceptable.
- Must handle Render free-sleep if we ever downgrade; keep demo on paid starter during pitch window.
- Docker image must include OCR deps (PaddleOCR/Tesseract).