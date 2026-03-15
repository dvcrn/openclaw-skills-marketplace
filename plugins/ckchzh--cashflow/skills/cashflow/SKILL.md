---
name: CashFlow
description: "Personal cash flow tracker for managing daily finances. Log income and expenses with notes, check your current balance, view daily and monthly transaction summaries, and browse transaction history. All data stored locally for complete privacy. Perfect for freelancers, students, or anyone who wants simple money tracking without complex apps."
---

# CashFlow

CashFlow is a lightweight personal finance tracker that runs entirely in your terminal. No accounts, no cloud sync, no complexity — just simple, fast money tracking.

## Why CashFlow?

- **Zero setup**: Works immediately, no configuration needed
- **Privacy first**: All data stored locally on your machine
- **Fast logging**: Log transactions in seconds
- **Clear summaries**: Instant daily and monthly overviews
- **Portable**: Works on any system with bash and python3

## Commands

- `income <amount> [note]` — Record income with optional description
- `expense <amount> [note]` — Record an expense with optional description
- `balance` — Show current balance with income/expense breakdown
- `today` — List all transactions from today
- `month` — Monthly income and expense summary
- `history [n]` — Show last n transactions (default: 10)
- `info` — Version information
- `help` — Show available commands

## Usage Examples

```bash
cashflow income 5000 March salary
cashflow expense 45.50 lunch with team
cashflow expense 120 electricity bill
cashflow balance
cashflow month
```

## Data Storage

All financial data is stored in `~/.cashflow/` as JSON files. You can back up, export, or inspect your data at any time.

---
💬 Feedback & Feature Requests: https://bytesagain.com/feedback
Powered by BytesAgain | bytesagain.com
