---
name: raiffeisen-elba
description: "Automate Raiffeisen ELBA online banking: login/logout, list accounts, and fetch transactions via Playwright."
homepage: https://github.com/odrobnik/raiffeisen-elba-skill
---

# Raiffeisen ELBA Banking Automation

Fetch current account balances, securities depot positions, and transactions for all account types in JSON format for automatic processing. Uses Playwright to automate Raiffeisen ELBA online banking.

**Entry point:** `{baseDir}/scripts/elba.py`

## Setup

See [SETUP.md](SETUP.md) for prerequisites and setup instructions.

## Commands

```bash
python3 {baseDir}/scripts/elba.py login
python3 {baseDir}/scripts/elba.py logout
python3 {baseDir}/scripts/elba.py accounts
python3 {baseDir}/scripts/elba.py transactions --account <iban> --from YYYY-MM-DD --until YYYY-MM-DD
```

## Recommended Flow

```
login → accounts → transactions → portfolio → logout
```

Always call `logout` after completing all operations to clear the stored browser session (cookies, local storage, Playwright profile). This minimizes persistent auth state on disk.
