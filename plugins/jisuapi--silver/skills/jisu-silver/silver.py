#!/usr/bin/env python3
"""
Silver price skill for OpenClaw.
基于极速数据白银价格 API：
https://www.jisuapi.com/api/silver/
"""

import sys
import json
import os
import requests


BASE_URL = "https://api.jisuapi.com/silver"


def _call_silver_api(path: str, appkey: str):
    params = {"appkey": appkey}
    url = f"{BASE_URL}/{path}"

    try:
        resp = requests.get(url, params=params, timeout=10)
    except Exception as e:
        return {"error": "request_failed", "message": str(e)}

    if resp.status_code != 200:
        return {
            "error": "http_error",
            "status_code": resp.status_code,
            "body": resp.text,
        }

    try:
        data = resp.json()
    except Exception:
        return {"error": "invalid_json", "body": resp.text}

    if data.get("status") != 0:
        return {
            "error": "api_error",
            "code": data.get("status"),
            "message": data.get("msg"),
        }

    return data.get("result", {})


def shgold(appkey: str):
    """上海黄金交易所白银价格 /silver/shgold"""
    return _call_silver_api("shgold", appkey)


def shfutures(appkey: str):
    """上海期货交易所白银价格 /silver/shfutures"""
    return _call_silver_api("shfutures", appkey)


def london_silver(appkey: str):
    """伦敦银价格 /silver/london"""
    return _call_silver_api("london", appkey)


def main():
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  silver.py shgold        # 上海黄金交易所白银价格\n"
            "  silver.py shfutures     # 上海期货交易所白银价格\n"
            "  silver.py london        # 伦敦银价格",
            file=sys.stderr,
        )
        sys.exit(1)

    appkey = os.getenv("JISU_API_KEY")

    if not appkey:
        print("Error: JISU_API_KEY must be set in environment.", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "shgold":
        result = shgold(appkey)
    elif cmd == "shfutures":
        result = shfutures(appkey)
    elif cmd == "london":
        result = london_silver(appkey)
    else:
        print(f"Error: unknown command '{cmd}'", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

