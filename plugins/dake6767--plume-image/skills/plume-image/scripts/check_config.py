#!/usr/bin/env python3
"""
Check if PLUME_API_KEY is configured
Output: CONFIGURED / NOT_CONFIGURED
"""

import json
import re
import os
import sys


def _load_openclaw_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return json.loads(text)


def main():
    key = None

    # 1. Check ~/.openclaw/.env
    env_path = os.path.expanduser("~/.openclaw/.env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("PLUME_API_KEY="):
                    key = line.strip().split("=", 1)[1]
                    break

    # 2. Check ~/.openclaw/openclaw.json
    if not key:
        cfg_path = os.path.expanduser("~/.openclaw/openclaw.json")
        if os.path.exists(cfg_path):
            try:
                cfg = _load_openclaw_json(cfg_path)
                key = cfg.get("env", {}).get("vars", {}).get("PLUME_API_KEY")
            except (json.JSONDecodeError, OSError):
                pass

    # 3. Check environment variable
    if not key:
        key = os.environ.get("PLUME_API_KEY")

    if key:
        print("CONFIGURED")
        sys.exit(0)
    else:
        print("NOT_CONFIGURED")
        sys.exit(1)


if __name__ == "__main__":
    main()
