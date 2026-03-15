---
name: wise
description: "Wise (TransferWise) — international transfers, multi-currency balances, recipients, exchange rates, and statements."
homepage: https://www.agxntsix.ai
---

# 💸 Wise

Wise (TransferWise) — international transfers, multi-currency balances, recipients, exchange rates, and statements.

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `WISE_API_TOKEN` | ✅ | Wise API token |


## Quick Start

```bash
# List profiles (personal/business)
python3 {{baseDir}}/scripts/wise.py get-profiles

# Get multi-currency balances
python3 {{baseDir}}/scripts/wise.py get-balances --profile-id <value>

# List recipients
python3 {{baseDir}}/scripts/wise.py list-recipients --profile-id <value>

# Create recipient
python3 {{baseDir}}/scripts/wise.py create-recipient --profile-id <value> --currency <value> --type <value> --details "JSON"

# Create transfer quote
python3 {{baseDir}}/scripts/wise.py create-quote --profile-id <value> --source <value> --target <value> --amount <value>

# Create transfer
python3 {{baseDir}}/scripts/wise.py create-transfer --quote-id <value> --recipient-id <value> --reference <value>

# Fund a transfer
python3 {{baseDir}}/scripts/wise.py fund-transfer --profile-id <value> --transfer-id <value>

# Get transfer status
python3 {{baseDir}}/scripts/wise.py get-transfer <id>

# List transfers
python3 {{baseDir}}/scripts/wise.py list-transfers --profile-id <value> --limit "10"

# Get exchange rate
python3 {{baseDir}}/scripts/wise.py get-rate --source <value> --target <value>

# Get statement
python3 {{baseDir}}/scripts/wise.py get-statement --profile-id <value> --balance-id <value>
```

## Output Format

All commands output JSON by default.

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/wise.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
