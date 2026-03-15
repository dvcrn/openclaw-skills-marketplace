# discord-cli

[![PyPI version](https://img.shields.io/pypi/v/kabi-discord-cli.svg)](https://pypi.org/project/kabi-discord-cli/)
[![Python versions](https://img.shields.io/pypi/pyversions/kabi-discord-cli.svg)](https://pypi.org/project/kabi-discord-cli/)

Discord CLI — fetch chat history, search messages, daily sync, AI analysis. Uses Discord HTTP API with user token (read-only).

## More Projects

- [twitter-cli](https://github.com/jackwener/twitter-cli) — Twitter/X CLI
- [bilibili-cli](https://github.com/jackwener/bilibili-cli) — Bilibili CLI
- [xhs-cli](https://github.com/jackwener/xhs-cli) — Xiaohongshu CLI



## Features

- 🔐 **Auth** — auto-extract token from browser/Discord client, status check, whoami
- 🏠 **Servers** — list guilds, channels, members, server info
- 📜 **History** — fetch and store message history in SQLite
- 🔄 **Sync** — incremental sync, bulk sync-all channels
- 🔍 **Search** — native Discord search + local keyword search
- 📊 **Analytics** — stats, top senders, timeline chart
- 📅 **Today** — view today's messages grouped by channel
- 🤖 **AI** — Claude-powered analyze and summary
- 📤 **Export** — text or JSON output for scripting
- 📊 **JSON output** — all query commands support `--json`

## Installation

```bash
# From PyPI
uv tool install kabi-discord-cli
# or
pipx install kabi-discord-cli

# From source
git clone git@github.com:jackwener/discord-cli.git
cd discord-cli
uv sync
```

## Quick Start

```bash
# Auto-extract and save token
discord auth --save

# Check login status
discord status
discord whoami

# List servers and channels
discord dc guilds
discord dc channels <guild_id>

# Fetch history
discord dc history <channel_id> -n 1000

# Incremental sync
discord dc sync <channel_id>
discord dc sync-all

# Today's messages
discord today
```

## Commands

### Auth & Account

| Command | Description |
|---------|-------------|
| `auth [--save]` | Extract token from browser/Discord client |
| `status` | Check if token is valid (exit code 0/1) |
| `whoami [--json]` | Detailed user profile |

### Discord (`discord dc ...`)

| Command | Description |
|---------|-------------|
| `dc guilds [--json]` | List joined servers |
| `dc channels GUILD [--json]` | List text channels |
| `dc history CHANNEL [-n 1000]` | Fetch historical messages |
| `dc sync CHANNEL` | Incremental sync |
| `dc sync-all` | Sync ALL channels in database |
| `dc search GUILD KEYWORD [-c CH]` | Native Discord search |
| `dc members GUILD [--max 50]` | List server members |
| `dc info GUILD [--json]` | Show server info |

### Query

| Command | Description |
|---------|-------------|
| `search KEYWORD [-c CH] [--json]` | Search stored messages |
| `stats [--json]` | Message statistics per channel |
| `today [-c CH] [--json]` | Today's messages |
| `top [-c CH] [--hours N] [--json]` | Most active senders |
| `timeline [-c CH] [--by day\|hour]` | Activity bar chart |

### Data & AI

| Command | Description |
|---------|-------------|
| `export CHANNEL [-f text\|json] [-o FILE]` | Export messages |
| `purge CHANNEL [-y]` | Delete stored messages |
| `analyze CHANNEL [--hours 24] [-p PROMPT]` | AI analysis (Claude) |
| `summary [-c CH] [--hours N]` | AI summary of today |

## Authentication

discord-cli auto-extracts token from:
1. **Discord desktop client** — reads from local leveldb
2. **Browsers** — Chrome, Edge, Brave local storage

Token is validated against the API before saving. Run `discord auth --save` for one-click setup.

## Architecture

```
src/discord_cli/
├── cli/
│   ├── main.py          # CLI entry + auth/status/whoami
│   ├── discord_cmds.py  # guilds, channels, history, sync, search, members
│   ├── query.py         # search, stats, today, top, timeline
│   └── data.py          # export, purge, analyze, summary
├── client.py            # httpx Discord API v10 with rate limiting
├── config.py            # Env var / .env config
├── db.py                # SQLite message store
├── auth.py              # Token extraction from browser/client
└── analyzer.py          # Claude AI analysis
```

Uses **httpx** (async HTTP) to call Discord REST API v10.
Messages are stored in **SQLite** (`~/Library/Application Support/discord-cli/messages.db`).

## Use as AI Agent Skill

discord-cli ships with a [`SKILL.md`](./SKILL.md) for AI agent integration.

### Claude Code / Antigravity

```bash
mkdir -p .agents/skills
git clone git@github.com:jackwener/discord-cli.git .agents/skills/discord-cli
```

### OpenClaw / ClawHub

```bash
clawhub install discord-cli
```

[中文文档](./README_CN.md)

## License

Apache-2.0
