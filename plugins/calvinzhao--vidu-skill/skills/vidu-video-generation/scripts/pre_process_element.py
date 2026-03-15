#!/usr/bin/env python3
"""
Call material/elements/pre-process: get recaption (style, description) for 1-3 uploaded images.
Workflow: this script must run before create_element — first pre-process, then create-element.
Use when you need recaption only, or as step 1 before running create_element.py; output recaption can be passed to create_element or used manually.

Usage:
  export VIDU_TOKEN=your_token
  python pre_process_element.py --name "机器猫" --image-uri "ssupload:?id=123"
  python pre_process_element.py --name "艾莉娅" --image-uri "ssupload:?id=1" --image-uri "ssupload:?id=2"

Input: 1-3 --image-uri (ssupload:?id=...); first is main, rest auxiliary. Images must be uploaded first (upload_image.py).
Output: One JSON line with full pre-process response (id, name, type, recaption, etc.). recaption has description, style.
Exit: 0 on success, non-zero on failure.
"""

import argparse
import json
import os
import sys

import requests


def main() -> int:
    ap = argparse.ArgumentParser(description="Pre-process material element (主体预处理)")
    ap.add_argument("--name", required=True, help="Subject name")
    ap.add_argument("--image-uri", action="append", dest="image_uris", required=True, help="ssupload:?id=... (1-3); first=main, rest=auxiliary")
    args = ap.parse_args()

    uris = args.image_uris or []
    if len(uris) < 1 or len(uris) > 3:
        print(json.dumps({"error": "pre_process_element requires 1-3 --image-uri"}), file=sys.stderr)
        return 1

    components = []
    for i, uri in enumerate(uris):
        comp_type = "main" if i == 0 else "auxiliary"
        components.append({
            "type": comp_type,
            "content": uri,
            "src_img": uri,
            "content_type": "image",
        })

    base = os.environ.get("VIDU_BASE_URL", "https://service.vidu.cn").rstrip("/")
    token = os.environ.get("VIDU_TOKEN", "")
    if not token:
        print(json.dumps({"error": "VIDU_TOKEN is not set"}), file=sys.stderr)
        return 1
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json",
        "User-Agent": f"viduclawbot/1.0 (+{base})",
    }

    body = {
        "components": components,
        "name": args.name,
        "type": "user",
    }
    url = f"{base}/vidu/v1/material/elements/pre-process"
    try:
        r = requests.post(url, json=body, headers=headers, timeout=60)
        r.raise_for_status()
        data = r.json()
        print(json.dumps(data))
        return 0
    except requests.RequestException as e:
        err = {"error": "pre-process failed"}
        if hasattr(e, "response") and e.response is not None:
            try:
                err["body"] = e.response.json()
            except Exception:
                err["text"] = (e.response.text or "")[:500]
        else:
            err["detail"] = str(e)
        print(json.dumps(err), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
