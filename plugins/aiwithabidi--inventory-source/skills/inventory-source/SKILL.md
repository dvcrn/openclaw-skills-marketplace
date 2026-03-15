---
name: inventory-source
description: "Inventory Source — dropship automation, supplier management, product feeds, inventory sync, and order routing."
homepage: https://www.agxntsix.ai
---

# 📋 Inventory Source

Inventory Source — dropship automation, supplier management, product feeds, inventory sync, and order routing.

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `INVENTORYSOURCE_API_KEY` | ✅ | Inventory Source API key |


## Quick Start

```bash
# List connected suppliers
python3 {{baseDir}}/scripts/inventory-source.py list-suppliers

# Get supplier details
python3 {{baseDir}}/scripts/inventory-source.py get-supplier <id>

# List products
python3 {{baseDir}}/scripts/inventory-source.py list-products --page "1" --per-page "50"

# Get product details
python3 {{baseDir}}/scripts/inventory-source.py get-product <id>

# Trigger inventory sync
python3 {{baseDir}}/scripts/inventory-source.py sync-inventory

# List orders
python3 {{baseDir}}/scripts/inventory-source.py list-orders --page "1" --status <value>

# Get order details
python3 {{baseDir}}/scripts/inventory-source.py get-order <id>

# Route order to supplier
python3 {{baseDir}}/scripts/inventory-source.py route-order <id>

# List connected stores
python3 {{baseDir}}/scripts/inventory-source.py list-integrations

# Get product feed
python3 {{baseDir}}/scripts/inventory-source.py get-feed <id>
```

## Output Format

All commands output JSON by default.

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/inventory-source.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
