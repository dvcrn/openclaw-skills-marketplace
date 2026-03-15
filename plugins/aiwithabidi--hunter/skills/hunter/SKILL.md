---
name: hunter
description: "Hunter.io — email finder, email verifier, domain search, author finder, and lead management."
homepage: https://www.agxntsix.ai
---

# 🔍 Hunter.io

Hunter.io — email finder, email verifier, domain search, author finder, and lead management.

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `HUNTER_API_KEY` | ✅ | Hunter.io API key |


## Quick Start

```bash
# Find emails for a domain
python3 {{baseDir}}/scripts/hunter.py domain-search --domain <value> --limit "10" --type <value>

# Find specific person's email
python3 {{baseDir}}/scripts/hunter.py email-finder --domain <value> --first-name <value> --last-name <value>

# Verify an email address
python3 {{baseDir}}/scripts/hunter.py email-verifier --email <value>

# Count emails for domain
python3 {{baseDir}}/scripts/hunter.py email-count --domain <value>

# List saved leads
python3 {{baseDir}}/scripts/hunter.py list-leads --limit "20" --offset "0"

# Create a lead
python3 {{baseDir}}/scripts/hunter.py create-lead --email <value> --first-name <value> --last-name <value> --company <value>

# Update a lead
python3 {{baseDir}}/scripts/hunter.py update-lead <id> --email <value> --first-name <value> --last-name <value>

# Delete a lead
python3 {{baseDir}}/scripts/hunter.py delete-lead <id>

# List lead lists
python3 {{baseDir}}/scripts/hunter.py list-leads-lists

# Get account info & usage
python3 {{baseDir}}/scripts/hunter.py get-account

# Find author of article
python3 {{baseDir}}/scripts/hunter.py author-finder --url <value>
```

## Output Format

All commands output JSON by default.

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/hunter.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
