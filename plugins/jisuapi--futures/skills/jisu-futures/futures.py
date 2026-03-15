#!/usr/bin/env python3
"""
Futures price skill for OpenClaw.
基于极速数据期货查询 API：
https://www.jisuapi.com/api/futures/
"""

import sys
import json
import os
import requests


BASE_URL = "https://api.jisuapi.com/futures"


def _call_futures(path: str, appkey: str):
    """
    通用调用 /futures/{path}，例如 shfutures/dlfutures/zzfutures/zgjrfutures/gzfutures。
    无需额外参数。
    """
    url = f"{BASE_URL}/{path}"
    params = {"appkey": appkey}

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


def shfutures(appkey: str):
    """上海期货交易所 /futures/shfutures"""
    return _call_futures("shfutures", appkey)


def dlfutures(appkey: str):
    """大连商品交易所 /futures/dlfutures"""
    return _call_futures("dlfutures", appkey)


def zzfutures(appkey: str):
    """郑州商品交易所 /futures/zzfutures"""
    return _call_futures("zzfutures", appkey)


def zgjrfutures(appkey: str):
    """中国金融期货交易所 /futures/zgjrfutures"""
    return _call_futures("zgjrfutures", appkey)


def gzfutures(appkey: str):
    """广州期货交易所 /futures/gzfutures"""
    return _call_futures("gzfutures", appkey)


def main():
    if len(sys.argv) < 2:
        print(
            "Usage:\\n"
            "  futures.py shfutures    # 上海期货交易所\\n"
            "  futures.py dlfutures    # 大连商品交易所\\n"
            "  futures.py zzfutures    # 郑州商品交易所\\n"
            "  futures.py zgjrfutures  # 中国金融期货交易所\\n"
            "  futures.py gzfutures    # 广州期货交易所",
            file=sys.stderr,
        )
        sys.exit(1)

    appkey = os.getenv("JISU_API_KEY")
    if not appkey:
        print("Error: JISU_API_KEY must be set in environment.", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "shfutures":
        result = shfutures(appkey)
    elif cmd == "dlfutures":
        result = dlfutures(appkey)
    elif cmd == "zzfutures":
        result = zzfutures(appkey)
    elif cmd == "zgjrfutures":
        result = zgjrfutures(appkey)
    elif cmd == "gzfutures":
        result = gzfutures(appkey)
    else:
        print(f"Error: unknown command '{cmd}'", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

