---
name: wave
description: "Wave accounting — invoices, customers, transactions, accounts, products, taxes. Small business accounting CLI."
homepage: https://www.agxntsix.ai
---

# 🌊 Wave

Invoicing and accounting for small business — invoices, customers, transactions.

## Features

- **Businesses** — list connected businesses
- **Invoices** — create, send, list, delete
- **Customers** — manage customer records
- **Accounts** — chart of accounts
- **Transactions** — view financial transactions
- **Products & taxes** — manage items and tax rates

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `WAVE_API_TOKEN` | ✅ | API key/token for Wave |

## Quick Start

```bash
python3 {baseDir}/scripts/wave.py businesses
python3 {baseDir}/scripts/wave.py invoices <business-id>
python3 {baseDir}/scripts/wave.py invoice-create <business-id> <customer-id> --amount 500
python3 {baseDir}/scripts/wave.py customers <business-id>
python3 {baseDir}/scripts/wave.py transactions <business-id>
```

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
