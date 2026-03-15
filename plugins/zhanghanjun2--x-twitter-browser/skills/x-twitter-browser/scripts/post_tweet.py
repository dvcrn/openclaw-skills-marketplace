#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from session_lib import (
    cookie_header_to_storage_state,
    ensure_playwright_browser_hint,
    load_cookie_header,
    require_playwright,
)


HOME_URL = "https://x.com/home"
COMPOSE_URL = "https://x.com/compose/post"
LOGIN_HINTS = (
    "/i/flow/login",
    "/login",
    "/account/access",
    "/account/login_challenge",
)
EDITOR_SELECTOR = '[data-testid="tweetTextarea_0"]'
POST_BUTTON_SELECTOR = '[data-testid="tweetButton"]'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Post to X with Playwright browser auth")
    parser.add_argument("--cookie-header", help="Raw Cookie header string")
    parser.add_argument("--cookie-file", help="File containing raw Cookie header string")
    parser.add_argument("--text", help="Tweet text")
    parser.add_argument("--text-file", help="Read tweet text from file")
    parser.add_argument("--verify-only", action="store_true", help="Only verify the session")
    parser.add_argument("--timeout-ms", type=int, default=30000, help="Timeout per operation in ms (default: 30000)")
    parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Run Chromium headless (default: False). Use --headless for headless mode.",
    )
    return parser.parse_args()


def load_text(args: argparse.Namespace) -> str:
    if args.text:
        return args.text
    if args.text_file:
        return Path(args.text_file).read_text(encoding="utf-8").strip()
    return ""


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


def open_compose(page: Any, timeout_ms: int) -> None:
    page.goto(COMPOSE_URL, wait_until="domcontentloaded", timeout=timeout_ms)


def post_text(page: Any, text: str, timeout_ms: int) -> None:
    editor = page.locator(EDITOR_SELECTOR).nth(0)
    editor.wait_for(state="visible", timeout=timeout_ms)
    editor.click()
    # Use press_sequentially instead of fill() so # and @ trigger autocomplete
    # correctly; fill() inserts all at once and can leave dropdown stuck.
    editor.press_sequentially(text, delay=60)
    page.wait_for_timeout(300)
    # Only press Escape when #/@ may have opened a dropdown; otherwise Escape
    # closes the compose window and triggers "Save post?" draft popup.
    if "#" in text or "@" in text:
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)

    button = page.locator(POST_BUTTON_SELECTOR).first
    page.wait_for_function(
        """
        selector => {
          const element = document.querySelector(selector);
          return !!element && element.getAttribute('aria-disabled') !== 'true' && !element.disabled;
        }
        """,
        arg=POST_BUTTON_SELECTOR,
        timeout=timeout_ms,
    )
    button.click()


def main() -> None:
    args = parse_args()
    text = load_text(args)
    if not args.verify_only and not text:
        raise SystemExit("Provide --text or --text-file unless using --verify-only")

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
       # "--disable-extensions",
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

            open_compose(page, args.timeout_ms)
            post_text(page, text, args.timeout_ms)
            page.wait_for_timeout(5000)
            print("Post flow executed. Check the timeline to confirm delivery.")
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
