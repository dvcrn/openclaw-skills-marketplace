---
name: researchvault
description: "Local-first research orchestration engine. Manages state, synthesis, and optional background services (MCP/Watchdog)."
homepage: https://github.com/lraivisto/ResearchVault
---

# ResearchVault 🦞

**Local-first research orchestration engine.**

ResearchVault manages persistent state, synthesis, and autonomous verification for agents.

## Security & Privacy (Local First)

- **Local Storage**: All data is stored in a local SQLite database (~/.researchvault/research_vault.db). No cloud sync.
- **Network Transparency**: Outbound connections occur ONLY for user-requested research or Brave Search (if configured). 
- **SSRF Hardening**: Strict internal network blocking by default. Local/private IPs (localhost, 10.0.0.0/8, etc.) are blocked. Use `--allow-private-networks` to override.
- **Manual Opt-in Services**: Background watchers and MCP servers are in `scripts/services/` and must be started manually.
- **Strict Control**: `disable-model-invocation: true` prevents the model from autonomously starting background tasks.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Quick Start

1. **Initialize Project**:
   ```bash
   python scripts/vault.py init --objective "Analyze AI trends" --name "Trends-2026"
   ```

2. **Ingest Data**:
   ```bash
   python scripts/vault.py scuttle "https://example.com" --id "trends-2026"
   ```

3. **Autonomous Strategist**:
   ```bash
   python scripts/vault.py strategy --id "trends-2026"
   ```

## Portal (Manual Opt-In)

Start the portal explicitly:

```bash
./start_portal.sh
```

- Backend: `127.0.0.1:8000`
- Frontend: `127.0.0.1:5173`
- Backend auth strictly uses `RESEARCHVAULT_PORTAL_TOKEN`
- `./start_portal.sh` loads/generates `.portal_auth` and exports `RESEARCHVAULT_PORTAL_TOKEN` before backend launch
- Token login: URL hash `#token=<token>` (token from `.portal_auth`)
- Allowed DB roots are controlled by `RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS` (default `~/.researchvault,/tmp`)
- OpenClaw workspace DBs are never discovered or selectable in Portal mode
- Provider secrets are env-only (`BRAVE_API_KEY`, `SERPER_API_KEY`, `SEARXNG_BASE_URL`) and are not injected into vault subprocesses
- Both hosts are supported for browser access:
  - `http://127.0.0.1:5173/#token=<token>`
  - `http://localhost:5173/#token=<token>`

Operational commands:

```bash
./start_portal.sh --status
./start_portal.sh --stop
```

Security parity with CLI:
- SSRF blocking is on by default (private/local/link-local targets denied).
- Portal toggle **Allow private networks** is equivalent to CLI `--allow-private-networks`.

## Optional Services (Manual Start)

- **MCP Server**: `python scripts/services/mcp_server.py`
- **Watchdog**: `python scripts/services/watchdog.py --once`

## Provenance & Maintenance

- **Maintainer**: lraivisto
- **License**: MIT
- **Issues**: [GitHub Issues](https://github.com/lraivisto/ResearchVault/issues)
- **Security**: See [SECURITY.md](SECURITY.md)
