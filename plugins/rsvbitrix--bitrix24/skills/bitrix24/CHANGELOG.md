# Changelog

## 0.15.5 — 2026-03-11

### Added
- **Changelog on landing page**: "What's New" section loads dynamically from changelog.json
- **Publish script**: `scripts/publish.sh` — one command to bump version, generate changelog, push, and publish
- **Auto-update system**: scheduled task checks ClawHub every 2 hours and installs new versions automatically
- **Version display**: current version shown in footer and changelog badge

## 0.15.4 — 2026-03-11

### Added
- **Operation safety**: `bitrix24_call.py` now classifies methods as read/write/destructive and requires `--confirm-write` or `--confirm-destructive` flags for data-changing operations
- **Auto-pagination**: `--iterate` flag automatically collects all pages from `.list` methods
- **JSON params from file**: `--params-file` for complex parameters without shell escaping issues
- **Dry-run mode**: `--dry-run` previews what would be called without executing
- **File uploads reference**: new `references/files.md` — base64 for CRM, disk+attach for tasks
- **API module restrictions**: documented which modules don't work as expected via webhook (telephony, mail, connectors)
- **Batch cross-references**: `$result[name]` pattern for chaining commands

## 0.15.3 — 2026-03-11

### Added
- **Open Lines reference**: full `imopenlines.*` API coverage — line config, operators, sessions, dialog, CRM integration, bot
- **Support triggers**: "поддержка", "обращения", "операторы", "омниканал", "helpdesk" now route to Open Lines
- **MCP server link**: Known Limitations sections now point to `https://mcp-dev.bitrix24.tech/mcp` for checking API updates

## 0.15.0 — 2026-03-10

### Added
- **Channels reference**: `references/channels.md` — broadcast chats with `ENTITY_TYPE=ANNOUNCEMENT`
- **CRM timeline**: timeline comments and log messages in `references/crm.md`
- **Chat improvements**: message search, sharing, dialog history
- **Disk attachments**: file upload to chat via `im.disk.file.commit`

## 0.14.0 — 2026-03-09

### Added
- Batch API support (`bitrix24_batch.py`) — multiple methods in one HTTP request
- User ID and timezone caching after `user.current`
- 7 ready-made scenarios: morning briefing, weekly report, team status, client dossier, meeting prep, day results, sales pipeline
- 5 scheduled task templates: day plan, morning briefing, evening summary, overdue alert, new leads monitor
- Trigger phrases for all domains
- Cross-domain search scenario

## 0.13.0 — 2026-03-08

### Added
- Smart processes, products, quotes, and sites domain references
- Projects, feed, timeman domains
- Enhanced org structure reference

## 0.12.0 — 2026-03-07

### Changed
- Complete rewrite of all references with MCP-verified method names and examples
- Interaction rules moved to top of SKILL.md
- No technical jargon in user-facing output

## 0.11.0 — 2026-03-06

### Added
- GitHub Pages landing site (5 languages: EN, RU, ZH, ES, FR)
- OG image and social sharing meta tags
- Auto-detect browser language

## 0.10.0 — 2026-03-05

### Changed
- Dropped env vars — config file is the single webhook source
- Webhook stored in `~/.config/bitrix24-skill/config.json`
- Improved webhook diagnostics (`check_webhook.py`)
