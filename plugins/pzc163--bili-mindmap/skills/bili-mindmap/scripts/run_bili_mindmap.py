#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the full Bilibili-to-XMind pipeline.")
    parser.add_argument("--source", required=True, help="Bilibili video URL or BV number")
    parser.add_argument("--output-dir", help="Pipeline output directory")
    parser.add_argument("--xmind-output", help="Explicit output .xmind path")
    parser.add_argument("--login-if-needed", action="store_true", help="Run `bili login` when needed")
    parser.add_argument("--transcribe-if-needed", action="store_true", help="Use ASR fallback when subtitles are unavailable")
    parser.add_argument("--asr-provider", choices=["auto", "parakeet", "aliyun"], default="auto")
    return parser.parse_args()


def run(command: list[str]) -> None:
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def read_video_title(context_dir: Path) -> str | None:
    details_path = context_dir / "video_details.json"
    if not details_path.exists():
        return None

    try:
        payload = json.loads(details_path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None

    title = str(payload.get("title") or "").strip()
    return title or None


def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*]+', "_", name).strip(" .")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned[:120] or "bilibili-mindmap"


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    context_dir = Path(args.output_dir).resolve() if args.output_dir else None

    prepare_cmd = [sys.executable, str(root / "scripts" / "prepare_bili_context.py"), "--source", args.source, "--asr-provider", args.asr_provider]
    if context_dir:
        prepare_cmd.extend(["--output", str(context_dir)])
    if args.login_if_needed:
        prepare_cmd.append("--login-if-needed")
    if args.transcribe_if_needed:
        prepare_cmd.append("--transcribe-if-needed")
    run(prepare_cmd)

    if context_dir is None:
        raise SystemExit("When using the full pipeline, please pass --output-dir so downstream steps have a stable path.")

    outline_path = context_dir / "outline.md"
    run([
        sys.executable,
        str(root / "scripts" / "generate_outline.py"),
        "--context-dir",
        str(context_dir),
        "--output",
        str(outline_path),
    ])

    if args.xmind_output:
        xmind_output = Path(args.xmind_output).resolve()
    else:
        video_title = read_video_title(context_dir)
        xmind_name = f"{sanitize_filename(video_title)}.xmind" if video_title else f"{context_dir.name}.xmind"
        xmind_output = context_dir / xmind_name

    run([
        sys.executable,
        str(root / "scripts" / "render_xmind.py"),
        "--outline",
        str(outline_path),
        "--output",
        str(xmind_output),
    ])

    print(f"outline={outline_path}")
    print(f"xmind={xmind_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
