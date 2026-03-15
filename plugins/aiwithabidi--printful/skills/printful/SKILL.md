---
name: printful
description: "Printful — print-on-demand products, orders, shipping rates, mockup generation, and store management."
homepage: https://www.agxntsix.ai
---

# 👕 Printful

Printful — print-on-demand products, orders, shipping rates, mockup generation, and store management.

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `PRINTFUL_API_KEY` | ✅ | Printful API token |


## Quick Start

```bash
# List sync products
python3 {{baseDir}}/scripts/printful.py list-products --limit "20" --offset "0"

# Get product details
python3 {{baseDir}}/scripts/printful.py get-product <id>

# Create an order
python3 {{baseDir}}/scripts/printful.py create-order --recipient "JSON" --items "JSON array"

# List orders
python3 {{baseDir}}/scripts/printful.py list-orders --limit "20" --offset "0" --status <value>

# Get order details
python3 {{baseDir}}/scripts/printful.py get-order <id>

# Cancel an order
python3 {{baseDir}}/scripts/printful.py cancel-order <id>

# Estimate order costs
python3 {{baseDir}}/scripts/printful.py estimate-costs --recipient "JSON" --items "JSON array"

# Calculate shipping rates
python3 {{baseDir}}/scripts/printful.py get-shipping-rates --recipient "JSON" --items "JSON array"

# Browse product catalog
python3 {{baseDir}}/scripts/printful.py list-catalog --category <value>

# Get catalog product details
python3 {{baseDir}}/scripts/printful.py get-catalog-product <id>

# List mockup templates
python3 {{baseDir}}/scripts/printful.py list-mockup-templates --product-id <value>

# Generate mockup
python3 {{baseDir}}/scripts/printful.py create-mockup --product-id <value> --files "JSON"

# List warehouses
python3 {{baseDir}}/scripts/printful.py list-warehouses

# List supported countries
python3 {{baseDir}}/scripts/printful.py list-countries

# Get store info
python3 {{baseDir}}/scripts/printful.py get-store-info
```

## Output Format

All commands output JSON by default.

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/printful.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
