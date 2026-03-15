#!/usr/bin/env python3
"""Save a Bitrix24 webhook into stable config."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from bitrix24_config import DEFAULT_CONFIG_PATH, load_config, save_config, validate_url  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Save a Bitrix24 webhook into stable config.")
    parser.add_argument("--url", required=True, help="Bitrix24 webhook URL")
    parser.add_argument("--config-file", default=str(DEFAULT_CONFIG_PATH), help="Target config file path")
    parser.add_argument("--force", action="store_true", help="Overwrite existing saved webhook")
    parser.add_argument("--check", action="store_true", help="Run check_webhook.py after saving")
    return parser.parse_args()


def run_check(config_path: Path) -> int:
    script = Path(__file__).with_name("check_webhook.py")
    cmd = [sys.executable, str(script), "--config-file", str(config_path), "--json"]
    result = subprocess.run(cmd, check=False)
    return result.returncode


def main() -> int:
    args = parse_args()
    try:
        normalized = validate_url(args.url)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    config_path = Path(args.config_file).expanduser()
    config = load_config(config_path)
    found = isinstance(config.get("webhook_url"), str) and bool(config.get("webhook_url"))
    if found and not args.force:
        changed = False
    else:
        config["webhook_url"] = normalized
        save_config(config_path, config)
        changed = True

    print(f"saved_to: {config_path}")
    if found and not args.force:
        print("note: saved webhook already existed and was kept unchanged; use --force to replace it")
    elif found and args.force:
        print("note: existing saved webhook was replaced")
    elif changed:
        print("note: webhook was saved")

    if args.check:
        return run_check(config_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
