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
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from .chunker import DEFAULT_MAX_CHUNK_TOKENS
from .client import DEFAULT_SERVER
from .mapping import has_tags, load_mapping, save_mapping
from .parallel import DEFAULT_MAX_PARALLEL_REQUESTS, resolve_parallel_workers
from .server_runtime import acquire_server


def _fatal(message: str) -> None:
    """Print a user-facing error and exit."""
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


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
    _fatal("No input text. Use --text, --file, or pipe via stdin.")


def _parse_types(types_str: str) -> List[str]:
    """Parse entity types from JSON array string."""
    try:
        types = json.loads(types_str)
        if not isinstance(types, list):
            raise ValueError
        return [str(t) for t in types]
    except (json.JSONDecodeError, ValueError):
        _fatal('--types must be a JSON array, e.g. \'["人名","地址","电话"]\'')


def _output(
    result: dict,
    pretty: bool = False,
    quiet: bool = False,
    text_key: Optional[str] = None,
) -> None:
    """Output result as JSON, or just the text value in quiet mode.

    Args:
        result: The result dict to output.
        pretty: Pretty-print JSON.
        quiet: If True and *text_key* names a key present in *result*,
               print only that value instead of the full JSON envelope.
        text_key: Explicit field name for quiet-mode extraction (e.g. ``"text"``).
                  Callers that produce non-text results (like ``scan``) should
                  leave this as ``None`` so quiet is a safe no-op.
    """
    if quiet and text_key and text_key in result:
        print(result[text_key])
    elif pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


def _parallel_default() -> int:
    """Read the shared parallel request budget from the environment."""
    raw = os.environ.get("HAS_TEXT_MAX_PARALLEL_REQUESTS")
    if raw is None:
        return DEFAULT_MAX_PARALLEL_REQUESTS

    try:
        value = int(raw)
    except ValueError:
        _fatal("HAS_TEXT_MAX_PARALLEL_REQUESTS must be an integer >= 1")

    if value < 1:
        _fatal("HAS_TEXT_MAX_PARALLEL_REQUESTS must be >= 1")

    return value


def _required_slots(total_requests: int, max_parallel_requests: int) -> int:
    """Clamp server slots to the actual model work for this command."""
    if total_requests <= 0:
        return 0
    return resolve_parallel_workers(total_requests, max_parallel_requests)


def _read_utf8_text_file(path: Path) -> Tuple[Optional[str], Optional[str]]:
    """Read a plaintext file, rejecting binary and non-UTF-8 content."""
    try:
        with path.open("rb") as fh:
            sample = fh.read(8192)
    except OSError as exc:
        return None, str(exc)

    if b"\x00" in sample:
        return None, "binary"

    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError:
        return None, "non_utf8"
    except OSError as exc:
        return None, str(exc)


def _is_within_directory(path: Path, directory: Path) -> bool:
    """Return whether `path` resolves within `directory`."""
    try:
        path.relative_to(directory)
        return True
    except ValueError:
        return False


