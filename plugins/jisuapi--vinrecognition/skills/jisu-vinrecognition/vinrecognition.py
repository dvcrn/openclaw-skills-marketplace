#!/usr/bin/env python3
"""
VIN recognition skill for OpenClaw.
基于极速数据 VIN 识别 API：
https://www.jisuapi.com/api/vinrecognition/
"""

import base64
import json
import os
import sys
from typing import Any, Dict

import requests


VIN_RECOG_URL = "https://api.jisuapi.com/vinrecognition/recognize"


def _call_vin_api(appkey: str, pic_base64: str) -> Dict[str, Any]:
    params = {"appkey": appkey}
    data = {"pic": pic_base64}

    try:
        resp = requests.post(VIN_RECOG_URL, params=params, data=data, timeout=15)
    except Exception as e:
        return {"error": "request_failed", "message": str(e)}

    if resp.status_code != 200:
        return {
            "error": "http_error",
            "status_code": resp.status_code,
            "body": resp.text,
        }

    try:
        data_json = resp.json()
    except Exception:
        return {"error": "invalid_json", "body": resp.text}

    if data_json.get("status") != 0:
        return {
            "error": "api_error",
            "code": data_json.get("status"),
            "message": data_json.get("msg"),
        }

    return data_json.get("result", {})


def _get_pic_base64(req: Dict[str, Any]) -> Dict[str, Any]:
    """
    从请求中获取 base64 图片内容：
    - 若提供 pic 字段（base64 字符串），直接使用；
    - 若提供 path/image/file，则从本地文件读取并转为 base64。
    """
    pic = req.get("pic")
    if pic:
        return {"pic": str(pic), "error": None}

    path = req.get("path") or req.get("image") or req.get("file")
    if not path:
        return {"pic": None, "error": "Either 'pic' (base64) or 'path/image/file' is required"}

    if not os.path.isfile(path):
        return {"pic": None, "error": f"File not found: {path}"}

    try:
        with open(path, "rb") as f:
            raw = f.read()
    except Exception as e:
        return {"pic": None, "error": f"Failed to read file: {e}"}

    try:
        encoded = base64.b64encode(raw).decode("utf-8")
    except Exception as e:
        return {"pic": None, "error": f"Failed to base64-encode file: {e}"}

    return {"pic": encoded, "error": None}


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  vinrecognition.py '{\"path\":\"vin.jpg\"}'   # 从本地图片读取并识别 VIN\n"
            "  vinrecognition.py '{\"pic\":\"<base64>\"}'   # 直接传 base64 图片内容",
            file=sys.stderr,
        )
        sys.exit(1)

    appkey = os.getenv("JISU_API_KEY")
    if not appkey:
        print("Error: JISU_API_KEY must be set in environment.", file=sys.stderr)
        sys.exit(1)

    raw = sys.argv[1]
    try:
        req: Dict[str, Any] = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(req, dict):
        print("Error: JSON body must be an object.", file=sys.stderr)
        sys.exit(1)

    pic_info = _get_pic_base64(req)
    if pic_info["error"]:
        print(
            json.dumps(
                {"error": "invalid_param", "message": pic_info["error"]},
                ensure_ascii=False,
                indent=2,
            )
        )
        sys.exit(1)

    result = _call_vin_api(appkey, pic_info["pic"])
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

