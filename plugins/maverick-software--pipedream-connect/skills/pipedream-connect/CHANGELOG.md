# Changelog

All notable changes to the Pipedream Connect skill will be documented in this file.

## [1.5.2] - 2026-03-10

### Added
- A–Z alphabet filter in the per-agent "Browse Apps" modal to quickly narrow app list by starting letter
- Active letter indicator in app count text (e.g. `Letter: Q`) for clearer filter state

### Fixed
- Improved letter filter matching to use first alphabetic character from app name/slug
- Improved app card readability in modal by removing hard truncation and allowing wrapped names
- Included latest CSP/reference updates for direct catalog fallback (`https://mcp.pipedream.com`) in reference snapshots

## [1.5.1] - 2026-03-10

### Fixed
- Added explicit metadata declarations for sensitive config paths touched by the skill (`secrets.json`, `pipedream-credentials.json`, per-agent config files, `mcporter.json`, log paths)
- Added capability declarations for file read/write, outbound network domains, and optional cron persistence
- Clarified persistence and credential handling in metadata and docs to match real behavior
- Corrected INSTALL.md paths to current `~/.openclaw/...` layout and vault-backed credential model

## [1.5.0] - 2026-03-10

### Added
- Live Pipedream app catalog loading in the per-agent app browser (`https://mcp.pipedream.com/api/apps`) with pagination, dedupe, and in-memory caching
- Catalog loading state in the app browser modal

### Changed
- Agent Pipedream app browsing now prefers the live catalog over the old hardcoded app list
- Featured app section now sources from the loaded catalog when available

### Fixed
- Prevented indefinite "Loading…" hangs in agent Pipedream status by adding a timeout to the backend accounts fetch
- Improved fallback behavior when Pipedream API is slow/unreachable so UI still renders

## [1.4.0] - 2026-03-01

### Removed
- **1Password integration fully removed** — `--1password` CLI flag, `PIPEDREAM_1PASSWORD_ITEM` env var, `get_credentials_from_1password()` function, and all 1Password references deleted from scripts, docs, and metadata
- `shutil` and `subprocess` imports removed from token refresh script (no longer needed)

### Fixed
- Script paths corrected to `~/.openclaw/workspace/config/` throughout (was `~/clawd/config/` in some places)
- Metadata `configPaths` now explicitly declares all files read/written by the skill
- `installWarnings` updated to remove 1Password references

## [1.3.0] - 2026-03-01

### Security (Breaking — vault migration)
- **clientId and clientSecret moved to `~/.openclaw/secrets.json`** (OpenClaw vault) — no longer stored in `pipedream-credentials.json`
- **`PIPEDREAM_CLIENT_SECRET` removed from all `mcporter.json` env entries** — client secret is never written to mcporter config
- **Auto-migration on first start**: existing plaintext `pipedream-credentials.json` secrets silently moved to vault, file rewritten with non-secrets only
- Token refresh script (`pipedream-token-refresh.py`) now reads vault first; falls back to credentials.json → mcporter.json
- `pipedream-credentials.json` now contains only: `projectId`, `environment`, `externalUserId`
- Resolves VirusTotal "Suspicious" flag — no plaintext credential files

### Changed
- `buildMcporterEntry()` helper centralizes mcporter server entry construction, never includes clientSecret
- `readPipedreamCredentials()` now resolves secrets from vault at runtime, not from file

## [1.2.0] - 2026-03-01

### Added
- **Per-agent app connections** — App connections moved to Agents → [Agent] → Tools → Pipedream tab
- **Agent Pipedream panel** — New UI panel with live connected apps, available apps grid, and OAuth connect flow
- **Multi-agent isolation** — Each agent gets its own `external_user_id` (defaults to agent slug) and isolated OAuth tokens
- **New reference files**: `agent-pipedream-views.ts`, `agent-pipedream-controller.ts`
- **New RPCs**: `pipedream.getToken`, `pipedream.getConnectUrl`, `pipedream.connectApp`, `pipedream.disconnectApp`, `pipedream.refreshToken`, `pipedream.activate`
- **Environment warning** — Agent panel warns when running in development mode (use production for real work)
- **Browse All Apps modal** — Full app browser within the agent panel
- Complete RPC reference table in SKILL.md

### Changed
- Global Pipedream tab is now credentials-only (Client ID / Secret / Project ID / Environment)
- Agent quick-links table on global tab navigates to per-agent config
- Backend doubled in size (493 → 1,006 lines) with full multi-agent implementation
- `pipedream-backend.ts` refactored for per-agent config at `~/.openclaw/workspace/config/integrations/pipedream/{agentId}.json`

## [1.1.0] - 2025-02-11

### Added
- **Security transparency** for ClawHub compliance:
  - Added `capabilities` section documenting all system-modifying behaviors
  - Added `securityNotes` with credential storage warnings
  - Added `installWarnings` array with pre-install considerations
- Security section in SKILL.md with behavior table
- Security notice in INSTALL.md

### Fixed
- Corrected false "Encrypted credential storage" claim — credentials are stored as plaintext JSON with 0600 permissions, NOT encrypted

### Changed
- Bumped version to 1.1.0
- Updated Files Created table to accurately describe storage format
- Enhanced `pipedream-token-refresh.py` credential resolution

## [1.0.0] - 2025-02-10

### Added
- Initial release
- Pipedream OAuth integration with UI dashboard
- Token refresh script with cron setup
- MCP integration via mcporter
- Support for 2,000+ apps via Pipedream Connect
- Reference implementations for backend, controller, and views
