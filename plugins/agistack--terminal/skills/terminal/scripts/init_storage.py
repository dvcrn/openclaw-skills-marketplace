#!/usr/bin/env python3
import json
import os
from datetime import datetime

BASE_DIR = os.path.expanduser("~/.openclaw/workspace/memory/terminal")
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")

def write_json_if_missing(path, payload):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

def main():
    os.makedirs(BASE_DIR, exist_ok=True)
    write_json_if_missing(HISTORY_FILE, {
        "metadata": {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        },
        "runs": []
    })
    print("✓ Terminal storage initialized")
    print(f"  {HISTORY_FILE}")

if __name__ == "__main__":
    main()
