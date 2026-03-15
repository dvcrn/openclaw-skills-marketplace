"""Shared utilities for antigravity-bridge scripts."""

import json
import os

CONFIG_PATH = os.path.expanduser("~/.openclaw/antigravity-bridge.json")


def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(
            f"Config not found at {CONFIG_PATH}\nRun: python3 scripts/configure.py"
        )
    with open(CONFIG_PATH) as f:
        return json.load(f)


def safe_load_json(path: str) -> dict | None:
    """Load JSON, handling trailing markdown artifacts."""
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(path) as f:
            raw = f.read().strip()
        try:
            last_brace = raw.rindex("}")
            return json.loads(raw[:last_brace + 1])
        except (ValueError, json.JSONDecodeError):
            return None
