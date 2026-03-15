#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from typing import Any

from session_lib import (
    cookie_header_to_storage_state,
    ensure_playwright_browser_hint,
    load_cookie_header,
    require_playwright,
)


HOME_URL = "https://x.com/home"
LOGIN_HINTS = (
    "/i/flow/login",
    "/login",
    "/account/access",
    "/account/login_challenge",
)


def extract_tweet_id(url_or_id: str) -> str:
    s = url_or_id.strip()
    match = re.search(r"/status/(\d+)", s)
    if match:
        return match.group(1)
    if s.isdigit():
        return s
    raise ValueError(f"Cannot extract tweet ID from: {url_or_id}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bookmark or remove bookmark from an X tweet with Playwright browser auth")
    parser.add_argument("--tweet", required=True, help="Tweet URL (e.g. https://x.com/user/status/123) or tweet ID")
    parser.add_argument("--undo", action="store_true", help="Remove bookmark instead of adding")
    parser.add_argument("--cookie-header", help="Raw Cookie header string")
    parser.add_argument("--cookie-file", help="File containing raw Cookie header string")
    parser.add_argument("--verify-only", action="store_true", help="Only verify the session")
    parser.add_argument("--timeout-ms", type=int, default=30000, help="Timeout per operation in ms (default: 30000)")
    parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Run Chromium headless (default: False). Use --headless for headless mode.",
    )
    return parser.parse_args()


def resolve_storage_state(args: argparse.Namespace) -> dict[str, Any]:
    cookie_header = load_cookie_header(args.cookie_header, args.cookie_file)
    return cookie_header_to_storage_state(cookie_header)


def looks_logged_out(page: Any) -> bool:
    url = page.url.lower()
    if any(hint in url for hint in LOGIN_HINTS):
        return True
    title = page.title().lower()
    if "login" in title:
        return True
    content = page.content().lower()
    return "sign in to x" in content or "log in to x" in content


def verify_session(page: Any, timeout_ms: int) -> None:
    page.goto(HOME_URL, wait_until="domcontentloaded", timeout=timeout_ms)
    page.wait_for_timeout(3000)
    if looks_logged_out(page):
        raise RuntimeError("Imported session is not authenticated")


def open_tweet_and_bookmark(page: Any, tweet_url: str, tweet_id: str, undo: bool, timeout_ms: int) -> None:
    if "/status/" in tweet_url:
        page.goto(tweet_url, wait_until="domcontentloaded", timeout=timeout_ms)
    else:
        page.goto(f"https://x.com/i/status/{tweet_id}", wait_until="domcontentloaded", timeout=timeout_ms)
    page.wait_for_timeout(3000)

    if undo:
        btn = page.locator(
            '[data-testid="removeBookmark"], [aria-label="Remove bookmark"]'
        ).or_(page.get_by_text("Remove post from Bookmarks")).first
    else:
        btn = page.locator(
            '[data-testid="bookmark"], [aria-label="Add bookmark"], [aria-label="Bookmark"]'
        ).or_(page.get_by_text("Add post to Bookmarks")).first
    btn.wait_for(state="visible", timeout=timeout_ms)
    btn.scroll_into_view_if_needed()
    btn.click()


def main() -> None:
    args = parse_args()
    tweet_input = args.tweet.strip()
    tweet_id = extract_tweet_id(tweet_input)

    storage_state = resolve_storage_state(args)

    sync_playwright = require_playwright()
    if sys.platform != "darwin":
        ensure_playwright_browser_hint()

    chromium_args = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-software-rasterizer",
        "--disable-setuid-sandbox",
        "--disable-extensions",
        "--disable-background-networking",
        "--disable-default-apps",
        "--disable-sync",
        "--no-first-run",
        "--no-zygote",
        "--disable-features=TranslateUI",
    ]

    with sync_playwright() as playwright:
        launch_options: dict[str, Any] = {
            "headless": args.headless,
            "args": chromium_args,
        }
        if sys.platform == "darwin":
            launch_options["channel"] = "chrome"
        try:
            browser = playwright.chromium.launch(**launch_options)
        except Exception:
            if "channel" in launch_options:
                del launch_options["channel"]
                ensure_playwright_browser_hint()
                browser = playwright.chromium.launch(**launch_options)
            else:
                raise
        context = browser.new_context(
            storage_state=storage_state,
            viewport={"width": 1440, "height": 900},
            locale="en-US",
            timezone_id="UTC",
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
            ),
        )
        context.set_default_timeout(args.timeout_ms)
        page = context.new_page()

        try:
            verify_session(page, args.timeout_ms)
            print(f"Session looks valid: {page.url}")

            if args.verify_only:
                return

            tweet_url = tweet_input if "/status/" in tweet_input else f"https://x.com/i/status/{tweet_id}"
            open_tweet_and_bookmark(page, tweet_url, tweet_id, args.undo, args.timeout_ms)
            page.wait_for_timeout(2000)
            action = "Remove bookmark" if args.undo else "Bookmark"
            print(f"{action} flow executed. Check the tweet or Bookmarks to confirm.")
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
