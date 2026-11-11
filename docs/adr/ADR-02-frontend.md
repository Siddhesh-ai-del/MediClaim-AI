# ADR-02 — Frontend framework

- Status: accepted
- Date: 2026-11-11
- Mode stage: Stage 2/3

## Context
Claims-officer dashboard with upload, extraction review/edit, risk score, flags, adjudication, audit log.

## Problem
Which frontend stack?

## Considered alternatives
1. **Next.js 15 + React + Tailwind + shadcn/ui** — fast iteration, Vercel free hosting, good DX, SSR for marketing. Con: more moving parts than plain React.
2. **Vite + React (SPA)** — simpler, but no SSR/SEO for landing; hosting still free.
3. **Vue 3 / Nuxt** — team less fluent; smaller ecosystem for our components.

## Decision
Next.js (App Router) + React + TypeScript + Tailwind + shadcn/ui. Deploy frontend on Vercel hobby (free for demo).

## Consequences
- Marketing + app in one codebase; good for pitch/demo.
- Must keep bundle small; lazy-load heavy components.