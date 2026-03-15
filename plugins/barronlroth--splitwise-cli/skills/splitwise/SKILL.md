---
name: splitwise
description: "Manage shared expenses via the Splitwise CLI. Use when asked to log, split, or track expenses with other people, check balances, see who owes whom, settle debts, or list recent charges. Triggers on mentions of Splitwise, shared expenses, splitting costs, \"log this expense,\" \"who owes what,\" roommate/partner bills, or any expense-tracking request. Also use when proactively logging bills discovered during email scans or subscription analysis. Even casual mentions like \"split this with Nina\" or \"add the internet bill\" should trigger this skill."
---

# Splitwise CLI Skill

Manage shared expenses, balances, and settlements through the `splitwise` CLI.

## Setup

The CLI is installed at `~/.local/bin/splitwise` and authenticated via OAuth 2.0. Token is at `~/.config/splitwise-cli/auth.json`. If auth expires, the CLI will tell you — run `splitwise auth` to re-authenticate (requires browser OAuth flow).

The default group is configured as **Dolores** (Barron + Nina's shared expenses group). You don't need to pass `--group` for their shared expenses.

## Quick Reference

### Check balances
```bash
# Default group (Dolores) balances
splitwise balances

# Specific group
splitwise balances --group "Aspen 23"
```

### List expenses
```bash
# Recent expenses in default group
splitwise expenses list --limit 10

# Date-filtered
splitwise expenses list --after 2026-03-01 --before 2026-03-31

# Different group
splitwise expenses list --group "Rome" --limit 5
```

### Create an expense
```bash
# Even split, you (Barron) paid — most common case
splitwise expenses create "Xfinity Internet - March" 51.30

# Nina paid
splitwise expenses create "Groceries" 87.50 --paid-by "Nina"

# Different group
splitwise expenses create "Dinner" 120.00 --group "Rome"

# Different currency
splitwise expenses create "Dinner in Lisbon" 45.00 --group "Rome" --currency EUR
```

### Other commands
```bash
splitwise me                          # Current user info
splitwise groups                      # List all groups
splitwise group "Dolores"             # Group details + member balances
splitwise friends                     # List friends
splitwise settle "Nina"               # Record a settlement
splitwise expenses delete 12345       # Delete an expense by ID
```

## Output Modes

Every command supports:
- `--json` — raw JSON (for scripting or piping)
- `--quiet` — minimal output, just IDs/amounts
- `--no-color` — disable color (also respects `NO_COLOR` env var)

## Patterns for Common Tasks

### Log a recurring shared bill
Include the month in the description to avoid confusion:
```bash
splitwise expenses create "Xfinity Internet - March 2026" 51.30
```

### Check before logging (avoid duplicates)
```bash
splitwise expenses list --after 2026-03-01 --limit 50 --json
```
Search the output for matching descriptions before creating.

### Batch-log multiple expenses
Run multiple `splitwise expenses create` commands in sequence. No special syntax.

## Error Handling

- **"not logged in"** → Run `splitwise auth` (needs browser for OAuth)
- **"group not found"** → Verify name with `splitwise groups`
- **"friend not found"** → Verify name with `splitwise friends`
- **Network errors** → Retry once, then report to user

## Key Details

- Group/friend names use case-insensitive partial matching
- Default group (Dolores) means `--group` is optional for Barron & Nina expenses
- Amounts are USD by default (configurable via `splitwise config set default_currency`)
- `--split even` is the default — expense split equally among all group members
- The `--paid-by` flag defaults to the authenticated user (Barron)
