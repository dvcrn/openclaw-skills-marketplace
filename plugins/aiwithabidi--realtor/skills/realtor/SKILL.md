---
name: realtor
description: "Realtor.com — search listings, agents, and property details via API"
homepage: https://www.agxntsix.ai
---

# 🏡 Realtor.com

Realtor.com — search listings, agents, and property details via API

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `REALTOR_API_KEY` | ✅ | RapidAPI key for Realtor API |

## Quick Start

```bash
# Search for-sale listings
python3 {{baseDir}}/scripts/realtor.py search-sale --city <value> --state_code <value> --postal_code <value> --price_min <value> --price_max <value>

# Search rentals
python3 {{baseDir}}/scripts/realtor.py search-rent --city <value> --state_code <value> --postal_code <value>

# Search recently sold
python3 {{baseDir}}/scripts/realtor.py search-sold --city <value> --state_code <value>

# Get property details
python3 {{baseDir}}/scripts/realtor.py property --property_id <value>

# Search agents
python3 {{baseDir}}/scripts/realtor.py agents --city <value> --state_code <value> --name <value>

# Get agent details
python3 {{baseDir}}/scripts/realtor.py agent-get --nrds_id <value>

# Location auto-complete
python3 {{baseDir}}/scripts/realtor.py auto-complete --input <value>
```

## All Commands

| Command | Description |
|---------|-------------|
| `search-sale` | Search for-sale listings |
| `search-rent` | Search rentals |
| `search-sold` | Search recently sold |
| `property` | Get property details |
| `agents` | Search agents |
| `agent-get` | Get agent details |
| `auto-complete` | Location auto-complete |

## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
python3 {{baseDir}}/scripts/realtor.py <command> --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{{baseDir}}/scripts/realtor.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
