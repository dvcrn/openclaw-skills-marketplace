---
name: mercury-banking
description: "Mercury banking API integration — accounts, balances, transactions, financial summaries, AI transaction categorization, and cash flow analysis. The only Mercury banking skill on ClawHub. Use for business banking, financial tracking, and expense management."
homepage: https://www.agxntsix.ai
---

# 🏦 Mercury Banking

Mercury banking API integration for OpenClaw agents. Manage accounts, transactions, cash flow, and get AI-powered financial insights.

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `MERCURY_API_KEY` | ✅ | Mercury API token ([get one](https://app.mercury.com/settings/tokens)) |
| `OPENROUTER_API_KEY` | Optional | For AI categorization and summaries |

## Quick Start

```bash
# List all accounts and balances
python3 {baseDir}/scripts/mercury_api.py accounts

# Recent transactions
python3 {baseDir}/scripts/mercury_api.py transactions <account_id>

# Transactions with date filter
python3 {baseDir}/scripts/mercury_api.py transactions <account_id> --start 2026-01-01 --end 2026-01-31

# Search transactions
python3 {baseDir}/scripts/mercury_api.py transactions <account_id> --search "Stripe"

# Cash flow analysis
python3 {baseDir}/scripts/mercury_api.py cashflow <account_id> --days 30

# AI categorize transactions
python3 {baseDir}/scripts/mercury_api.py categorize <account_id> --days 30

# Financial summary
python3 {baseDir}/scripts/mercury_api.py summary <account_id> --period weekly
```

## Commands

### `accounts`
Lists all Mercury accounts with current balances, account type, and status.

### `transactions <account_id>`
Fetch transactions with optional filters:
- `--start YYYY-MM-DD` / `--end YYYY-MM-DD` — date range
- `--search "term"` — filter by counterparty or description
- `--limit N` — max results (default 50)
- `--status pending|sent|cancelled|failed` — filter by status

### `cashflow <account_id>`
Analyze cash flow over a period:
- `--days N` — lookback period (default 30)
- Shows total inflows, outflows, net, daily average, burn rate

### `categorize <account_id>`
AI-powered transaction categorization (requires `OPENROUTER_API_KEY`):
- `--days N` — lookback period (default 30)
- Groups transactions into categories (payroll, SaaS, revenue, etc.)
- Outputs category totals and percentages

### `summary <account_id>`
Generate financial summary:
- `--period weekly|monthly` — summary period
- Includes top expenses, revenue sources, cash position, trends

## Mercury API Notes

- **Base URL:** `https://api.mercury.com/api/v1`
- **Auth:** Bearer token in Authorization header
- **Rate limits:** Be mindful of API limits; the script handles pagination automatically
- **Sandbox:** Mercury provides a sandbox environment for testing

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
