#!/usr/bin/env python3
"""
Get public download URL(s) for uploaded resource(s) by ssupload id(s).

The returned URL(s) are valid for 1 hour only. After expiry, run this script
again to obtain a new URL.

Usage:
  export VIDU_TOKEN=your_token
  python get_upload_url.py <ssupload_uri_or_id> [ssupload_uri_or_id ...]

Each argument may be either a full ssupload URI (e.g. ssupload:?id=123) or
a numeric upload id (e.g. 123). Output: one public URL per line, in input order.
Exit: 0 on success, non-zero on failure.
"""

import os
import re
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

SSUPLOAD_PATTERN = re.compile(r"^ssupload:\?id=(\d+)$")


def normalize_uri(arg: str) -> str | None:
    """Return ssupload:?id=<id> for valid input, else None."""
    arg = arg.strip()
    if not arg:
        return None
    m = SSUPLOAD_PATTERN.match(arg)
    if m:
        return f"ssupload:?id={m.group(1)}"
    if arg.isdigit():
        return f"ssupload:?id={arg}"
    return None


def main() -> int:
    if not TOKEN:
        print("VIDU_TOKEN is not set", file=sys.stderr)
        return 1
    if len(sys.argv) < 2:
        print(
            "Usage: get_upload_url.py <ssupload_uri_or_id> [ssupload_uri_or_id ...]",
            file=sys.stderr,
        )
        return 1

    uris: list[str] = []
    for i, arg in enumerate(sys.argv[1:], start=1):
        u = normalize_uri(arg)
        if u is None:
            print(f"Invalid argument {i}: {arg!r}", file=sys.stderr)
            return 1
        uris.append(u)

    url = f"{BASE_URL}/tools/v1/files/uploads/presigned-urls"
    r = requests.post(url, json={"uris": uris}, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()

    # Support common response shapes: presigned_urls or urls (map: uri -> url)
    presigned = data.get("presigned_urls") or data.get("urls")
    if not isinstance(presigned, dict):
        print("Unexpected response: missing presigned_urls map", file=sys.stderr)
        return 1

    missing = []
    for uri in uris:
        if uri not in presigned or not presigned[uri]:
            missing.append(uri)
        else:
            print(presigned[uri])

    if missing:
        print(f"No URL returned for: {missing}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
