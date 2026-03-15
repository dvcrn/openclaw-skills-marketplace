---
name: openfec
description: "OpenFEC — campaign finance data, candidates, committees, filings, and contribution search."
homepage: https://www.agxntsix.ai
---

# 🗳️ OpenFEC

OpenFEC — campaign finance data, candidates, committees, filings, and contribution search.

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `FEC_API_KEY` | ✅ | FEC API key (or DEMO_KEY) |


## Quick Start

```bash
# Search candidates
python3 {{baseDir}}/scripts/openfec.py search-candidates --q <value> --office <value> --state <value> --party <value> --cycle <value> --per-page "20"

# Get candidate details
python3 {{baseDir}}/scripts/openfec.py get-candidate <id>

# Get candidate financial totals
python3 {{baseDir}}/scripts/openfec.py candidate-totals <id> --cycle <value>

# Search committees
python3 {{baseDir}}/scripts/openfec.py search-committees --q <value> --committee-type <value> --per-page "20"

# Get committee details
python3 {{baseDir}}/scripts/openfec.py get-committee <id>

# List filings
python3 {{baseDir}}/scripts/openfec.py list-filings --candidate-id <value> --committee-id <value> --per-page "20"

# Search individual contributions
python3 {{baseDir}}/scripts/openfec.py search-contributions --contributor-name <value> --contributor-state <value> --min-amount <value> --max-amount <value> --per-page "20"

# Search disbursements
python3 {{baseDir}}/scripts/openfec.py search-disbursements --committee-id <value> --recipient-name <value> --per-page "20"

# Get election results
python3 {{baseDir}}/scripts/openfec.py election-results --office "president" --cycle <value>

# Totals by entity type
python3 {{baseDir}}/scripts/openfec.py get-totals --cycle <value>
```

## Output Format

All commands output JSON by default.

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/openfec.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
