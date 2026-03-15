#!/usr/bin/env python3
"""
Submit a vidu task (text2video, img2video, headtailimg2video, character2video). Outputs task_id to stdout.

Usage:
  export VIDU_TOKEN=your_token
  python submit_task.py --type text2video --prompt "hello apple"
  python submit_task.py --type img2video --prompt "..." --image-uri "ssupload:?id=123"   # exactly 1 image
  python submit_task.py --type headtailimg2video --prompt "..." --image-uri id1 --image-uri id2   # exactly 2 (首帧,尾帧)
  python submit_task.py --type character2video --prompt "..." --image-uri id1 --image-uri id2 [...]  # image(s), Q2 only
  python submit_task.py --type character2video --prompt "..." --material "name:id:version" [...]  # subject(s), Q2 only
  python submit_task.py --type character2video --prompt "..." --image-uri id1 --material "name:id:version" [...]  # image + subject + text, Q2 only
  python submit_task.py --body-file task_body.json

Options:
  --type text2video | img2video | headtailimg2video | character2video
  --prompt "text"           (required; for character2video text is always required)
  --image-uri "ssupload:?id=X"  (img2video: 1; headtailimg2video: 2; character2video: image+subject combined at most 7)
  --material "name:id:version"  (character2video only; image+subject combined at most 7)
  --duration 8  --resolution 1080p  --aspect-ratio "16:9"  (aspect_ratio omitted for img2video)
  --model-version 3.2 | 3.1  --transition pro | speed  (transition omitted for character2video and for text2video Q2)
  --body-file path         (use full JSON body from file instead of flags)

Output: task_id (one line). Exit: 0 on success.
"""

import argparse
import json
import os
import sys

try:
    import requests
except ImportError:
    print("install requests: pip install requests", file=sys.stderr)
    sys.exit(1)

BASE_URL = os.environ.get("VIDU_BASE_URL", "https://service.vidu.cn").rstrip("/")
TOKEN = os.environ.get("VIDU_TOKEN", "")
HEADERS = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": f"viduclawbot/1.0 (+{BASE_URL})",
}


def _parse_material(s: str) -> tuple[str, str, str]:
    """Parse 'name:id:version' or 'id:version' into (name, id, version)."""
    parts = s.rsplit(":", 2)
    if len(parts) == 2:
        return (parts[0], parts[0], parts[1])  # id:version -> name=id
    if len(parts) == 3:
        return (parts[0], parts[1], parts[2])
    raise ValueError(f"Invalid --material format (use name:id:version or id:version): {s!r}")


def build_body(args: argparse.Namespace) -> dict:
    if args.body_file:
        with open(args.body_file, "r", encoding="utf-8") as f:
            return json.load(f)

    prompts = []
    for p in args.prompt or []:
        prompts.append({"type": "text", "content": p})
    for uri in args.image_uri or []:
        prompts.append({"type": "image", "content": uri})

    materials = getattr(args, "material", None) or []
    if args.type == "character2video" and materials:
        # character2video with material elements: 1-7 subjects
        if len(materials) > 7:
            raise ValueError("character2video allows at most 7 --material")
        for m in materials:
            name, mid, version = _parse_material(m)
            prompts.append({
                "type": "material",
                "name": name,
                "material": {"id": mid, "version": version},
            })

    n_images = len(args.image_uri or [])
    # character2video: text required; image and/or material at least one; image+material combined at most 7
    if args.type == "character2video":
        if not (args.prompt or []):
            raise ValueError("character2video requires --prompt (text is required)")
        if n_images + len(materials) > 7:
            raise ValueError("character2video: image + subject combined at most 7 (got %d image + %d material)" % (n_images, len(materials)))
        if n_images == 0 and len(materials) == 0:
            raise ValueError("character2video requires at least one of --image-uri or --material (image and/or subject)")

    if not prompts:
        raise ValueError("At least one --prompt, --image-uri, or (for character2video) --material required")

    # Validate image count per type (see 任务支持列表)
    if args.type == "img2video" and n_images != 1:
        raise ValueError("img2video requires exactly 1 --image-uri")
    if args.type == "headtailimg2video" and n_images != 2:
        raise ValueError("headtailimg2video requires exactly 2 --image-uri (首帧, 尾帧)")

    settings = {
        "duration": args.duration,
        "resolution": args.resolution,
        "movement_amplitude": "auto",
        "sample_count": 1,
        "schedule_mode": "normal",
        "codec": args.codec,
        "model_version": "3.1" if args.type == "character2video" else args.model_version,
        "use_trial": False,
    }
    # img2video: do not pass aspect_ratio (determined by input image)
    if args.type != "img2video":
        settings["aspect_ratio"] = args.aspect_ratio
    # character2video and text2video Q2: do not pass transition
    if args.type != "character2video" and not (args.type == "text2video" and args.model_version == "3.1"):
        settings["transition"] = args.transition

    return {
        "input": {
            "prompts": prompts,
            "editor_mode": "normal",
            "enhance": True,
        },
        "type": args.type,
        "settings": settings,
    }


def main() -> int:
    if not TOKEN:
        print("VIDU_TOKEN is not set", file=sys.stderr)
        return 1

    ap = argparse.ArgumentParser(description="Submit vidu task")
    ap.add_argument("--type", choices=("text2video", "img2video", "headtailimg2video", "character2video"), default="text2video")
    ap.add_argument("--prompt", action="append", help="Text prompt (repeat for multiple)")
    ap.add_argument("--image-uri", action="append", help="ssupload:?id=... for img2video")
    ap.add_argument("--material", action="append", help="character2video only: name:id:version (1-7, from create_element/list_elements)")
    ap.add_argument("--duration", type=int, default=8)
    ap.add_argument("--resolution", default="1080p")
    ap.add_argument("--aspect-ratio", default="16:9")
    ap.add_argument("--model-version", default="3.2")
    ap.add_argument("--transition", default="pro")
    ap.add_argument("--codec", default="h265")
    ap.add_argument("--body-file", help="Path to full JSON body file")
    args = ap.parse_args()

    try:
        body = build_body(args)
    except Exception as e:
        print(e, file=sys.stderr)
        return 1

    url = f"{BASE_URL}/vidu/v1/tasks"
    r = requests.post(url, json=body, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    task_id = data.get("id")
    if task_id is None:
        print("Response missing id", file=sys.stderr)
        return 1
    print(task_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
