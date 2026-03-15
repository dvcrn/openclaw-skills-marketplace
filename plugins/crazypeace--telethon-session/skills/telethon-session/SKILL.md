---
name: telethon-session
description: "Generate Telethon .session files for user-account login to Telegram. Use when: (1) user wants to test a Telegram bot as a real user, (2) user needs to interact with Telegram via user identity, (3) creating a Telegram session for Telethon-based automation, (4) mentions telethon, telegram session, or user-account login. NOT for: bot-token-based bots (no session needed)."
---

# Telethon Session Generator

Generate a `.session` file to authenticate a Telegram user account via Telethon.

## Prerequisites

- `telethon` — install with `pip install telethon` (use venv if needed)
- API credentials from <https://my.telegram.org> (api_id + api_hash)

## Quick Start

Run the bundled script in interactive (PTY) mode — Telegram will send a login code and optionally ask for 2FA:

```bash
python3 scripts/login.py --api-id YOUR_ID --api-hash YOUR_HASH --phone "+86..."
```

The script prompts for:
1. **Login code** — from Telegram app or SMS
2. **2FA password** — only if enabled on the account

On success, `<session_name>.session` is created in the working directory.

## Key Notes

- **Session file is reusable** — no need to re-login unless Telegram invalidates it
- **Do NOT commit `.session` files** to version control (treat as secrets)
- **Bot token ≠ session** — bots use `bot_token=` in Telethon, no session file needed
- If `pip install telethon` fails on externally-managed Python, use a venv:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install telethon
  ```

## Using the Session File

```python
from telethon import TelegramClient

client = TelegramClient('telegram_session', api_id, api_hash)
await client.start()  # auto-loads session, no prompt needed
```
