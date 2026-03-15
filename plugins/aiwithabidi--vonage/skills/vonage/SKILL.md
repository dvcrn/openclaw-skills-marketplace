---
name: vonage
description: "Vonage — SMS messaging, voice calls, verify API, number management, and application management."
homepage: https://www.agxntsix.ai
---

# 📞 Vonage

Vonage — SMS messaging, voice calls, verify API, number management, and application management.

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `VONAGE_API_KEY` | ✅ | Vonage API key |
| `VONAGE_API_SECRET` | ✅ | Vonage API secret |


## Quick Start

```bash
# Send SMS
python3 {{baseDir}}/scripts/vonage.py send-sms --from <value> --to <value> --text <value>

# Search messages
python3 {{baseDir}}/scripts/vonage.py list-messages --date <value> --to <value>

# Create voice call
python3 {{baseDir}}/scripts/vonage.py create-call --to <value> --from <value> --ncco "JSON"

# List calls
python3 {{baseDir}}/scripts/vonage.py list-calls

# Get call details
python3 {{baseDir}}/scripts/vonage.py get-call <id>

# Send verification code
python3 {{baseDir}}/scripts/vonage.py send-verify --number <value> --brand <value>

# Check verification code
python3 {{baseDir}}/scripts/vonage.py check-verify --request-id <value> --code <value>

# List your numbers
python3 {{baseDir}}/scripts/vonage.py list-numbers

# Search available numbers
python3 {{baseDir}}/scripts/vonage.py search-numbers --country "US" --type "mobile-lvn"

# Buy a number
python3 {{baseDir}}/scripts/vonage.py buy-number --country <value> --msisdn <value>

# List applications
python3 {{baseDir}}/scripts/vonage.py list-applications

# Create application
python3 {{baseDir}}/scripts/vonage.py create-application --name <value>

# Get account balance
python3 {{baseDir}}/scripts/vonage.py get-balance
```

## Output Format

All commands output JSON by default.

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/vonage.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
