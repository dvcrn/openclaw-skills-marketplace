#!/usr/bin/env python3
"""
Validate if PLUME_API_KEY is valid
Output: VALID / INVALID
"""

import sys
import os
import re

# Add current directory to path for importing plume_api
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def get_api_key():
    """Get API Key from .env, openclaw.json, or environment variable"""
    # 1. Check .env file
    env_path = os.path.expanduser("~/.openclaw/.env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("PLUME_API_KEY="):
                    return line.strip().split("=", 1)[1]

    # 2. Check openclaw.json
    import json
    cfg_path = os.path.expanduser("~/.openclaw/openclaw.json")
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, "r") as f:
                text = f.read()
            text = re.sub(r",\s*([}\]])", r"\1", text)
            cfg = json.loads(text)
            key = cfg.get("env", {}).get("vars", {}).get("PLUME_API_KEY")
            if key:
                return key
        except (json.JSONDecodeError, OSError):
            pass

    # 3. Check environment variable
    return os.environ.get("PLUME_API_KEY")


try:
    api_key = get_api_key()
    if not api_key:
        print("INVALID")
        sys.exit(1)

    # Call validation endpoint
    import ssl
    import urllib.request
    import json

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        "https://design.useplume.app/api/open/validate",
        headers={
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json",
        },
    )

    resp = urllib.request.urlopen(req, timeout=10, context=ctx)
    result = json.loads(resp.read().decode("utf-8"))

    if result.get("success") and result.get("data", {}).get("valid"):
        print("VALID")
        sys.exit(0)
    else:
        print("INVALID")
        sys.exit(1)

except Exception as e:
    # Any exception is treated as invalid
    print("INVALID")
    sys.exit(1)
