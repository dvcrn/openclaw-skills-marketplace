#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""has_text — CLI tool for text anonymization and restoration.

Usage:
    has_text hide  --types '["人名","地址"]' --text "..."
    has_text seek  --mapping mapping.json --text "..."
    has_text scan  --types '["人名","地址"]' --text "..."

See `has_text <command> --help` for details.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import List, Optional

from .client import HaSClient, DEFAULT_SERVER
from .mapping import load_mapping
from .chunker import DEFAULT_MAX_CHUNK_TOKENS


def _read_text(args: argparse.Namespace) -> str:
    """Read input text from --text, --file, or stdin."""
    if hasattr(args, "text") and args.text:
        return args.text
    if hasattr(args, "file") and args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            return f.read()
    # Try stdin
    if not sys.stdin.isatty():
        return sys.stdin.read()
    print("Error: No input text. Use --text, --file, or pipe via stdin.", file=sys.stderr)
    sys.exit(1)


def _parse_types(types_str: str) -> List[str]:
    """Parse entity types from JSON array string."""
    try:
        types = json.loads(types_str)
        if not isinstance(types, list):
            raise ValueError
        return [str(t) for t in types]
    except (json.JSONDecodeError, ValueError):
        print(
            f'Error: --types must be a JSON array, e.g. \'["人名","地址","电话"]\'',
            file=sys.stderr,
        )
        sys.exit(1)


def _output(result: dict, pretty: bool = False, quiet: bool = False) -> None:
    """Output result as JSON."""
    if quiet:
        # Only output the text field
        print(result.get("text", ""))
    elif pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


# ======================================================================
# Subcommand: hide
# ======================================================================

def cmd_hide(args: argparse.Namespace) -> None:
    """Execute the hide (anonymize) command."""
    from .commands.hide import run_hide

    client = HaSClient(args.server)
    text = _read_text(args)
    types = _parse_types(args.types)

    existing_mapping = None
    if args.mapping:
        existing_mapping = load_mapping(args.mapping)

    t0 = time.time()
    result = run_hide(
        client,
        text,
        types,
        existing_mapping=existing_mapping,
        max_chunk_tokens=args.max_chunk_tokens,
    )
    result["elapsed_ms"] = round((time.time() - t0) * 1000)

    _output(result, pretty=args.pretty, quiet=args.quiet)


# ======================================================================
# Subcommand: seek
# ======================================================================

def cmd_seek(args: argparse.Namespace) -> None:
    """Execute the seek (restore) command."""
    from .commands.seek import run_seek

    client = HaSClient(args.server)
    text = _read_text(args)
    mapping = load_mapping(args.mapping)

    t0 = time.time()
    result = run_seek(client, text, mapping)
    result["elapsed_ms"] = round((time.time() - t0) * 1000)

    _output(result, pretty=args.pretty, quiet=args.quiet)


# ======================================================================
# Subcommand: scan
# ======================================================================

def cmd_scan(args: argparse.Namespace) -> None:
    """Execute the scan (NER) command."""
    from .commands.scan import run_scan

    client = HaSClient(args.server)
    text = _read_text(args)
    types = _parse_types(args.types)

    t0 = time.time()
    result = run_scan(
        client,
        text,
        types,
        max_chunk_tokens=args.max_chunk_tokens,
    )
    result["elapsed_ms"] = round((time.time() - t0) * 1000)

    _output(result, pretty=args.pretty, quiet=args.quiet)


# ======================================================================
# Argument parser
# ======================================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="has_text",
        description="HaS (Hide and Seek) — Text anonymization and restoration CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  has_text hide --types \'["人名","地址"]\' --text "张三住在北京市朝阳区"\n'
            "  has_text hide --types '[\"人名\"]' --file document.txt --mapping prev.json\n"
            "  has_text seek --mapping mapping.json --text \"<人名[1].个人.姓名>住在...\"\n"
            '  has_text scan --types \'["人名","电话"]\' --file report.txt\n'
            "  cat doc.txt | has_text hide --types '[\"人名\"]'\n"
        ),
    )

    # Global options
    server_default = os.environ.get("HAS_TEXT_SERVER", DEFAULT_SERVER)
    parser.add_argument(
        "--server",
        default=server_default,
        help=f"llama-server URL (env: HAS_TEXT_SERVER, default: {DEFAULT_SERVER})",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Only output the text field, no JSON wrapper",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- hide ---
    hide_parser = subparsers.add_parser(
        "hide",
        help="Anonymize text (replace entities with privacy tags)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    hide_parser.add_argument(
        "--types",
        required=True,
        help='Entity types to anonymize (JSON array), e.g. \'["人名","地址","电话"]\'',
    )
    hide_parser.add_argument("--text", help="Text to anonymize")
    hide_parser.add_argument("--file", help="Read text from file")
    hide_parser.add_argument(
        "--mapping",
        help="Existing mapping: file path or inline JSON string (for incremental anonymization)",
    )
    hide_parser.add_argument(
        "--max-chunk-tokens",
        type=int,
        default=DEFAULT_MAX_CHUNK_TOKENS,
        help=f"Max tokens per chunk (default: {DEFAULT_MAX_CHUNK_TOKENS})",
    )
    hide_parser.set_defaults(func=cmd_hide)

    # --- seek ---
    seek_parser = subparsers.add_parser(
        "seek",
        help="Restore anonymized text to original form",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    seek_parser.add_argument(
        "--mapping",
        required=True,
        help="Mapping source: file path or inline JSON string",
    )
    seek_parser.add_argument("--text", help="Anonymized text to restore")
    seek_parser.add_argument("--file", help="Read anonymized text from file")
    seek_parser.set_defaults(func=cmd_seek)

    # --- scan ---
    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan text for sensitive entities (NER only, no anonymization)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    scan_parser.add_argument(
        "--types",
        required=True,
        help='Entity types to scan for (JSON array), e.g. \'["人名","地址","电话"]\'',
    )
    scan_parser.add_argument("--text", help="Text to scan")
    scan_parser.add_argument("--file", help="Read text from file")
    scan_parser.add_argument(
        "--max-chunk-tokens",
        type=int,
        default=DEFAULT_MAX_CHUNK_TOKENS,
        help=f"Max tokens per chunk (default: {DEFAULT_MAX_CHUNK_TOKENS})",
    )
    scan_parser.set_defaults(func=cmd_scan)

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
