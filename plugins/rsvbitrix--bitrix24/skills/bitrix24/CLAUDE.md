# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Bitrix24 skill for OpenClaw — an agent that connects to Bitrix24 via webhook and lets non-technical users (company directors) manage CRM, tasks, calendar, etc. through natural language. Published to ClawHub as `bitrix24`.

## Architecture

Two-layer design:

1. **Python scripts** (`scripts/`) — make REST calls, manage webhook config, diagnose connectivity. No external dependencies beyond Python stdlib (`urllib`, `json`, `ssl`, `socket`).
2. **MCP documentation server** (`https://mcp-dev.bitrix24.tech/mcp`) — provides live method/event/article lookups via `bitrix-search`, `bitrix-method-details`, etc.

All REST calls go through a single webhook URL stored in `~/.config/bitrix24-skill/config.json`.

## Key Files

- `SKILL.md` — **the most important file**. Agent entrypoint: frontmatter (metadata, tags, MCP config), user interaction rules, technical rules, domain reference index. This is what the bot reads to know how to behave.
- `scripts/bitrix24_call.py` — REST caller with operation safety, auto-pagination, dry-run. Usage: `python3 scripts/bitrix24_call.py <method> --param 'key=value' --json`. Supports `--params-file`, `--iterate`, `--dry-run`, `--confirm-write`, `--confirm-destructive`.
- `scripts/bitrix24_batch.py` — batch caller for multi-method requests. Usage: `python3 scripts/bitrix24_batch.py --cmd 'name=method?params' --cmd '...' --json`
- `scripts/bitrix24_config.py` — shared config module: `load_url()`, `validate_url()`, `persist_url_to_config()`, `get_cached_user()`
- `scripts/save_webhook.py` — save webhook to config with optional `--check` verification
- `scripts/check_webhook.py` — diagnostics: format → DNS → HTTP probe of `user.current.json`
- `references/*.md` — 18 domain reference files with exact method names, parameters, filter syntax, examples
- `docs/index.html` — GitHub Pages landing site (5 languages: EN/RU/ZH/ES/FR, auto-detects browser language)
- `agents/openai.yaml` — OpenAI/OpenClaw agent metadata

## Common Commands

```bash
# Make a REST call
python3 scripts/bitrix24_call.py user.current --json
python3 scripts/bitrix24_call.py crm.deal.list --param 'select[]=ID' --param 'select[]=TITLE' --json

# Auto-paginate (collect all pages)
python3 scripts/bitrix24_call.py crm.deal.list --param 'select[]=ID' --iterate --json

# Params from JSON file (for complex queries)
echo '{"filter": {">=DATE_CREATE": "2025-01-01"}, "select": ["ID", "TITLE"]}' > /tmp/p.json
python3 scripts/bitrix24_call.py crm.deal.list --params-file /tmp/p.json --json

# Dry-run (preview without executing)
python3 scripts/bitrix24_call.py crm.deal.add --param 'fields[TITLE]=Test' --dry-run --json

# Write operations require --confirm-write
python3 scripts/bitrix24_call.py crm.deal.add --param 'fields[TITLE]=Test' --confirm-write --json

# Save webhook (first-time setup)
python3 scripts/bitrix24_call.py user.current --url "https://portal.bitrix24.ru/rest/1/secret/" --json

# Diagnose webhook
python3 scripts/check_webhook.py --json

# Publish to ClawHub (check current version first)
npx clawhub inspect bitrix24 --versions
npx clawhub publish . --version X.Y.Z

# Batch call (multiple methods in one request)
python3 scripts/bitrix24_batch.py \
  --cmd 'tasks=tasks.task.list?filter[RESPONSIBLE_ID]=5' \
  --cmd 'deals=crm.deal.list?filter[ASSIGNED_BY_ID]=5&select[]=ID&select[]=TITLE' \
  --json

# Preview landing page locally
# Use Claude Preview with "landing" config from .claude/launch.json (port 8090)

# Install on remote (full PATH required)
ssh slon-mac "export PATH=\$HOME/.nvm/versions/node/*/bin:/opt/homebrew/bin:/usr/local/bin:\$PATH && npx clawhub install bitrix24 --version X.Y.Z --force"

# Restart gateway after install
ssh slon-mac "export PATH=\$HOME/.nvm/versions/node/*/bin:/opt/homebrew/bin:/usr/local/bin:\$PATH && openclaw gateway restart"
```

## Publishing Workflow

### Quick publish (recommended)

```bash
# 1. Update CHANGELOG.md with new version entry
# 2. Run the publish script:
bash scripts/publish.sh X.Y.Z
```

This script automatically:
- Updates version in `docs/index.html` footer
- Generates `docs/changelog.json` from CHANGELOG.md
- Commits, pushes, and publishes to ClawHub

### Manual steps (if needed)

1. Commit and push to `origin/main` (`https://github.com/rsvbitrix/bitrix24-skill.git`)
2. `npx clawhub publish . --version X.Y.Z` — publishes to ClawHub, triggers security scan (~1-2 min)
3. Wait ~90 seconds for scan to pass before installing (check with `npx clawhub inspect bitrix24`)
4. On slon-mac: `npx clawhub install bitrix24 --version X.Y.Z --force` (needs full PATH, see Common Commands)
5. Restart OpenClaw gateway: `openclaw gateway restart`

### Auto-update

A scheduled task (`bitrix24-auto-update`) checks ClawHub every 2 hours and auto-installs new versions on slon-mac. Manual install is only needed if you want it immediately.

**Known issue:** ClawHub rate-limits install requests. If you get `Rate limit exceeded`, wait 2-3 minutes and retry.

## Critical Design Decisions

- **No env vars** — webhook lives only in config JSON, no `.env` files, no `BITRIX24_WEBHOOK_URL`
- **SKILL.md rules go first** — user interaction rules are at the top before any technical content, because the bot must see them before anything else
- **Reference files use `bitrix24_call.py` examples** — not curl, not BX24.js. All examples are copy-paste ready for the agent.
- **Filter operators are key prefixes** — `>=DEADLINE`, `!STATUS`, `>OPPORTUNITY`. This is a common bot mistake; it's documented in SKILL.md rules and reference files.
- **No `calendar.get`** — it doesn't exist. The correct method is `calendar.event.get` with mandatory `type` and `ownerId`. This was a real bot failure that triggered a full MCP audit.
- **Timeline methods mix field cases** — `crm.timeline.logmessage.add` uses camelCase (`entityTypeId`), while `crm.timeline.comment.add` uses UPPER_CASE (`ENTITY_ID`). Always check the reference.
- **Single skill, not multi-skill** — we intentionally keep everything in one skill (not split into 10 separate ones like the analysis doc suggests). One skill = simpler UX for the director.

## Bitrix24 API Patterns

- Method names: `module.entity.action` (e.g., `crm.deal.list`, `tasks.task.add`)
- Entity type IDs: 1=lead, 2=deal, 3=contact, 4=company, 7=quote, 31=smart invoice, 128+=custom
- Universal API: `crm.item.*` works across all entity types with `entityTypeId` param
- Fields: UPPER_CASE in classic methods (`crm.deal.*`), camelCase in universal (`crm.item.*`)
- Pagination: page size 50, use `start` parameter
- Dates: ISO 8601 for datetime, `YYYY-MM-DD` for date-only
- Batch API: `batch` method accepts `cmd` dict and returns results keyed by command name under `body.result.result`
- No REST API for emails: `mailservice.*` only configures SMTP/IMAP, cannot send/read emails
