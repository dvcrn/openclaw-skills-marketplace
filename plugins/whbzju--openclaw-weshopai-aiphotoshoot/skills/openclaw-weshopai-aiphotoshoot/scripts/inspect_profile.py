#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

from weshop_client import load_profile


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect the locally stored WeShop AI photoshoot profile and return "
            "a concise JSON summary for session bootstrap."
        )
    )
    parser.add_argument(
        "--profile",
        default="",
        help="Optional explicit profile path. Defaults to the runtime profile resolution order.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    profile, resolved_profile_path = load_profile(args.profile or None)

    girlfriend = profile.get("girlfriend", {})
    defaults = profile.get("defaults", {})
    outfits = defaults.get("outfits", [])
    scenes = defaults.get("scenes", [])
    scene_notes = defaults.get("sceneNotes", [])

    profile_exists = resolved_profile_path.exists()
    identity_ready = bool(girlfriend.get("fashionModelId") or girlfriend.get("cover"))
    setup_complete = identity_ready and str(girlfriend.get("status", "")).strip().lower() == "complete"

    output = {
        "profilePath": str(resolved_profile_path),
        "profileExists": profile_exists,
        "profileLoaded": bool(profile),
        "identityReady": identity_ready,
        "setupComplete": setup_complete,
        "girlfriend": {
            "name": str(girlfriend.get("name", "")).strip(),
            "fashionModelId": str(girlfriend.get("fashionModelId", "")).strip(),
            "status": str(girlfriend.get("status", "")).strip(),
            "appearanceNote": str(girlfriend.get("appearanceNote", "")).strip(),
        },
        "defaults": {
            "outfitCount": len(outfits) if isinstance(outfits, list) else 0,
            "sceneCount": len(scenes) if isinstance(scenes, list) else 0,
            "sceneNoteCount": len(scene_notes) if isinstance(scene_notes, list) else 0,
            "outfitLabels": [
                str(entry.get("label") or entry.get("id") or "").strip()
                for entry in outfits
                if isinstance(entry, dict)
            ],
            "sceneLabels": [
                str(entry.get("label") or entry.get("id") or "").strip()
                for entry in scenes
                if isinstance(entry, dict)
            ],
            "sceneNoteLabels": [
                str(entry.get("label") or entry.get("id") or "").strip()
                for entry in scene_notes
                if isinstance(entry, dict)
            ],
        },
    }

    json.dump(output, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
