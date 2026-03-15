#!/usr/bin/env python3
"""
Multi-Platform Social Media Publisher
======================================
CLI entry point.  Publishes content to X/Twitter, LinkedIn,
WeChat Official Account, and Xiaohongshu with a single command.

Usage examples
--------------
    python3 main.py publish --content "Hello world" --platforms all
    python3 main.py publish --file article.md --platforms twitter,linkedin
    python3 main.py publish --content "Long post…" --platforms twitter --thread
    python3 main.py validate
    python3 main.py list-platforms
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Local imports (adapters + utils)
# ---------------------------------------------------------------------------
from adapters.twitter_adapter import TwitterAdapter
from adapters.linkedin_adapter import LinkedInAdapter
from adapters.wechat_adapter import WeChatAdapter
from adapters.xiaohongshu_adapter import XiaohongshuAdapter
from utils.config_loader import ConfigLoader
from utils.content_adapter import ContentAdapter
from utils.image_handler import ImageHandler
from utils.logger import Logger

log = Logger(__name__)

# ---------------------------------------------------------------------------
# Platform registry
# ---------------------------------------------------------------------------
PLATFORM_REGISTRY: dict[str, type] = {
    "twitter": TwitterAdapter,
    "linkedin": LinkedInAdapter,
    "wechat": WeChatAdapter,
    "xiaohongshu": XiaohongshuAdapter,
}

PLATFORM_ALIASES: dict[str, str] = {
    "x": "twitter",
    "xhs": "xiaohongshu",
    "wechat-oa": "wechat",
}


def resolve_platforms(platforms_arg: str) -> list[str]:
    """Expand 'all' and resolve aliases."""
    if platforms_arg.lower() == "all":
        return list(PLATFORM_REGISTRY.keys())
    result = []
    for p in platforms_arg.split(","):
        p = p.strip().lower()
        p = PLATFORM_ALIASES.get(p, p)
        if p in PLATFORM_REGISTRY:
            result.append(p)
        else:
            log.warning(f"Unknown platform '{p}', skipping.")
    return result


def build_adapter(platform: str, config: dict):
    """Instantiate an adapter, returning None if credentials are missing."""
    cls = PLATFORM_REGISTRY[platform]
    try:
        return cls(config.get(platform, {}))
    except ValueError as exc:
        log.warning(f"[{platform}] Skipping – {exc}")
        return None


# ---------------------------------------------------------------------------
# Sub-commands
# ---------------------------------------------------------------------------
def cmd_publish(args: argparse.Namespace) -> int:
    config = ConfigLoader.load()
    content_adapter = ContentAdapter()
    image_handler = ImageHandler()

    # Load raw content
    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"❌ File not found: {args.file}", file=sys.stderr)
            return 1
        raw_content = path.read_text(encoding="utf-8")
    else:
        raw_content = args.content or ""

    if not raw_content.strip():
        print("❌ No content provided. Use --content or --file.", file=sys.stderr)
        return 1

    # Process images
    processed_images: list[str] = []
    if args.images:
        for img_path in args.images:
            processed = image_handler.process_image(img_path)
            if processed:
                processed_images.append(processed)
            else:
                log.warning(f"Image skipped: {img_path}")

    platforms = resolve_platforms(args.platforms)
    if not platforms:
        print("❌ No valid platforms specified.", file=sys.stderr)
        return 1

    dry_run = args.dry_run or config.get("settings", {}).get("dry_run", False)
    results: dict[str, dict] = {}
    exit_code = 0

    for platform in platforms:
        print(f"\n📤 [{platform.upper()}] Publishing…")

        adapter = build_adapter(platform, config)
        if adapter is None:
            results[platform] = {"success": False, "error": "Missing credentials"}
            exit_code = 1
            continue

        # Adapt content for this platform
        adapted = content_adapter.adapt(
            raw_content,
            platform,
            as_thread=(args.thread and platform == "twitter"),
        )

        if dry_run:
            print(f"   [DRY RUN] Would publish to {platform}:")
            if isinstance(adapted, list):
                for i, t in enumerate(adapted, 1):
                    print(f"   [{i}] {t}")
            elif isinstance(adapted, dict):
                print(f"   {json.dumps(adapted, ensure_ascii=False, indent=4)}")
            else:
                print(f"   {adapted}")
            results[platform] = {"success": True, "dry_run": True}
            continue

        try:
            result = adapter.publish(adapted, processed_images or None)
            results[platform] = result
            if result.get("success"):
                url = result.get("url") or result.get("media_id") or "✓"
                print(f"   ✅ Success  →  {url}")
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                exit_code = 1
        except Exception as exc:
            results[platform] = {"success": False, "error": str(exc)}
            print(f"   ❌ Exception: {exc}")
            exit_code = 1

    # Summary
    print("\n" + "─" * 50)
    success = sum(1 for r in results.values() if r.get("success"))
    total = len(results)
    print(f"📊 Results: {success}/{total} platforms succeeded")

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))

    return exit_code


def cmd_validate(args: argparse.Namespace) -> int:
    config = ConfigLoader.load()
    platforms = resolve_platforms(args.platforms if hasattr(args, "platforms") else "all")
    exit_code = 0

    print("🔑 Validating credentials…\n")
    for platform in platforms:
        adapter = build_adapter(platform, config)
        if adapter is None:
            print(f"  {platform:<15} ⚠️  No credentials configured")
            continue
        try:
            ok = adapter.validate()
            status = "✅ Valid" if ok else "❌ Invalid"
            print(f"  {platform:<15} {status}")
            if not ok:
                exit_code = 1
        except Exception as exc:
            print(f"  {platform:<15} ❌ Error: {exc}")
            exit_code = 1

    return exit_code


def cmd_list_platforms(_args: argparse.Namespace) -> int:
    config = ConfigLoader.load()
    print("\n📋 Supported Platforms\n")
    print(f"  {'Name':<15} {'Auth':<15} {'Configured':<12} {'Features'}")
    print("  " + "─" * 70)
    for key, cls in PLATFORM_REGISTRY.items():
        platform_cfg = config.get(key, {})
        configured = "✅ Yes" if platform_cfg else "❌ No"
        features = ", ".join(cls.FEATURES)
        print(f"  {cls.DISPLAY_NAME:<15} {cls.AUTH_METHOD:<15} {configured:<12} {features}")
    print()
    return 0


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Multi-Platform Social Media Publisher",
    )
    sub = parser.add_subparsers(dest="command")

    # publish
    p_pub = sub.add_parser("publish", help="Publish content to social platforms")
    p_pub.add_argument("--content", "-c", help="Content string to publish")
    p_pub.add_argument("--file", "-f", help="Path to a Markdown/text file to publish")
    p_pub.add_argument(
        "--platforms",
        "-p",
        default="all",
        help="Comma-separated platforms or 'all' (default: all)",
    )
    p_pub.add_argument(
        "--images",
        nargs="+",
        metavar="IMAGE",
        help="Image paths to attach",
    )
    p_pub.add_argument(
        "--thread",
        action="store_true",
        help="Publish Twitter content as a thread",
    )
    p_pub.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview adapted content without actually publishing",
    )
    p_pub.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    # validate
    p_val = sub.add_parser("validate", help="Validate credentials for all platforms")
    p_val.add_argument("--platforms", "-p", default="all")

    # list-platforms
    sub.add_parser("list-platforms", help="List supported platforms and their status")

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "publish":
        return cmd_publish(args)
    if args.command == "validate":
        return cmd_validate(args)
    if args.command == "list-platforms":
        return cmd_list_platforms(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
