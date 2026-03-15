#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from weshop_client import (
    DEFAULT_CHANGE_POSE_GENERATE_VERSION,
    DEFAULT_CHANGE_POSE_PROMPT,
    WeShopError,
    submit_change_pose,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Edit an existing image with the WeShop change-pose agent while "
            "preserving the same character identity."
        )
    )
    parser.add_argument(
        "--profile",
        default="",
        help=(
            "Optional profile JSON created by setup_profile.py. Used to resolve a stored "
            "identity reference if available."
        ),
    )
    identity = parser.add_mutually_exclusive_group(required=False)
    identity.add_argument("--fashion-model-image", help="Identity image URL or local file.")
    identity.add_argument("--fashion-model-id", help="Stored WeShop fashionModelId to resolve.")
    parser.add_argument(
        "--editing-image",
        required=True,
        help="The image to edit. Accepts a URL or local file.",
    )
    parser.add_argument(
        "--edit-brief",
        default="",
        help="Short edit instruction such as pose, expression, hand, or framing changes.",
    )
    parser.add_argument(
        "--prompt",
        default="",
        help=(
            "Explicit prompt override. If omitted, the script uses the default "
            f"change-pose prompt: {DEFAULT_CHANGE_POSE_PROMPT}"
        ),
    )
    parser.add_argument("--task-name", default="OpenClaw Pose Edit")
    parser.add_argument(
        "--generate-version",
        choices=["lite", "pro"],
        default=DEFAULT_CHANGE_POSE_GENERATE_VERSION,
        help="Generation tier for change-pose. The skill default is lite.",
    )
    parser.add_argument("--description-type", choices=["custom", "auto"], default="custom")
    parser.add_argument("--batch-count", type=int, default=1)
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

    if args.batch_count < 1:
        parser.error("--batch-count must be at least 1.")

    try:
        result = submit_change_pose(
            profile_path=args.profile or None,
            fashion_model_image=args.fashion_model_image,
            fashion_model_id=args.fashion_model_id,
            editing_image=args.editing_image,
            prompt=args.prompt or None,
            edit_brief=args.edit_brief or None,
            task_name=args.task_name,
            generate_version=args.generate_version,
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
