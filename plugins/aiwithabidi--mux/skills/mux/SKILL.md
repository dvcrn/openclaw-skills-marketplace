---
name: mux
description: "Mux video — manage assets, live streams, playback IDs, and analytics via REST API"
homepage: https://www.agxntsix.ai
---

# 🎬 Mux

Mux video — manage assets, live streams, playback IDs, and analytics via REST API

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `MUX_TOKEN_ID` | ✅ | API token ID |
| `MUX_TOKEN_SECRET` | ✅ | API token secret |

## Quick Start

```bash
# List assets
python3 {{baseDir}}/scripts/mux.py assets --limit <value>

# Get asset
python3 {{baseDir}}/scripts/mux.py asset-get id <value>

# Create asset
python3 {{baseDir}}/scripts/mux.py asset-create --url <value> --playback_policy <value>

# Delete asset
python3 {{baseDir}}/scripts/mux.py asset-delete id <value>

# Get input info
python3 {{baseDir}}/scripts/mux.py asset-input-info id <value>

# List playback IDs
python3 {{baseDir}}/scripts/mux.py asset-playback-ids id <value>

# List live streams
python3 {{baseDir}}/scripts/mux.py live-streams

# Get live stream
python3 {{baseDir}}/scripts/mux.py live-stream-get id <value>
```

## All Commands

| Command | Description |
|---------|-------------|
| `assets` | List assets |
| `asset-get` | Get asset |
| `asset-create` | Create asset |
| `asset-delete` | Delete asset |
| `asset-input-info` | Get input info |
| `asset-playback-ids` | List playback IDs |
| `live-streams` | List live streams |
| `live-stream-get` | Get live stream |
| `live-stream-create` | Create live stream |
| `live-stream-delete` | Delete live stream |
| `live-stream-reset-key` | Reset stream key |
| `uploads` | List uploads |
| `upload-create` | Create direct upload |
| `views` | List video views |
| `metrics` | Get metrics |
| `monitoring` | Monitoring metrics |

## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
python3 {{baseDir}}/scripts/mux.py <command> --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{{baseDir}}/scripts/mux.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
