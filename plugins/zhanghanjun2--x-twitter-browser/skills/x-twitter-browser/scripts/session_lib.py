#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote


DEFAULT_COOKIE_DOMAIN = ".x.com"
CONFIG_DIR = Path.home() / ".x-twitter-browser"
CONFIG_PATH = CONFIG_DIR / "config.json"


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def save_config(config: dict[str, Any]) -> Path:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return CONFIG_PATH


def parse_cookie_header(cookie_header: str) -> dict[str, str]:
    cookies: dict[str, str] = {}
    for item in cookie_header.split(";"):
        part = item.strip()
        if not part or "=" not in part:
            continue
        name, value = part.split("=", 1)
        name = name.strip()
        value = value.strip()
        if not name:
            continue
        cookies[name] = value
    return cookies


def cookie_header_to_storage_state(
    cookie_header: str,
    domain: str = DEFAULT_COOKIE_DOMAIN,
) -> dict[str, Any]:
    parsed = parse_cookie_header(cookie_header)
    cookies = []
    for name, value in parsed.items():
        secure = name not in {"lang", "g_state", "__cuid"}
        cookies.append(
            {
                "name": name,
                "value": value,
                "domain": domain,
                "path": "/",
                "expires": -1,
                "httpOnly": False,
                "secure": secure,
                "sameSite": "Lax",
            }
        )

    origins = []
    if "g_state" in parsed:
        origins.append(
            {
                "origin": "https://x.com",
                "localStorage": [
                    {
                        "name": "g_state",
                        "value": unquote(parsed["g_state"]),
                    }
                ],
            }
        )

    return {
        "cookies": cookies,
        "origins": origins,
    }


def load_cookie_header(cookie_header: str | None, cookie_file: str | None) -> str:
    if cookie_header:
        return cookie_header.strip()
    if cookie_file:
        return Path(cookie_file).expanduser().read_text(encoding="utf-8").strip()
    config = load_config()
    if config.get("cookie_header"):
        return config["cookie_header"].strip()
    raise FileNotFoundError(
        "No cookie header provided. Save one with save_cookie_header.py or set cookie_header in ~/.x-twitter-browser/config.json"
    )


def save_cookie_to_config(cookie_header: str) -> Path:
    config = load_config()
    config["cookie_header"] = cookie_header.strip()
    return save_config(config)


def require_playwright() -> Any:
    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Missing dependency: playwright. Install it first, then run this skill again."
        ) from exc
    return sync_playwright


def _default_playwright_browsers_path() -> Path:
    home = Path.home()
    if sys.platform == "darwin":
        return home / "Library" / "Caches" / "ms-playwright"
    if sys.platform == "win32":
        return home / "AppData" / "Local" / "ms-playwright"
    return home / ".cache" / "ms-playwright"


def ensure_playwright_browser_hint() -> None:
    env_path = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    browsers_path = Path(env_path) if env_path else _default_playwright_browsers_path()
    if not browsers_path.exists():
        raise SystemExit(
            "Playwright browser binaries are not installed. Run `python3 -m playwright install chromium` first."
        )
