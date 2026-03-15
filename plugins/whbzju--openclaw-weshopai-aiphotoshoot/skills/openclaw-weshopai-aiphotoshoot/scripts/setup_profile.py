#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

from weshop_client import (
    DEFAULT_PROFILE_FILENAME,
    WeShopError,
    create_my_fashion_model,
    load_profile,
    resolve_image_input,
    save_profile,
    wait_for_my_fashion_model,
)


def parse_labeled_value(raw: str) -> tuple[str, str]:
    if "=" not in raw:
        return "", raw.strip()
    label, value = raw.split("=", 1)
    return label.strip(), value.strip()


def slugify(value: str, fallback: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or fallback


def derive_label(value: str, fallback: str) -> str:
    trimmed = value.strip()
    if not trimmed:
        return fallback
    if "://" in trimmed:
        return Path(trimmed.split("?", 1)[0]).name or fallback
    return Path(trimmed).stem or fallback


def upsert_image_entry(
    entries: list[dict[str, str]],
    *,
    raw_value: str,
    default_prefix: str,
    index: int,
) -> None:
    label, value = parse_labeled_value(raw_value)
    image_url = resolve_image_input(value)
    final_label = label or derive_label(value, f"{default_prefix}-{index}")
    entry_id = slugify(final_label, f"{default_prefix}-{index}")
    new_entry = {
        "id": entry_id,
        "label": final_label,
        "image": image_url,
        "savedAt": str(int(time.time())),
    }

    for idx, entry in enumerate(entries):
        if entry.get("id") == entry_id or entry.get("label") == final_label:
            entries[idx] = new_entry
            return
        if entry.get("image") == image_url:
            entries[idx] = new_entry
            return
    entries.append(new_entry)


def upsert_scene_note(entries: list[dict[str, str]], *, raw_value: str, index: int) -> None:
    label, description = parse_labeled_value(raw_value)
    trimmed_description = description.strip()
    if not trimmed_description:
        raise WeShopError("Scene note cannot be empty.")

    final_label = label or f"scene-note-{index}"
    entry_id = slugify(final_label, f"scene-note-{index}")
    new_entry = {
        "id": entry_id,
        "label": final_label,
        "description": trimmed_description,
        "savedAt": str(int(time.time())),
    }

    for idx, entry in enumerate(entries):
        if entry.get("id") == entry_id or entry.get("label") == final_label:
            entries[idx] = new_entry
            return
        if entry.get("description") == trimmed_description:
            entries[idx] = new_entry
            return
    entries.append(new_entry)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create or update a stored girlfriend profile for the OpenClaw "
            "WeShop AI photoshoot skill."
        )
    )
    parser.add_argument(
        "--profile",
        default="",
        help=(
            "Profile JSON path. Defaults to WESHOP_PROFILE_FILE, "
            f"the current directory {DEFAULT_PROFILE_FILENAME}, or a new file there."
        ),
    )
    parser.add_argument("--name", default="", help="Girlfriend / character name.")
    parser.add_argument(
        "--face-image",
        action="append",
        default=[],
        help="Clear front-face image URL or local file. Repeat 1-4 times to build the identity.",
    )
    parser.add_argument(
        "--existing-fashion-model-id",
        default="",
        help="Reuse an existing WeShop fashionModelId instead of creating a new one.",
    )
    parser.add_argument(
        "--default-outfit",
        action="append",
        default=[],
        help="Default outfit image. Accepts IMAGE or label=IMAGE.",
    )
    parser.add_argument(
        "--default-scene",
        action="append",
        default=[],
        help="Default scene image. Accepts IMAGE or label=IMAGE.",
    )
    parser.add_argument(
        "--scene-note",
        action="append",
        default=[],
        help="Default imagined scene text. Accepts NOTE or label=NOTE.",
    )
    parser.add_argument(
        "--appearance-note",
        default="",
        help="Optional short note about the girlfriend's appearance or vibe.",
    )
    parser.add_argument("--replace-outfits", action="store_true")
    parser.add_argument("--replace-scenes", action="store_true")
    parser.add_argument("--replace-scene-notes", action="store_true")
    parser.add_argument("--wait-retries", type=int, default=120)
    parser.add_argument("--wait-delay-seconds", type=int, default=5)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.face_image and args.existing_fashion_model_id:
        parser.error("Use either --face-image or --existing-fashion-model-id, not both.")
    if len(args.face_image) > 4:
        parser.error("WeShop supports at most 4 face images for myFashionModel/create.")

    try:
        profile, resolved_profile_path = load_profile(args.profile or None)
        defaults = profile.setdefault("defaults", {})
        defaults.setdefault("outfits", [])
        defaults.setdefault("scenes", [])
        defaults.setdefault("sceneNotes", [])
        girlfriend = profile.setdefault("girlfriend", {})
        meta = profile.setdefault("meta", {})

        if args.replace_outfits:
            defaults["outfits"] = []
        if args.replace_scenes:
            defaults["scenes"] = []
        if args.replace_scene_notes:
            defaults["sceneNotes"] = []

        name = args.name.strip() or str(girlfriend.get("name", "")).strip() or "Girlfriend"

        if args.face_image:
            face_urls = [resolve_image_input(value) for value in args.face_image]
            fashion_model_id = create_my_fashion_model(face_urls, name)
            model_info = wait_for_my_fashion_model(
                fashion_model_id=fashion_model_id,
                max_retries=args.wait_retries,
                delay_seconds=args.wait_delay_seconds,
            )
            girlfriend.update(
                {
                    "name": str(model_info.get("name", name)).strip() or name,
                    "fashionModelId": int(fashion_model_id),
                    "cover": str(model_info.get("cover", "")).strip(),
                    "images": model_info.get("images", face_urls),
                    "status": str(model_info.get("status", "complete")).strip() or "complete",
                }
            )
        elif args.existing_fashion_model_id:
            model_info = wait_for_my_fashion_model(
                fashion_model_id=args.existing_fashion_model_id,
                max_retries=args.wait_retries,
                delay_seconds=args.wait_delay_seconds,
            )
            girlfriend.update(
                {
                    "name": str(model_info.get("name", name)).strip() or name,
                    "fashionModelId": int(args.existing_fashion_model_id),
                    "cover": str(model_info.get("cover", "")).strip(),
                    "images": model_info.get("images", []),
                    "status": str(model_info.get("status", "complete")).strip() or "complete",
                }
            )
        elif not girlfriend.get("fashionModelId") and not girlfriend.get("cover"):
            raise WeShopError(
                "No stored girlfriend identity found. Provide --face-image or "
                "--existing-fashion-model-id first."
            )
        else:
            girlfriend["name"] = name

        if args.appearance_note.strip():
            girlfriend["appearanceNote"] = args.appearance_note.strip()

        for idx, raw_value in enumerate(args.default_outfit, start=1):
            upsert_image_entry(
                defaults["outfits"],
                raw_value=raw_value,
                default_prefix="outfit",
                index=idx,
            )

        for idx, raw_value in enumerate(args.default_scene, start=1):
            upsert_image_entry(
                defaults["scenes"],
                raw_value=raw_value,
                default_prefix="scene",
                index=idx,
            )

        for idx, raw_value in enumerate(args.scene_note, start=1):
            upsert_scene_note(defaults["sceneNotes"], raw_value=raw_value, index=idx)

        if not defaults["outfits"]:
            # Scene notes are valid without a default image, but actual generation still
            # needs at least one outfit image later.
            meta["missingDefaultOutfit"] = True
        else:
            meta["missingDefaultOutfit"] = False

        profile["profileName"] = profile.get("profileName") or slugify(name, "girlfriend-profile")
        meta["createdAt"] = int(meta.get("createdAt") or time.time())
        meta["updatedAt"] = int(time.time())

        saved_path = save_profile(profile, resolved_profile_path)
    except WeShopError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "ok": True,
                "profilePath": str(saved_path),
                "profileName": profile.get("profileName", ""),
                "girlfriend": profile.get("girlfriend", {}),
                "defaults": {
                    "outfits": profile.get("defaults", {}).get("outfits", []),
                    "scenes": profile.get("defaults", {}).get("scenes", []),
                    "sceneNotes": profile.get("defaults", {}).get("sceneNotes", []),
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
