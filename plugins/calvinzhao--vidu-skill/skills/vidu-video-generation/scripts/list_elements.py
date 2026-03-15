#!/usr/bin/env python3
"""
Query personal material elements (查询主体). GET /vidu/v1/material/elements/personal.

Usage:
  export VIDU_TOKEN=your_token
  python list_elements.py
  python list_elements.py --keyword "机器猫" --page 0 --pagesz 30
  python list_elements.py --modalities image --modalities text

Options:
  --page N           Page number (0-based), default 0
  --pagesz N         Page size, default 30
  --page-token TOKEN Next page token (from previous response)
  --keyword "text"   Search term (URL-encoded by script if needed)
  --modalities M     Filter by modality; can repeat (e.g. image, text)

Output: One JSON object per line per element with id, name, version; then a line with next_page_token if any.
Exit: 0 on success, 1 on failure.
"""

import argparse
import json
import os
import sys
from urllib.parse import quote

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


def main() -> int:
    if not TOKEN:
        print("VIDU_TOKEN is not set", file=sys.stderr)
        return 1

    ap = argparse.ArgumentParser(description="Query personal material elements (查询主体)")
    ap.add_argument("--page", type=int, default=0, help="Page number (0-based)")
    ap.add_argument("--pagesz", type=int, default=30, help="Page size")
    ap.add_argument("--page-token", default="", help="Next page token for pagination")
    ap.add_argument("--keyword", default="", help="Search keyword")
    ap.add_argument("--modalities", action="append", dest="modalities", help="Filter by modality (repeat for multiple)")
    args = ap.parse_args()

    # Build query string (repeated modalities: modalities=image&modalities=text)
    query_parts = [f"pager.page={args.page}", f"pager.pagesz={args.pagesz}"]
    if args.page_token:
        query_parts.append(f"pager.page_token={quote(args.page_token, safe='')}")
    if args.keyword:
        query_parts.append(f"keyword={quote(args.keyword, safe='')}")
    for m in args.modalities or []:
        query_parts.append(f"modalities={quote(m, safe='')}")

    url = f"{BASE_URL}/vidu/v1/material/elements/personal?{'&'.join(query_parts)}"

    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        err = {"error": "list elements failed", "detail": str(e)}
        if hasattr(e, "response") and e.response is not None:
            try:
                err["body"] = e.response.json()
            except Exception:
                err["text"] = (e.response.text or "")[:500]
        print(json.dumps(err), file=sys.stderr)
        return 1

    elements = data.get("elements") or []
    for el in elements:
        # Output one line per element: at least id, name, version for character2video
        out = {
            "id": el.get("id"),
            "name": el.get("name"),
            "version": el.get("version"),
        }
        # Optionally include recaption.description if present
        recaption = el.get("recaption") or {}
        if recaption.get("description"):
            out["description"] = recaption["description"]
        if recaption.get("style"):
            out["style"] = recaption["style"]
        print(json.dumps(out, ensure_ascii=False))

    next_token = data.get("next_page_token") or ""
    if next_token:
        print(json.dumps({"next_page_token": next_token}, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
