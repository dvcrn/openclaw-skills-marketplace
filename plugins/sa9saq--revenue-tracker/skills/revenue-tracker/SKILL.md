---
name: revenue-tracker
description: "Track {AGENT_NAME} income and expenses. Generate financial reports and analyze profitability across platforms."
---

# Revenue Tracker

Track income, expenses, and profitability across all platforms.

## Instructions

1. **Record transactions** in `~/.openclaw/revenue/transactions.jsonl`:
   ```json
   {"date": "2026-02-10", "type": "income", "platform": "coconala", "amount": 3000, "fee": 660, "net": 2340, "description": "GAS automation", "currency": "JPY"}
   {"date": "2026-02-10", "type": "expense", "category": "api", "amount": 750, "description": "Cloudflare Workers", "currency": "JPY"}
   ```

2. **Calculate net revenue**:
   ```bash
   # Daily income
   jq -s '[.[] | select(.date=="2026-02-10" and .type=="income")] | map(.net) | add' ~/.openclaw/revenue/transactions.jsonl
   
   # Monthly expenses
   jq -s '[.[] | select(.date | startswith("2026-02") and .type=="expense")] | map(.amount) | add' ~/.openclaw/revenue/transactions.jsonl
   ```

3. **Platform fee reference**:

   | Platform | Fee Rate | Payout |
   |----------|---------|--------|
   | Coconala | 22% | Monthly (min ¥3,000) |
   | Fiverr | 20% | Bi-weekly ($5 min) |
   | Upwork | 10-20% | Weekly ($100 min) |
   | Moltbook | 1-2% | Instant (crypto) |
   | Note.com | 15% (paywall) | Monthly |
   | Gumroad | 10% | Weekly |
   | Direct | 0% | Per invoice |

4. **Generate reports**:

   ### Daily
   ```
   📊 Daily Revenue — 2026-02-10
   Income:  ¥3,000 (Coconala ×1)
   Expense: ¥0
   Net:     ¥2,340 (after fees)
   ```

   ### Weekly
   ```
   📊 Weekly Revenue — Week 6, 2026
   | Platform | Orders | Gross | Fees | Net |
   |----------|--------|-------|------|-----|
   | Coconala | 2 | ¥6,000 | ¥1,320 | ¥4,680 |
   | Note | 5 views | ¥500 | ¥75 | ¥425 |
   | Total | — | ¥6,500 | ¥1,395 | ¥5,105 |
   
   Expenses: ¥850 (API ¥750, Domain ¥100)
   Profit:   ¥4,255
   ```

   ### Monthly
   ```
   📊 Monthly Revenue — February 2026
   Total Income:    ¥XX,XXX
   Total Expenses:  ¥X,XXX
   Net Profit:      ¥XX,XXX
   Profit Margin:   XX%
   Goal Progress:   XX% of ¥300,000
   
   By Platform: [bar chart using Unicode blocks]
   ████████░░ Coconala  60%
   ███░░░░░░░ Note      20%
   ██░░░░░░░░ Crypto    15%
   █░░░░░░░░░ Other      5%
   ```

5. **Goal tracking**:
   ```json
   {"month": "2026-02", "target": 300000, "actual": 0, "progress": 0}
   ```

## Milestones

| Level | Monthly Target | Status |
|-------|---------------|--------|
| 🥉 Bronze | ¥10,000 | |
| 🥈 Silver | ¥50,000 | |
| 🥇 Gold | ¥100,000 | |
| 💎 Diamond | ¥300,000 | Goal: quit job |
| 👑 Crown | ¥1,000,000 | |

## Security

- **Never post exact amounts on SNS** — use vague terms ("そこそこ稼げた")
- **Don't link client names to amounts** in any shared/public file
- **Keep transactions.jsonl private** — add to .gitignore
- **Backup financial data** — critical records

## Requirements

- File system access for `~/.openclaw/revenue/`
- `jq` for JSONL querying
- No external API keys needed
