---
name: shippo
description: "Shippo — shipping labels, rates comparison, package tracking, address validation, and returns."
homepage: https://www.agxntsix.ai
---

# 📦 Shippo

Shippo — shipping labels, rates comparison, package tracking, address validation, and returns.

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `SHIPPO_API_TOKEN` | ✅ | Shippo API token |


## Quick Start

```bash
# Create shipment & get rates
python3 {{baseDir}}/scripts/shippo.py create-shipment --from "JSON address" --to "JSON address" --parcel "JSON"

# List shipments
python3 {{baseDir}}/scripts/shippo.py list-shipments --results "25" --page "1"

# Get shipment details
python3 {{baseDir}}/scripts/shippo.py get-shipment <id>

# Get rates for shipment
python3 {{baseDir}}/scripts/shippo.py get-rates <id>

# Purchase shipping label
python3 {{baseDir}}/scripts/shippo.py purchase-label --rate <value>

# List label transactions
python3 {{baseDir}}/scripts/shippo.py list-transactions --results "25"

# Get label/transaction details
python3 {{baseDir}}/scripts/shippo.py get-transaction <id>

# Track a package
python3 {{baseDir}}/scripts/shippo.py track-package --carrier <value> --tracking-number <value>

# Validate an address
python3 {{baseDir}}/scripts/shippo.py validate-address --name <value> --street1 <value> --city <value> --state <value> --zip <value> --country "US"

# List saved parcels
python3 {{baseDir}}/scripts/shippo.py list-parcels

# Create a parcel template
python3 {{baseDir}}/scripts/shippo.py create-parcel --length <value> --width <value> --height <value> --weight <value>

# Create return shipment
python3 {{baseDir}}/scripts/shippo.py create-return --from "JSON" --to "JSON" --parcel "JSON" --is-return "true"

# List carrier accounts
python3 {{baseDir}}/scripts/shippo.py list-carriers
```

## Output Format

All commands output JSON by default.

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/shippo.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
