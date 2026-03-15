#!/usr/bin/env python3
"""Shared helpers for Bitrix24 skill scripts."""

from __future__ import annotations

import json
import re
from pathlib import Path

WEBHOOK_RE = re.compile(r"^https://(?P<host>[^/]+)/rest/(?P<user_id>\d+)/(?P<secret>[^/]+)/?$")
DEFAULT_CONFIG_PATH = Path.home() / ".config" / "bitrix24-skill" / "config.json"


def normalize_url(value: str) -> str:
    return value.strip().strip('"').strip("'").rstrip("/") + "/"


def validate_url(value: str) -> str:
    normalized = normalize_url(value)
    if not WEBHOOK_RE.match(normalized):
        raise ValueError("Webhook format is invalid. Expected https://<host>/rest/<user_id>/<secret>/")
    return normalized


def mask_url(value: str) -> str:
    match = WEBHOOK_RE.match(value)
    if not match:
        return value
    secret = match.group("secret")
    if len(secret) <= 4:
        masked = "*" * len(secret)
    else:
        masked = f"{secret[:2]}***{secret[-2:]}"
    return f"https://{match.group('host')}/rest/{match.group('user_id')}/{masked}/"


def load_config(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def save_config(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def persist_url_to_config(url: str, config_file: str | None = None) -> Path:
    config_path = Path(config_file).expanduser() if config_file else DEFAULT_CONFIG_PATH
    config = load_config(config_path)
    config["webhook_url"] = validate_url(url)
    save_config(config_path, config)
    return config_path


def load_url(
    *,
    cli_url: str | None,
    config_file: str | None = None,
) -> tuple[str | None, str]:
    if cli_url:
        return cli_url, "arg:url"

    config_path = Path(config_file).expanduser() if config_file else DEFAULT_CONFIG_PATH
    config = load_config(config_path)
    config_url = config.get("webhook_url")
    if isinstance(config_url, str) and config_url.strip():
        return config_url, f"config:{config_path}"

    return None, "missing"


def get_cached_user(config_file: str | None = None) -> dict | None:
    """Return cached user data (user_id, timezone) or None."""
    config_path = Path(config_file).expanduser() if config_file else DEFAULT_CONFIG_PATH
    config = load_config(config_path)
    user_id = config.get("user_id")
    if user_id is not None:
        return {"user_id": user_id, "timezone": config.get("timezone", "")}
    return None


def cache_user_data(user_id: int, timezone: str = "", config_file: str | None = None) -> None:
    """Save user_id and timezone to config for reuse."""
    config_path = Path(config_file).expanduser() if config_file else DEFAULT_CONFIG_PATH
    config = load_config(config_path)
    config["user_id"] = user_id
    if timezone:
        config["timezone"] = timezone
    save_config(config_path, config)
