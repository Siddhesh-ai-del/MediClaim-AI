# ADR-07 — Fraud detection approach

- Status: accepted
- Date: 2026-11-11
- Mode stage: Stage 2/3

## Context
Need credible, explainable fraud detection buildable in 5 months with no real labeled data.

## Problem
Rules vs ML vs hybrid?

## Considered alternatives
1. **Rule-based Red Flag Indicators (IRDAI-aligned) + statistical anomaly** — explainable, buildable, maps to regulator's vocabulary (RFIs), no training data needed. Con: may miss novel schemes; lower recall.
2. **Supervised ML classifier (XGBoost)** — higher recall potential but needs labeled fraud data (we don't have) → overfit to synthetic; black-box risk.
3. **Hybrid: rules+stats (P0) + ML classifier (P1, trained on synthetic, clearly labeled)** — best of both; ML only enhances, never sole decision.

## Decision
Hybrid: rules + statistical anomaly as P0 (mandatory, explainable, sole basis for MVP recommendations); ML classifier as P1 enhancement trained on synthetic data, clearly labeled as "experimental" in UI and docs. Every flag cites type + evidence + severity + source (rule/stat/ml).

## Consequences
- MVP defensible even without ML; ML is upside, not dependency.
- Must label synthetic-trained ML as experimental (R09, no fabricated completion).
- Eval harness (Stage 6) reports precision/recall on synthetic set.