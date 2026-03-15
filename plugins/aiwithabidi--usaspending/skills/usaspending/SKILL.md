---
name: usaspending
description: "USAspending.gov — federal spending data, contracts, grants, awards, agencies, and recipient search. No API key required."
homepage: https://www.agxntsix.ai
---

# 🏛️ USAspending

USAspending.gov — federal spending data, contracts, grants, awards, agencies, and recipient search. No API key required.

## Requirements

No API key required for basic usage.


## Quick Start

```bash
# Search federal awards
python3 {{baseDir}}/scripts/usaspending.py search-awards --keywords <value> --award-type "contracts" --limit "25" --page "1"

# Get award details
python3 {{baseDir}}/scripts/usaspending.py get-award <id>

# Search recipients
python3 {{baseDir}}/scripts/usaspending.py search-recipients --keyword <value> --limit "25"

# Get recipient details
python3 {{baseDir}}/scripts/usaspending.py get-recipient <id>

# List top-tier agencies
python3 {{baseDir}}/scripts/usaspending.py list-agencies

# Get agency details
python3 {{baseDir}}/scripts/usaspending.py get-agency --code <value>

# Spending by category
python3 {{baseDir}}/scripts/usaspending.py spending-by-category --category "awarding_agency" --filters "JSON"

# Spending over time
python3 {{baseDir}}/scripts/usaspending.py spending-over-time --group "fiscal_year" --filters "JSON"

# List CFDA programs
python3 {{baseDir}}/scripts/usaspending.py list-cfda

# Autocomplete search
python3 {{baseDir}}/scripts/usaspending.py autocomplete --search-text <value>
```

## Output Format

All commands output JSON by default.

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/usaspending.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
