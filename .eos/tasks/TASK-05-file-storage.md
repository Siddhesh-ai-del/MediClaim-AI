---
id: TASK-05
title: File storage adapter
assignee: eos-backend-engineer
parallel: yes
dependencies: [TASK-01]
---
# TASK-05 — File storage adapter

## Description
Implement storage adapter (local FS, UUID filenames, path traversal protection, magic-byte validation, size limits) per extraction-contract §5 and error-handling §9.1 (H-5).

## Requirements
- Interface `StorageBackend` (local impl; S3 adapter later).
- Server-generated UUID filename; original filename metadata only.
- Validate magic bytes + PDF structure; reject traversal; timeouts.
- Per-file max 20MB; claim max 10 files.

## Expected output
- backend/app/ingestion/storage.py, backend/app/ingestion/validation.py

## Acceptance criteria
- [ ] Upload of malicious filename (../) rejected.
- [ ] Oversized file rejected before parsing.
- [ ] Round-trip store/retrieve by UUID works.

## Verification method
pytest tests/ingestion/storage/ (unit).

## Report format for the assigned agent
changed files · commands run w/ results · unresolved problems · AC confirmations

## Status
pending