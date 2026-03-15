#!/usr/bin/env python3
"""
Fetch vidu task by ID and output nomark_uri(s) or error info.

Usage:
  export VIDU_TOKEN=your_token
  python get_task_result.py <task_id>

Output: one JSON object per line to stdout:
  On success: {"nomark_uri": "https://...", "creation_id": ...} for each creation (or single line with nomark_uris array).
  On failed: {"state": "failed", "err_code": "...", "err_msg": "..."}
Exit: 0 if success and at least one nomark_uri, else 1.
"""

import json
import os
import sys

try:
    import requests
except ImportError:
    print("install requests: pip install requests", file=sys.stderr)
    sys.exit(1)

BASE_URL = os.environ.get("VIDU_BASE_URL", "https://service.vidu.cn").rstrip("/")
TOKEN = os.environ.get("VIDU_TOKEN", "")
HEADERS = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": f"viduclawbot/1.0 (+{BASE_URL})",
}


def main() -> int:
    if not TOKEN:
        print("VIDU_TOKEN is not set", file=sys.stderr)
        return 1
    if len(sys.argv) < 2:
        print("Usage: get_task_result.py <task_id>", file=sys.stderr)
        return 1

    task_id = sys.argv[1]
    url = f"{BASE_URL}/vidu/v1/tasks/{task_id}"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    task = r.json()

    state = task.get("state", "")
    if state == "success":
        creations = task.get("creations") or []
        uris = []
        for c in creations:
            nomark = c.get("nomark_uri")
            if nomark:
                uris.append(nomark)
                print(json.dumps({"nomark_uri": nomark, "creation_id": c.get("id")}))
        if not uris:
            print(json.dumps({"state": state, "error": "no nomark_uri in creations"}), file=sys.stderr)
            return 1
        return 0
    else:
        out = {"state": state}
        if task.get("err_code"):
            out["err_code"] = task["err_code"]
        if task.get("err_msg"):
            out["err_msg"] = task["err_msg"]
        print(json.dumps(out), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
