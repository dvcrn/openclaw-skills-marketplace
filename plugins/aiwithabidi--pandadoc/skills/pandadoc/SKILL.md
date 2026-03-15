---
name: pandadoc
description: "PandaDoc — manage documents, templates, contacts, and e-signatures via REST API"
homepage: https://www.agxntsix.ai
---

# 🐼 PandaDoc

PandaDoc — manage documents, templates, contacts, and e-signatures via REST API

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `PANDADOC_API_KEY` | ✅ | API key from app.pandadoc.com |

## Quick Start

```bash
# List documents
python3 {{baseDir}}/scripts/pandadoc.py documents --status <value> --q <value> --tag <value>

# Get document details
python3 {{baseDir}}/scripts/pandadoc.py document-get id <value>

# Create document
python3 {{baseDir}}/scripts/pandadoc.py document-create --name <value> --template_uuid <value> --recipients <value>

# Send document
python3 {{baseDir}}/scripts/pandadoc.py document-send id <value> --message <value> --subject <value>

# Get status
python3 {{baseDir}}/scripts/pandadoc.py document-status id <value>

# Delete document
python3 {{baseDir}}/scripts/pandadoc.py document-delete id <value>

# Create sharing link
python3 {{baseDir}}/scripts/pandadoc.py document-link id <value> --recipient <value>

# List templates
python3 {{baseDir}}/scripts/pandadoc.py templates --q <value>
```

## All Commands

| Command | Description |
|---------|-------------|
| `documents` | List documents |
| `document-get` | Get document details |
| `document-create` | Create document |
| `document-send` | Send document |
| `document-status` | Get status |
| `document-delete` | Delete document |
| `document-link` | Create sharing link |
| `templates` | List templates |
| `template-get` | Get template |
| `contacts` | List contacts |
| `contact-create` | Create contact |
| `folders` | List folders |
| `webhooks` | List webhooks |

## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
python3 {{baseDir}}/scripts/pandadoc.py <command> --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{{baseDir}}/scripts/pandadoc.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
