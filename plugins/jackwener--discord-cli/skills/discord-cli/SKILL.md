---
name: discord-cli
description: "Discord CLI for fetching chat history, searching messages, and AI analysis"
---

# discord-cli Skill

CLI tool for Discord — fetch chat history, search messages, sync channels, AI analysis.

## Prerequisites

- Python 3.10+

```bash
# Install
uv tool install kabi-discord-cli
# Or: pipx install kabi-discord-cli
```

- Token configured via `discord auth --save`
- AI commands require `ANTHROPIC_API_KEY` env var

## Commands

### Auth & Account

```bash
discord auth --save          # Auto-extract & save token
discord status               # Check token validity (exit 0 = valid)
discord whoami               # User profile
discord whoami --json        # Raw JSON
```

### Servers & Channels

```bash
discord dc guilds            # List servers
discord dc guilds --json     # JSON output
discord dc channels <GUILD>  # List text channels
discord dc info <GUILD>      # Server details
discord dc members <GUILD>   # List members
```

### Fetching Messages

```bash
discord dc history <CHANNEL_ID> -n 1000   # Fetch history
discord dc sync <CHANNEL_ID>              # Incremental sync
discord dc sync-all                       # Sync all known channels
discord dc search <GUILD> "keyword"       # Native Discord search
```

### Querying Stored Messages

```bash
discord search "keyword"                  # Search local DB
discord search "keyword" -c general       # Filter by channel
discord stats                             # Per-channel stats
discord today                             # Today's messages
discord today -c general --json           # Filter + JSON
discord top                               # Most active senders
discord top --hours 24                    # Last 24h only
discord timeline                          # Activity chart
discord timeline --by hour               # Hourly granularity
```

### Data & AI

```bash
discord export <CHANNEL> -f json -o out.json   # Export
discord purge <CHANNEL> -y                     # Delete stored
discord analyze <CHANNEL> --hours 24           # AI analysis
discord summary                                # AI summary of today
discord summary --hours 48                     # Last 48h summary
```

## Workflow: Daily Sync

```bash
# 1. First time: fetch history for channels you care about
discord dc guilds
discord dc channels <guild_id>
discord dc history <channel_id> -n 2000

# 2. Daily: incremental sync
discord dc sync-all

# 3. Read today's messages
discord today

# 4. AI summary
discord summary
```

## Notes

- Uses Discord user token (not bot token) for read-only access
- Rate limits are handled automatically with retry
- Messages stored in SQLite at `~/Library/Application Support/discord-cli/messages.db`
- AI commands require `ANTHROPIC_API_KEY` env var

## Safety Notes

- Do not ask users to share raw token values in chat logs.
- Prefer auto-extraction via `discord auth --save` over manual token input.
- Token is stored locally and never uploaded.
