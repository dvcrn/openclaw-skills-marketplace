---
name: docusign
description: "DocuSign e-signatures — manage envelopes, templates, recipients, and signing via REST API"
homepage: https://www.agxntsix.ai
---

# ✍️ DocuSign

DocuSign e-signatures — manage envelopes, templates, recipients, and signing via REST API

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `DOCUSIGN_ACCESS_TOKEN` | ✅ | OAuth access token |
| `DOCUSIGN_ACCOUNT_ID` | ✅ | Account ID |
| `DOCUSIGN_BASE_URL` | ✅ | Base URL (default: demo) |

## Quick Start

```bash
# List envelopes
python3 {{baseDir}}/scripts/docusign.py envelopes --from_date <value> --status <value>

# Get envelope
python3 {{baseDir}}/scripts/docusign.py envelope-get id <value>

# Create envelope
python3 {{baseDir}}/scripts/docusign.py envelope-create --subject <value> --templateId <value> --status <value>

# Void envelope
python3 {{baseDir}}/scripts/docusign.py envelope-void id <value> --voidedReason <value>

# List recipients
python3 {{baseDir}}/scripts/docusign.py recipients id <value>

# List documents
python3 {{baseDir}}/scripts/docusign.py documents id <value>

# List templates
python3 {{baseDir}}/scripts/docusign.py templates --search_text <value>

# Get template
python3 {{baseDir}}/scripts/docusign.py template-get id <value>
```

## All Commands

| Command | Description |
|---------|-------------|
| `envelopes` | List envelopes |
| `envelope-get` | Get envelope |
| `envelope-create` | Create envelope |
| `envelope-void` | Void envelope |
| `recipients` | List recipients |
| `documents` | List documents |
| `templates` | List templates |
| `template-get` | Get template |
| `audit-events` | Get audit events |
| `folders` | List folders |
| `users` | List users |

## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
python3 {{baseDir}}/scripts/docusign.py <command> --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{{baseDir}}/scripts/docusign.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
