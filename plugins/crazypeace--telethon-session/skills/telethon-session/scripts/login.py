"""Generate a Telethon .session file for user-login to Telegram.

Usage:
    python login.py --api-id 24714103 --api-hash YOUR_HASH --phone +8617776504041

Interactive prompts: SMS/Telegram login code, then 2FA password if enabled.
Output: <session_name>.session (default: telegram_session)
"""
import argparse
import asyncio
from pathlib import Path

from telethon import TelegramClient


async def main(args):
    client = TelegramClient(args.session, args.api_id, args.api_hash)
    await client.start(phone=args.phone)

    me = await client.get_me()
    print(f"\n✅ Login successful")
    print(f"   Name:     {me.first_name} {me.last_name or ''}")
    print(f"   Username: @{me.username or 'N/A'}")
    print(f"   Phone:    {me.phone}")
    print(f"   Session:  {Path(args.session).resolve()}.session")
    await client.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Telethon session file")
    parser.add_argument("--api-id", type=int, required=True, help="Telegram API ID (from my.telegram.org)")
    parser.add_argument("--api-hash", required=True, help="Telegram API hash")
    parser.add_argument("--phone", required=True, help="Phone number with country code, e.g. +86...")
    parser.add_argument("--session", default="telegram_session", help="Session file name (default: telegram_session)")
    asyncio.run(main(parser.parse_args()))
