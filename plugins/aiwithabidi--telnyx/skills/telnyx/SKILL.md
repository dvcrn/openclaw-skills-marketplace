---
name: telnyx
description: "Telnyx — voice, SMS/MMS messaging, SIP trunking, number management, and fax."
homepage: https://www.agxntsix.ai
---

# ☎️ Telnyx

Telnyx — voice, SMS/MMS messaging, SIP trunking, number management, and fax.

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `TELNYX_API_KEY` | ✅ | Telnyx API key (v2) |


## Quick Start

```bash
# Send SMS/MMS
python3 {{baseDir}}/scripts/telnyx.py send-message --from <value> --to <value> --text <value>

# List messages
python3 {{baseDir}}/scripts/telnyx.py list-messages --page-size "25"

# Create outbound call
python3 {{baseDir}}/scripts/telnyx.py create-call --from <value> --to <value> --connection-id <value>

# List active calls
python3 {{baseDir}}/scripts/telnyx.py list-calls

# Get call details
python3 {{baseDir}}/scripts/telnyx.py get-call <id>

# Hang up call
python3 {{baseDir}}/scripts/telnyx.py hangup-call <id>

# List phone numbers
python3 {{baseDir}}/scripts/telnyx.py list-numbers --page-size "25"

# Search available numbers
python3 {{baseDir}}/scripts/telnyx.py search-numbers --country-code "US" --limit "10"

# Order phone number
python3 {{baseDir}}/scripts/telnyx.py order-number --phone-numbers "JSON array"

# List SIP connections
python3 {{baseDir}}/scripts/telnyx.py list-connections

# Create SIP connection
python3 {{baseDir}}/scripts/telnyx.py create-connection --name <value> --connection-type "ip"

# Send a fax
python3 {{baseDir}}/scripts/telnyx.py send-fax --from <value> --to <value> --media-url <value>

# List faxes
python3 {{baseDir}}/scripts/telnyx.py list-faxes

# Get account balance
python3 {{baseDir}}/scripts/telnyx.py get-balance
```

## Output Format

All commands output JSON by default.

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/telnyx.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
