#!/usr/bin/env python3
"""Convert CHANGELOG.md to docs/changelog.json for the landing page.

Usage: python3 scripts/changelog_to_json.py <current_version>

Parses CHANGELOG.md format:
  ## 0.15.4 — 2026-03-11
  ### Added
  - **Feature name**: description

Outputs docs/changelog.json:
  {"version": "0.15.4", "entries": [{"version": "0.15.4", "date": "2026-03-11", "items": [...]}]}
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHANGELOG = ROOT / "CHANGELOG.md"
OUTPUT = ROOT / "docs" / "changelog.json"

VERSION_RE = re.compile(r"^## (\d+\.\d+\.\d+)\s*[—–-]\s*(\d{4}-\d{2}-\d{2})")
SECTION_RE = re.compile(r"^### (.+)")
ITEM_RE = re.compile(r"^- \*\*(.+?)\*\*:\s*(.+)")
ITEM_PLAIN_RE = re.compile(r"^- (.+)")


def parse_changelog() -> list[dict]:
    if not CHANGELOG.exists():
        return []

    entries = []
    current: dict | None = None
    section = ""

    for line in CHANGELOG.read_text(encoding="utf-8").splitlines():
        line = line.rstrip()

        vm = VERSION_RE.match(line)
        if vm:
            if current:
                entries.append(current)
            current = {"version": vm.group(1), "date": vm.group(2), "items": []}
            section = ""
            continue

        sm = SECTION_RE.match(line)
        if sm:
            section = sm.group(1)
            continue

        if current is None:
            continue

        im = ITEM_RE.match(line)
        if im:
            current["items"].append({
                "section": section,
                "title": im.group(1),
                "description": im.group(2),
            })
            continue

        ip = ITEM_PLAIN_RE.match(line)
        if ip:
            current["items"].append({
                "section": section,
                "title": "",
                "description": ip.group(1),
            })

    if current:
        entries.append(current)

    return entries


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else ""
    entries = parse_changelog()

    data = {
        "version": version or (entries[0]["version"] if entries else ""),
        "entries": entries[:10],  # Last 10 releases
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Generated {OUTPUT} ({len(entries)} releases, showing {len(data['entries'])})")


if __name__ == "__main__":
    main()
