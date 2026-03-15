#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path


ALLOWED_TYPES = {"paper", "benchmark", "dataset", "official_doc", "repo"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Conservatively verify fetched source-note drafts. This step only upgrades notes "
            "when page-level metadata facts are present and fetch status is review-ready."
        )
    )
    parser.add_argument("inputs", nargs="+", help="Source-note markdown files to verify.")
    parser.add_argument("--output-dir", required=True, help="Directory for verified note outputs.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    for value in args.inputs:
        source = Path(value).expanduser().resolve()
        if not source.exists():
            continue
        text = source.read_text(encoding="utf-8")
        verified = verify_note(text)
        target = output_dir / source.name
        target.write_text(verified, encoding="utf-8")
        print(target)

    return 0


def verify_note(text: str) -> str:
    lines = text.splitlines()
    source_type = field_value(lines, "- Source type:")
    verification = field_value(lines, "- Verification status:")
    facts = [line for line in lines if line.startswith("- Fact:")]
    semantic_facts = [
        line
        for line in facts
        if any(
            token in line.lower()
            for token in [
                "candidate benchmark/task fact:",
                "candidate evaluation fact:",
                "candidate metric fact:",
            ]
        )
    ]

    should_verify = (
        source_type in ALLOWED_TYPES
        and verification == "fetched-primary-review-required"
        and (
            (len(semantic_facts) >= 1 and all("TODO:" not in line for line in semantic_facts[:1]))
            or (len(facts) >= 2 and all("TODO:" not in line for line in facts[:2]))
        )
    )

    if not should_verify:
        return text

    updated: list[str] = []
    for line in lines:
        if line.startswith("- Verification status:"):
            updated.append("- Verification status: verified-page-metadata")
        else:
            updated.append(line)
    return "\n".join(updated) + ("\n" if text.endswith("\n") else "")


def field_value(lines: list[str], prefix: str) -> str:
    for line in lines:
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip().lower()
    return ""


if __name__ == "__main__":
    raise SystemExit(main())
