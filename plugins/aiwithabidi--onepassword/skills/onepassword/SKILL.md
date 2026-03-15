---
name: onepassword
description: "1Password Connect — vaults, items, secrets management for server-side applications."
homepage: https://www.agxntsix.ai
---

# 🔐 1Password

1Password Connect — vaults, items, secrets management for server-side applications.

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `OP_CONNECT_TOKEN` | ✅ | 1Password Connect token |
| `OP_CONNECT_HOST` | ✅ | 1Password Connect server URL |


## Quick Start

```bash
# List all vaults
python3 {{baseDir}}/scripts/onepassword.py list-vaults

# Get vault details
python3 {{baseDir}}/scripts/onepassword.py get-vault <id>

# List items in vault
python3 {{baseDir}}/scripts/onepassword.py list-items --vault-id <value>

# Get item with fields
python3 {{baseDir}}/scripts/onepassword.py get-item --vault-id <value> <id>

# Create item
python3 {{baseDir}}/scripts/onepassword.py create-item --vault-id <value> --category "LOGIN" --title <value> --fields "JSON"

# Update item
python3 {{baseDir}}/scripts/onepassword.py update-item --vault-id <value> <id> --fields "JSON"

# Delete item
python3 {{baseDir}}/scripts/onepassword.py delete-item --vault-id <value> <id>

# Check Connect server health
python3 {{baseDir}}/scripts/onepassword.py get-health

# Simple heartbeat check
python3 {{baseDir}}/scripts/onepassword.py get-heartbeat
```

## Output Format

All commands output JSON by default.

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/onepassword.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
