#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from weshop_client import DEFAULT_TRY_ON_PROMPT, WeShopError, submit_virtual_try_on


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a girlfriend photoshoot image using the OpenClaw WeShop "
            "AI photoshoot profile + virtualtryon flow."
        )
    )
    parser.add_argument(
        "--profile",
        default="",
        help="Profile JSON created by setup_profile.py. Used for stored identity and defaults.",
    )
    identity = parser.add_mutually_exclusive_group(required=False)
    identity.add_argument("--fashion-model-image", help="Identity image URL or local file.")
    identity.add_argument("--fashion-model-id", help="Stored WeShop fashionModelId to resolve.")
    parser.add_argument(
        "--original-image",
        help=(
            "Clothing/product image URL or local file. If omitted, the script tries the "
            "stored outfit defaults in the profile first."
        ),
    )
    parser.add_argument(
        "--default-original-image",
        default="",
        help="Explicit fallback clothing/product image. Used when --original-image is omitted.",
    )
    parser.add_argument(
        "--outfit-key",
        default="",
        help="Pick a stored default outfit by id or label from the profile.",
    )
    parser.add_argument(
        "--location-image",
        default="",
        help="Optional scene image URL or local file.",
    )
    parser.add_argument(
        "--scene-key",
        default="",
        help="Pick a stored scene image or scene note by id or label from the profile.",
    )
    parser.add_argument(
        "--shot-brief",
        default="",
        help="Short user request or scene brief. This is merged into the try-on prompt.",
    )
    parser.add_argument(
        "--shot-style",
        choices=["selfie", "mirror-selfie", "candid", "portrait"],
        default="selfie",
        help="Shot framing preset that adds quality and composition guardrails.",
    )
    parser.add_argument(
        "--auto-refine",
        action="store_true",
        help="Run a second change-pose pass to clean up anatomy/perspective issues after generation.",
    )
    parser.add_argument(
        "--prompt",
        default="",
        help=(
            "Explicit prompt override. If omitted, the script uses the recommended "
            f"try-on prompt: {DEFAULT_TRY_ON_PROMPT}"
        ),
    )
    parser.add_argument("--task-name", default="OpenClaw AI Photoshoot")
    parser.add_argument("--description-type", choices=["custom", "auto"], default="custom")
    parser.add_argument("--batch-count", type=int, default=1, help="Number of initial candidates to generate.")
    parser.add_argument("--poll-retries", type=int, default=120)
    parser.add_argument("--poll-delay-seconds", type=int, default=5)
    parser.add_argument(
        "--download-dir",
        default="generated",
        help=(
            "Relative directory under the current working directory where generated "
            "images are downloaded for local attachment replies."
        ),
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.profile and not args.fashion_model_image and not args.fashion_model_id:
        parser.error(
            "Provide --profile, --fashion-model-image, or --fashion-model-id so the "
            "script can resolve the girlfriend identity."
        )

    try:
        result = submit_virtual_try_on(
            profile_path=args.profile or None,
            fashion_model_image=args.fashion_model_image,
            fashion_model_id=args.fashion_model_id,
            original_image=args.original_image,
            default_original_image=args.default_original_image,
            outfit_key=args.outfit_key or None,
            location_image=args.location_image,
            scene_key=args.scene_key or None,
            prompt=args.prompt or None,
            shot_brief=args.shot_brief or None,
            shot_style=args.shot_style or None,
            auto_refine=args.auto_refine,
            task_name=args.task_name,
            description_type=args.description_type,
            batch_count=args.batch_count,
            poll_retries=args.poll_retries,
            poll_delay_seconds=args.poll_delay_seconds,
            download_dir=args.download_dir,
        )
    except WeShopError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    print(json.dumps({"ok": True, **result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
