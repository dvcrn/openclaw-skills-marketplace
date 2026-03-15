---
name: segment
description: "Segment — manage sources, destinations, events, and tracking plans via Config & Tracking APIs"
homepage: https://www.agxntsix.ai
---

# 📊 Segment

Segment — manage sources, destinations, events, and tracking plans via Config & Tracking APIs

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `SEGMENT_ACCESS_TOKEN` | ✅ | Config API token |
| `SEGMENT_WRITE_KEY` | ✅ | Source write key |

## Quick Start

```bash
# List sources
python3 {{baseDir}}/scripts/segment.py sources

# Get source
python3 {{baseDir}}/scripts/segment.py source-get id <value>

# Create source
python3 {{baseDir}}/scripts/segment.py source-create --name <value> --catalog_name <value>

# Delete source
python3 {{baseDir}}/scripts/segment.py source-delete id <value>

# List destinations
python3 {{baseDir}}/scripts/segment.py destinations

# Get destination
python3 {{baseDir}}/scripts/segment.py destination-get id <value>

# List warehouses
python3 {{baseDir}}/scripts/segment.py warehouses

# List source catalog
python3 {{baseDir}}/scripts/segment.py catalog-sources
```

## All Commands

| Command | Description |
|---------|-------------|
| `sources` | List sources |
| `source-get` | Get source |
| `source-create` | Create source |
| `source-delete` | Delete source |
| `destinations` | List destinations |
| `destination-get` | Get destination |
| `warehouses` | List warehouses |
| `catalog-sources` | List source catalog |
| `catalog-destinations` | List destination catalog |
| `tracking-plans` | List tracking plans |
| `tracking-plan-get` | Get tracking plan |
| `spaces` | List spaces |
| `functions` | List functions |
| `track` | Send track event |
| `identify` | Send identify |

## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
python3 {{baseDir}}/scripts/segment.py <command> --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{{baseDir}}/scripts/segment.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
