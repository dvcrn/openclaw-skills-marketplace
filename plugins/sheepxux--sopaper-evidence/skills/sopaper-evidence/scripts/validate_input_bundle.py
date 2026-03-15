#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path


SCHEMAS = {
    "source-note": ["## Title", "## Source", "Verification status:", "## Why it matters", "## Key facts", "## Limits"],
    "claims": ["- Claim:", "Claim type:", "Current status:"],
    "result-artifact": ["## Artifact", "Artifact type:", "Path:", "Metric:", "Provenance:"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a structured Sopaper Evidence input file against a lightweight schema."
    )
    parser.add_argument("schema", choices=sorted(SCHEMAS.keys()))
    parser.add_argument("file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.file).expanduser().resolve()
    if not path.exists():
        print(f"Missing input: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    missing = [item for item in SCHEMAS[args.schema] if item not in text]
    if missing:
        print("invalid")
        for item in missing:
            print(f"- missing: {item}")
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
