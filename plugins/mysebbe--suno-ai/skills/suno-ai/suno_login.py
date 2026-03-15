#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from browser_session import (
    DEFAULT_PROFILE_DIR,
    DEFAULT_RAW_COOKIE_FILE,
    ensure_logged_in_browser,
    export_live_chromium_suno_cookies,
    fetch_billing_from_browser,
    launch_browser_runtime,
    persist_context_cookies,
    save_cookie_records,
)
from suno_auth import SunoAuthError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare and validate a persistent Suno browser session."
    )
    parser.add_argument(
        "--raw-cookie-file",
        default=str(DEFAULT_RAW_COOKIE_FILE),
        help="Path to the raw Suno cookie JSON export.",
    )
    parser.add_argument(
        "--profile-dir",
        default=str(DEFAULT_PROFILE_DIR),
        help="Persistent Playwright profile directory for Suno.",
    )
    parser.add_argument(
        "--import-cookies",
        help="Optional raw cookie JSON file to import before validation.",
    )
    parser.add_argument(
        "--export-live-browser",
        action="store_true",
        help="Export current Chromium Suno cookies into the raw cookie file and exit.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable output.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw_cookie_file = Path(args.raw_cookie_file).expanduser().resolve()
    profile_dir = Path(args.profile_dir).expanduser().resolve()

    try:
        if args.export_live_browser:
            cookies = export_live_chromium_suno_cookies()
            save_cookie_records(raw_cookie_file, cookies)
            payload = {
                "ok": True,
                "cookie_file": str(raw_cookie_file),
                "cookie_count": len(cookies),
                "source": "live-chromium",
            }
            print(json.dumps(payload, ensure_ascii=True, indent=2) if args.json else raw_cookie_file)
            return 0

        runtime = launch_browser_runtime(raw_cookie_file=raw_cookie_file, profile_dir=profile_dir)
        try:
            source = ensure_logged_in_browser(
                runtime,
                import_cookie_file=Path(args.import_cookies).expanduser().resolve()
                if args.import_cookies
                else None,
                allow_live_browser_export=True,
            )
            billing = fetch_billing_from_browser(runtime.page)
            persist_context_cookies(runtime.context, raw_cookie_file)
        finally:
            runtime.close()
    except SunoAuthError as exc:
        payload = {"ok": False, "error": str(exc)}
        print(json.dumps(payload, ensure_ascii=True, indent=2) if args.json else str(exc))
        return 1

    payload = {
        "ok": True,
        "source": source,
        "cookie_file": str(raw_cookie_file),
        "profile_dir": str(profile_dir),
        "credits_left": billing.get("total_credits_left") or billing.get("credits"),
        "monthly_usage": billing.get("monthly_usage"),
        "monthly_limit": billing.get("monthly_limit"),
    }
    print(json.dumps(payload, ensure_ascii=True, indent=2) if args.json else "Suno browser session ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
