# Migration Guide - AI Video Generation

Read this guide when upgrading from older published versions.

## Breaking Changes in v1.0.1

### 1) Setup and memory files are now required

**Before:** no standardized setup/memory workflow

**Now:** `setup.md`, `memory-template.md`, and `~/video-generation/memory.md` are the default pattern

**Migration steps:**
1. Create backup if legacy memory exists:
   ```bash
   cp ~/video-generation/memory.md ~/video-generation/memory.md.bak 2>/dev/null || true
   ```
2. Add missing sections from `memory-template.md`.
3. Keep old notes until the new structure is validated.

### 2) Provider routing shifted to current model stacks

**Before:** older references (for example early Kling, SVD-only fallback)

**Now:** prioritized routing includes Sora 2, Veo 3.x, Runway Gen-4, Seedance, Vidu, and Hailuo paths

**Migration steps:**
1. Map old provider notes into the new files in `Quick Reference`.
2. Keep old prompts as baseline, then rerun with current model IDs.
3. Preserve previous output archives for side-by-side quality checks.

### 3) API guidance now assumes async-first execution

**Before:** polling/retry logic was partial

**Now:** `api-patterns.md` defines unified async handling, backoff, URL expiry, and fallback rules

**Migration steps:**
1. Add idempotency keys for create requests where supported.
2. Standardize status polling and timeout handling.
3. Download outputs immediately after completion.

## Post-Migration Verification

- [ ] `~/video-generation/memory.md` exists and keeps prior preferences
- [ ] Legacy provider notes map to current provider files
- [ ] Async job handling is implemented consistently
- [ ] No user assets were deleted without explicit confirmation

## Cleanup Policy

- Never delete backups without explicit user confirmation.
- Prefer copy-first migration, then optional cleanup.