def _collect_text_documents(dir_path: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """Collect immediate plaintext files from a directory."""
    directory = Path(dir_path)
    if not directory.is_dir():
        _fatal(f"Not a directory: {dir_path}")
    directory_root = directory.resolve()

    documents: List[Dict[str, str]] = []
    skipped: List[Dict[str, str]] = []

    for entry in sorted(directory.iterdir()):
        if not entry.is_file():
            continue
        try:
            resolved_entry = entry.resolve()
        except OSError as exc:
            skipped.append({"file": str(entry), "reason": str(exc)})
            continue
        if not _is_within_directory(resolved_entry, directory_root):
            skipped.append({"file": str(entry), "reason": "symlink_escape"})
            continue
        text, skip_reason = _read_utf8_text_file(entry)
        if text is None:
            skipped.append({"file": str(entry), "reason": skip_reason or "unreadable"})
            continue
        documents.append({"file": str(entry), "text": text})

    return documents, skipped


def _write_text_output(path: Path, text: str) -> None:
    """Write UTF-8 text, creating parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _default_seek_mapping_dir(dir_path: str) -> Path:
    """Return the default per-file mapping directory for batch seek."""
    return Path(dir_path) / "mappings"


def _seek_mapping_path(mapping_dir: Path, source_path: Path) -> Path:
    """Return the per-file mapping path generated by `hide --dir`."""
    return mapping_dir / f"{source_path.name}.mapping.json"


# ======================================================================
# Subcommand: hide
# ======================================================================

def cmd_hide(args: argparse.Namespace) -> None:
    """Execute the hide (anonymize) command."""
    from .commands.hide import (
        HideDocument,
        estimate_hide_batch_request_count,
        run_hide,
        run_hide_batch,
    )

    types = _parse_types(args.types)
    dir_path = getattr(args, "dir", None)

    if dir_path and args.mapping:
        _fatal("hide --dir does not support --mapping; batch hide always writes per-file mappings.")

    existing_mapping = None
    if args.mapping:
        existing_mapping = load_mapping(args.mapping)

    t0 = time.time()
    if dir_path:
        raw_documents, skipped = _collect_text_documents(dir_path)
        documents = [
            HideDocument(source=item["file"], text=item["text"])
            for item in raw_documents
        ]
        required_slots = _required_slots(
            estimate_hide_batch_request_count(documents),
            args.max_parallel_requests,
        )

        if documents and required_slots > 0:
            with acquire_server(
                DEFAULT_SERVER,
                required_slots=required_slots,
            ) as lease:
                client = lease.create_client()
                batch_result = run_hide_batch(
                    client,
                    documents,
                    types,
                    existing_mapping=existing_mapping,
                    max_chunk_tokens=args.max_chunk_tokens,
                    max_parallel_requests=args.max_parallel_requests,
                )
        elif documents:
            batch_result = {
                "results": [
                    {
                        "file": document.source,
                        "text": document.text,
                        "mapping": dict(existing_mapping) if existing_mapping else {},
                    }
                    for document in documents
                ],
                "count": len(documents),
            }
        else:
            batch_result = {"results": [], "count": 0}

        output_dir = Path(args.output_dir or str(Path(dir_path) / "anonymized"))
        mapping_dir = Path(args.mapping_dir or str(output_dir / "mappings"))
        manifest_results: List[Dict[str, Any]] = []

        for item in batch_result["results"]:
            source_path = Path(str(item["file"]))
            output_path = output_dir / source_path.name
            mapping_path = mapping_dir / f"{source_path.name}.mapping.json"
            if output_path.resolve() == source_path.resolve():
                _fatal(f"Refusing to overwrite source file: {source_path}")

            _write_text_output(output_path, str(item["text"]))
            mapping_path.parent.mkdir(parents=True, exist_ok=True)
            save_mapping(item["mapping"], str(mapping_path))

            manifest_item: Dict[str, Any] = {
                "file": str(source_path),
                "output": str(output_path),
                "mapping": str(mapping_path),
            }
            if "chunks" in item:
                manifest_item["chunks"] = item["chunks"]
            manifest_results.append(manifest_item)

        result = {"results": manifest_results, "count": len(manifest_results)}
        if skipped:
            result["skipped"] = skipped
            result["skipped_count"] = len(skipped)
    else:
        text = _read_text(args)
        if text.strip():
            with acquire_server(DEFAULT_SERVER, required_slots=1) as lease:
                client = lease.create_client()
                result = run_hide(
                    client,
                    text,
                    types,
                    existing_mapping=existing_mapping,
                    max_chunk_tokens=args.max_chunk_tokens,
                )
        else:
            result = {"text": "", "mapping": dict(existing_mapping) if existing_mapping else {}}
    result["elapsed_ms"] = round((time.time() - t0) * 1000)

    # Directory mode returns a manifest, not a single text — text_key only
    # applies to single-file hide so quiet safely falls through for --dir.
    _output(
        result,
        pretty=args.pretty,
        quiet=args.quiet,
        text_key="text" if not dir_path else None,
    )


# ======================================================================
# Subcommand: seek
# ======================================================================

def cmd_seek(args: argparse.Namespace) -> None:
    """Execute the seek (restore) command."""
    from .commands.seek import (
        SeekDocument,
        estimate_seek_model_request_count,
        restore_without_model,
        run_seek,
    )

    dir_path = getattr(args, "dir", None)

    t0 = time.time()
    if dir_path:
        if args.mapping:
            _fatal("seek --dir does not support --mapping; use per-file mappings under <dir>/mappings or --mapping-dir.")

        raw_documents, skipped = _collect_text_documents(dir_path)
        documents = [
            SeekDocument(source=item["file"], text=item["text"])
            for item in raw_documents
        ]
        mapping_dir_arg = getattr(args, "mapping_dir", None)
        mapping_dir = Path(mapping_dir_arg) if mapping_dir_arg else _default_seek_mapping_dir(dir_path)

        restored_results: List[Optional[Dict[str, Any]]] = [None] * len(documents)
        pending_documents: List[Tuple[int, SeekDocument, Dict[str, List[str]]]] = []
        missing_mappings: List[str] = []

        for index, document in enumerate(documents):
            source_path = Path(document.source)
            document_mapping: Optional[Dict[str, List[str]]] = None

            per_file_mapping_path = _seek_mapping_path(mapping_dir, source_path)
            if per_file_mapping_path.is_file():
                document_mapping = load_mapping(str(per_file_mapping_path))
            elif has_tags(document.text):
                missing_mappings.append(str(per_file_mapping_path))
                continue

            if document_mapping is None:
                if has_tags(document.text):
                    _fatal(
                        "Batch seek requires per-file mappings under "
                        f"{mapping_dir} for files that still contain anonymized tags."
                    )

                restored_results[index] = {"file": document.source, "text": document.text}
                continue

            restored = restore_without_model(document.text, document_mapping)
            if restored is not None:
                restored_results[index] = {"file": document.source, "text": restored}
            else:
                pending_documents.append((index, document, document_mapping))

        if missing_mappings:
            _fatal(
                "Missing per-file mapping JSON for batch seek: "
                + ", ".join(sorted(missing_mappings))
            )

        if pending_documents:
            request_count = 0
            for _, document, document_mapping in pending_documents:
                try:
                    request_count += estimate_seek_model_request_count(
                        document.text,
                        document_mapping,
                        max_chunk_tokens=args.max_chunk_tokens,
                    )
                except RuntimeError:
                    request_count += 1

            with acquire_server(
                DEFAULT_SERVER,
                required_slots=_required_slots(
                    max(request_count, 1),
                    args.max_parallel_requests,
                ),
            ) as lease:
                client = lease.create_client()
                for index, document, document_mapping in pending_documents:
                    item = run_seek(
                        client,
                        document.text,
                        document_mapping,
                        max_chunk_tokens=args.max_chunk_tokens,
                        max_parallel_requests=args.max_parallel_requests,
                    )
                    item["file"] = document.source
                    restored_results[index] = item

        output_dir = Path(args.output_dir or str(Path(dir_path) / "restored"))
        manifest_results: List[Dict[str, Any]] = []
        for item in restored_results:
            if item is None:
                continue
            source_path = Path(item["file"])
            output_path = output_dir / source_path.name
            if output_path.resolve() == source_path.resolve():
                _fatal(f"Refusing to overwrite source file: {source_path}")
            _write_text_output(output_path, str(item["text"]))

            manifest_item: Dict[str, Any] = {
                "file": str(source_path),
                "output": str(output_path),
            }
            if "chunks" in item:
                manifest_item["chunks"] = item["chunks"]
            manifest_results.append(manifest_item)

        result = {"results": manifest_results, "count": len(manifest_results)}
        if skipped:
            result["skipped"] = skipped
            result["skipped_count"] = len(skipped)
    else:
        if not args.mapping:
            _fatal("seek requires --mapping in single-file mode.")

        mapping = load_mapping(args.mapping)
        text = _read_text(args)
        restored = restore_without_model(text, mapping)
        if restored is not None:
            result = {"text": restored}
        else:
            try:
                request_count = estimate_seek_model_request_count(
                    text,
                    mapping,
                    max_chunk_tokens=args.max_chunk_tokens,
                )
            except RuntimeError:
                request_count = 1

            with acquire_server(
                DEFAULT_SERVER,
                required_slots=_required_slots(request_count, args.max_parallel_requests),
            ) as lease:
                client = lease.create_client()
                result = run_seek(
                    client,
                    text,
                    mapping,
                    max_chunk_tokens=args.max_chunk_tokens,
                    max_parallel_requests=args.max_parallel_requests,
                )
    result["elapsed_ms"] = round((time.time() - t0) * 1000)

    _output(
        result,
        pretty=args.pretty,
        quiet=args.quiet,
        text_key="text" if not dir_path else None,
    )


# ======================================================================
# Subcommand: scan
# ======================================================================

def cmd_scan(args: argparse.Namespace) -> None:
    """Execute the scan (NER) command."""
    from .commands.scan import (
        ScanDocument,
        estimate_scan_batch_request_count,
        estimate_scan_request_count,
        run_scan,
        run_scan_batch,
    )

    types = _parse_types(args.types)
    dir_path = getattr(args, "dir", None)

    t0 = time.time()
    if dir_path:
        raw_documents, skipped = _collect_text_documents(dir_path)
        documents = [
            ScanDocument(source=item["file"], text=item["text"])
            for item in raw_documents
        ]
        request_count = estimate_scan_batch_request_count(
            documents,
            max_chunk_tokens=args.max_chunk_tokens,
        )

        if documents and request_count > 0:
            with acquire_server(
                DEFAULT_SERVER,
                required_slots=_required_slots(request_count, args.max_parallel_requests),
            ) as lease:
                client = lease.create_client()
                result = run_scan_batch(
                    client,
                    documents,
                    types,
                    max_chunk_tokens=args.max_chunk_tokens,
                    max_parallel_requests=args.max_parallel_requests,
                )
        elif documents:
            result = {
                "results": [
                    {"file": document.source, "entities": {}}
                    for document in documents
                ],
                "count": len(documents),
                "summary": {},
            }
        else:
            result = {"results": [], "count": 0, "summary": {}}

        if skipped:
            result["skipped"] = skipped
            result["skipped_count"] = len(skipped)
    else:
        text = _read_text(args)
        request_count = estimate_scan_request_count(
            text,
            max_chunk_tokens=args.max_chunk_tokens,
        )
        if request_count > 0:
            with acquire_server(
                DEFAULT_SERVER,
                required_slots=_required_slots(request_count, args.max_parallel_requests),
            ) as lease:
                client = lease.create_client()
                result = run_scan(
                    client,
                    text,
                    types,
                    max_chunk_tokens=args.max_chunk_tokens,
                    max_parallel_requests=args.max_parallel_requests,
                )
        else:
            result = {"entities": {}}
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
            "  has_text hide --types '[\"人名\"]' --dir docs/ --output-dir anonymized/\n"
            "  has_text seek --mapping mapping.json --text \"<人名[1].个人.姓名>住在...\"\n"
            "  has_text seek --dir anonymized/ --output-dir restored/\n"
            "  has_text seek --dir anonymized/ --mapping-dir exported-mappings/ --output-dir restored/\n"
            '  has_text scan --types \'["人名","电话"]\' --file report.txt\n'
            '  has_text scan --types \'["人名","电话"]\' --dir reports/\n'
            "  cat doc.txt | has_text hide --types '[\"人名\"]'\n"
        ),
    )

    # Global options
    parallel_default = _parallel_default()
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Only output the text field when the command returns text",
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
        "--dir",
        help="Anonymize the immediate plaintext files in a directory (non-recursive)",
    )
    hide_parser.add_argument(
        "--output-dir",
        help="Batch output directory for anonymized files (default: anonymized/ under the input directory)",
    )
    hide_parser.add_argument(
        "--mapping-dir",
        help="Batch output directory for per-file mapping JSON files (default: mappings/ under the output directory)",
    )
    hide_parser.add_argument(
        "--mapping",
        help="Single-file only: existing mapping file path or inline JSON string (for incremental anonymization)",
    )
    hide_parser.add_argument(
        "--max-chunk-tokens",
        type=int,
        default=DEFAULT_MAX_CHUNK_TOKENS,
        help=f"Max tokens per chunk (default: {DEFAULT_MAX_CHUNK_TOKENS})",
    )
    hide_parser.add_argument(
        "--max-parallel-requests",
        "--max-parallel-files",
        type=int,
        dest="max_parallel_requests",
        default=parallel_default,
        help=(
            "Max files to anonymize in parallel when hide uses --dir "
            f"(env: HAS_TEXT_MAX_PARALLEL_REQUESTS, default: {parallel_default}; "
            "deprecated alias: --max-parallel-files)"
        ),
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
        help=(
            "Single-file only: mapping source as a file path or inline JSON string. "
            "seek --dir always uses per-file mappings from <dir>/mappings/ or --mapping-dir."
        ),
    )
    seek_parser.add_argument("--text", help="Anonymized text to restore")
    seek_parser.add_argument("--file", help="Read anonymized text from file")
    seek_parser.add_argument(
        "--dir",
        help="Restore the immediate plaintext files in a directory (non-recursive)",
    )
    seek_parser.add_argument(
        "--mapping-dir",
        help=(
            "Batch mapping directory for per-file mapping JSON files "
            "(default: mappings/ under the input directory)"
        ),
    )
    seek_parser.add_argument(
        "--output-dir",
        help="Batch output directory for restored files (default: restored/ under the input directory)",
    )
    seek_parser.add_argument(
        "--max-chunk-tokens",
        type=int,
        default=DEFAULT_MAX_CHUNK_TOKENS,
        help=f"Max tokens per chunk when seek uses the model (default: {DEFAULT_MAX_CHUNK_TOKENS})",
    )
    seek_parser.add_argument(
        "--max-parallel-requests",
        "--max-parallel-chunks",
        type=int,
        dest="max_parallel_requests",
        default=parallel_default,
        help=(
            "Max model-backed seek chunks to run in parallel "
            f"(env: HAS_TEXT_MAX_PARALLEL_REQUESTS, default: {parallel_default}; "
            "deprecated alias: --max-parallel-chunks)"
        ),
    )
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
        "--dir",
        help="Scan the immediate plaintext files in a directory (non-recursive)",
    )
    scan_parser.add_argument(
        "--max-chunk-tokens",
        type=int,
        default=DEFAULT_MAX_CHUNK_TOKENS,
        help=f"Max tokens per chunk (default: {DEFAULT_MAX_CHUNK_TOKENS})",
    )
    scan_parser.add_argument(
        "--max-parallel-requests",
        "--max-parallel-chunks",
        type=int,
        dest="max_parallel_requests",
        default=parallel_default,
        help=(
            "Max scan chunks to run in parallel "
            f"(env: HAS_TEXT_MAX_PARALLEL_REQUESTS, default: {parallel_default}; "
            "deprecated alias: --max-parallel-chunks)"
        ),
    )
    scan_parser.set_defaults(func=cmd_scan)

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except (OSError, RuntimeError, ValueError) as exc:
        _fatal(str(exc))


if __name__ == "__main__":
    main()
