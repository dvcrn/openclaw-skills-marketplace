#!/usr/bin/env python3
"""
Upload a local image to vidu and output the ssupload URI for use in img2video task body.

Usage:
  export VIDU_TOKEN=your_token
  python upload_image.py <image_path> [width] [height]

If width/height are omitted, they are inferred from the image (requires PIL/Pillow or similar).
Output: ssupload:?id=<id> (one line to stdout).
Exit: 0 on success, non-zero on failure.
"""

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


def get_image_size(path: str) -> tuple[int, int]:
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size  # (width, height)
    except Exception:
        return 0, 0


def main() -> int:
    if not TOKEN:
        print("VIDU_TOKEN is not set", file=sys.stderr)
        return 1
    if len(sys.argv) < 2:
        print("Usage: upload_image.py <image_path> [width] [height]", file=sys.stderr)
        return 1

    path = sys.argv[1]
    if not os.path.isfile(path):
        print(f"File not found: {path}", file=sys.stderr)
        return 1

    if len(sys.argv) >= 4:
        width, height = int(sys.argv[2]), int(sys.argv[3])
    else:
        width, height = get_image_size(path)
        if width <= 0 or height <= 0:
            print("Could not get image size; pass width height as arguments", file=sys.stderr)
            return 1

    # 1) CreateUpload
    create_url = f"{BASE_URL}/tools/v1/files/uploads"
    create_body = {
        "metadata": {"image-height": str(height), "image-width": str(width)},
        "scene": "vidu",
    }
    r = requests.post(create_url, json=create_body, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    put_url = data.get("put_url")
    upload_id = data.get("id")
    if not put_url or upload_id is None:
        print("CreateUpload response missing put_url or id", file=sys.stderr)
        return 1

    # 2) PUT file
    content_type = "image/webp"
    if path.lower().endswith(".png"):
        content_type = "image/png"
    elif path.lower().endswith((".jpg", ".jpeg")):
        content_type = "image/jpeg"
    put_headers = {
        "Content-Type": content_type,
        "x-amz-meta-image-height": str(height),
        "x-amz-meta-image-width": str(width),
    }
    with open(path, "rb") as f:
        put_r = requests.put(put_url, data=f, headers=put_headers, timeout=60)
    put_r.raise_for_status()
    etag = put_r.headers.get("ETag", "").strip('"')

    # 3) FinishUpload
    finish_url = f"{BASE_URL}/tools/v1/files/uploads/{upload_id}/finish"
    finish_body = {"etag": etag, "id": str(upload_id)}
    fin_r = requests.put(finish_url, json=finish_body, headers=HEADERS, timeout=30)
    fin_r.raise_for_status()

    print(f"ssupload:?id={upload_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
