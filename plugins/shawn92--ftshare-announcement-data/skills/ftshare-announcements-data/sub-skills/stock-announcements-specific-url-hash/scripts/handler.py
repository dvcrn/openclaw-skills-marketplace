#!/usr/bin/env python3
"""通过 url_hash 下载 A 股公告文件"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = "https://market.ft.tech"


def main():
    parser = argparse.ArgumentParser(description="通过 url_hash 下载 A 股公告文件")
    parser.add_argument("--url-hash", required=True, help="公告文件的 url_hash，从公告列表接口获取")
    parser.add_argument("--output", default=None, help="保存的文件名（默认 {url_hash}.pdf）")
    args = parser.parse_args()

    output = args.output or f"{args.url_hash}.pdf"
    url = f"{BASE_URL}/data/api/v1/market/data/announcements/stock-announcements/{args.url_hash}"

    try:
        with urllib.request.urlopen(url) as resp:
            content_type = resp.headers.get("Content-Type", "")
            data = resp.read()

        if b"{" in data[:10]:
            try:
                err = json.loads(data.decode())
                print(json.dumps(err, ensure_ascii=False, indent=2), file=sys.stderr)
                sys.exit(1)
            except Exception:
                pass

        with open(output, "wb") as f:
            f.write(data)
        print(json.dumps({"saved_to": os.path.abspath(output), "size_bytes": len(data)}, ensure_ascii=False))
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            err = json.loads(body)
        except Exception:
            err = {"error": body}
        print(json.dumps(err, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
