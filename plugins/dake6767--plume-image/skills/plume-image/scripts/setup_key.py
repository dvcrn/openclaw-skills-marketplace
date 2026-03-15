#!/usr/bin/env python3
"""
Write PLUME_API_KEY to ~/.openclaw/.env
Usage: python3 setup_key.py <api_key>
Output: OK / ERROR: <reason>
"""

import os
import sys
import re


def main():
    if len(sys.argv) < 2:
        print("ERROR: missing api_key argument")
        print("Usage: python3 setup_key.py <api_key>")
        sys.exit(1)

    api_key = sys.argv[1].strip()
    if not api_key:
        print("ERROR: api_key cannot be empty")
        sys.exit(1)

    env_path = os.path.expanduser("~/.openclaw/.env")

    # Ensure directory exists
    os.makedirs(os.path.dirname(env_path), exist_ok=True)

    # Read existing content
    existing = ""
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            existing = f.read()

    if re.search(r"^PLUME_API_KEY=", existing, re.MULTILINE):
        # Update existing key
        new_content = re.sub(
            r"^PLUME_API_KEY=.*$",
            f"PLUME_API_KEY={api_key}",
            existing,
            flags=re.MULTILINE,
        )
    else:
        # Append new key
        new_content = existing
        if existing and not existing.endswith("\n"):
            new_content += "\n"
        new_content += f"PLUME_API_KEY={api_key}\n"

    with open(env_path, "w") as f:
        f.write(new_content)

    print("OK")


if __name__ == "__main__":
    main()
