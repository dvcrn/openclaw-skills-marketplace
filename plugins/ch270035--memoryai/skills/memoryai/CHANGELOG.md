# Changelog

## 1.0.0 (2026-03-10)

### Changed
- **Context Guard v4.0** — Reads token usage directly from OpenClaw `sessions.json` instead of calling a non-existent API. Works immediately on all platforms (Windows, Linux, Mac).
- **Cron payloads** — Removed all `cd ...;` commands, replaced with absolute paths. Fixes exec tool errors.
- Client and skill version bumped to 0.6.0.

## 0.5.0 (2026-03-09)

### Added
- **Session Handoff** — Zero-gap session switching. When context fills up, seamlessly transition to a new session without losing any context.
  - `handoff-start` — Send old session conversation to MemoryAI server
  - `handoff-restore` — New session reads old conversation + related long-term memories
  - `handoff-complete` — Archive old session into long-term storage when ready
  - `handoff-status` — Check handoff state
- **Reflect command** — `client.py reflect` scans recent memories and creates insight chunks from patterns
- Server-side handoff engine with PostgreSQL-backed state management

### Changed
- Context Guard interval updated to 15 minutes (was 20)
- Client User-Agent updated to v0.5.0

## 0.4.2 (2026-03-08)

### Changed
- **Context Guard is now opt-in** — Agent must ask user permission before creating the background cron job.
- **Skill is no longer force-enabled** — Users enable it when needed.
- **Added Security & Privacy section** — Documents data handling, auditability, and key rotation guidance.

## 0.4.1 (2026-03-08)

### Fixed
- **Cloudflare 403 fix** — Added `User-Agent` header to all API requests. Previously blocked by Cloudflare bot protection.

## 0.4.0 (2026-03-08)

### Added
- **Context Guard** — Optional cron job monitors brain health, consolidates memories when urgency is high/critical
- **Check command** — `client.py check` returns brain urgency level (low/medium/high/critical)

### Changed
- SKILL.md rewritten with `{baseDir}` paths for proper skill resolution
- Added metadata for OpenClaw gating (emoji: 🧠)
- Improved "When to Use" table with triggers, actions, priorities, and tags

## 0.3.0 (2026-03-07)

### Changed
- Migrated to cloud-backed memory server for reliability and cross-device sync
- Store/recall/compact/restore commands updated for server API

## 0.2.0 (2026-03-07)

Initial public release — **A Brain for Your AI Agent**.

### Features
- **Store** — Save decisions, patterns, preferences with priority levels (hot / warm / cold)
- **Recall** — Intelligent multi-signal search (fast / deep / exhaustive)
- **Compact** — Consolidate long sessions into key memories automatically
- **Restore** — Start new sessions with full context from previous work
- **Stats** — Monitor brain health and memory usage

### Technical
- Zero dependencies — Python stdlib only (3.10+)
- Configure via config.json or environment variables
- Supports hosted (memoryai.dev) and self-hosted deployments
