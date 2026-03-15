from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

DEFAULT_CONFIG = {
    "market": "US",
}


def _config_path() -> Path:
    from_env = os.getenv("STOCK_CLI_CONFIG_PATH")
    if from_env:
        return Path(from_env).expanduser()
    return Path.home() / ".stock-cli" / "config.json"


def load_config() -> dict[str, Any]:
    path = _config_path()
    if not path.exists():
        return dict(DEFAULT_CONFIG)
    try:
        content = path.read_text(encoding="utf-8")
        data = json.loads(content)
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_CONFIG)
    if not isinstance(data, dict):
        return dict(DEFAULT_CONFIG)
    config = dict(DEFAULT_CONFIG)
    config.update(data)
    return config


def save_config(config: dict[str, Any]) -> None:
    path = _config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
