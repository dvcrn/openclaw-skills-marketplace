#!/usr/bin/env python3
"""
Plume API Client
Wraps Open API HTTP calls: create task, query task, upload image
"""

import json
import os
import ssl
import sys
import urllib.request
import urllib.error
import urllib.parse
from typing import Optional

# Skip SSL verification (consistent with feishu-img-msg)
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE


def _load_openclaw_json(path: str) -> dict:
    """Read openclaw.json, tolerating trailing commas (JSON5 compatible)"""
    import re
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    # Remove trailing commas (, followed by } or ])
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return json.loads(text)


API_BASE = "https://design.useplume.app"


def get_config():
    """Read PLUME_API_KEY from ~/.openclaw/openclaw.json, fallback to environment variable"""
    api_key = None

    openclaw_cfg = os.path.expanduser("~/.openclaw/openclaw.json")
    if os.path.isfile(openclaw_cfg):
        try:
            cfg = _load_openclaw_json(openclaw_cfg)
            api_key = cfg.get("env", {}).get("vars", {}).get("PLUME_API_KEY")
        except (json.JSONDecodeError, OSError):
            pass

    if not api_key:
        api_key = os.environ.get("PLUME_API_KEY")

    if not api_key:
        raise ValueError("PLUME_API_KEY not configured (please set in openclaw.json env.vars)")

    return api_key, API_BASE


def _request(method: str, url: str, data: dict = None, headers: dict = None,
             timeout: int = 30) -> dict:
    """Generic HTTP request"""
    if headers is None:
        headers = {}

    headers.setdefault("User-Agent", "PlumeSkill/1.0")

    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")

    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        try:
            return json.loads(error_body)
        except json.JSONDecodeError:
            return {
                "success": False,
                "code": f"HTTP_{e.code}",
                "message": error_body or str(e),
            }
    except urllib.error.URLError as e:
        return {
            "success": False,
            "code": "NETWORK_ERROR",
            "message": str(e.reason),
        }


def _detect_mime_type(file_data: bytes, file_path: str) -> str:
    """Detect real MIME type via magic bytes, file extension as fallback"""
    import mimetypes

    # Check magic bytes
    if file_data[:3] == b'\xff\xd8\xff':
        return "image/jpeg"
    if file_data[:8] == b'\x89PNG\r\n\x1a\n':
        return "image/png"
    if file_data[:4] == b'RIFF' and file_data[8:12] == b'WEBP':
        return "image/webp"
    if file_data[:6] in (b'GIF87a', b'GIF89a'):
        return "image/gif"

    # Fallback to file extension inference
    return mimetypes.guess_type(file_path)[0] or "application/octet-stream"


def _upload_multipart(url: str, file_path: str, headers: dict,
                      timeout: int = 60) -> dict:
    """multipart/form-data file upload"""
    from uuid import uuid4

    boundary = f"----PlumeUpload{uuid4().hex}"
    filename = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        file_data = f.read()

    content_type = _detect_mime_type(file_data, file_path)

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n"
        f"\r\n"
    ).encode("utf-8") + file_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

    headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    headers.setdefault("User-Agent", "PlumeSkill/1.0")

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        try:
            return json.loads(error_body)
        except json.JSONDecodeError:
            return {"success": False, "code": f"HTTP_{e.code}", "message": error_body}
    except urllib.error.URLError as e:
        return {"success": False, "code": "NETWORK_ERROR", "message": str(e.reason)}


def create_task(category: str, content: dict, project_id: str = None,
                widget_mapping: dict = None, title: str = None) -> dict:
    """
    Create AI task
    Returns: { success, code, message, data: { id, status, ... } }
    """
    api_key, api_base = get_config()
    url = f"{api_base}/api/open/tasks"

    payload = {
        "category": category,
        "content": content,
        "type": 2,  # Async polling
    }
    if title:
        payload["title"] = title
    if project_id:
        payload["project_id"] = project_id
    if widget_mapping:
        payload["widget_mapping"] = widget_mapping

    return _request("POST", url, data=payload, headers={
        "Authorization": f"Bearer {api_key}",
    })


def get_task(task_id: str) -> dict:
    """
    Query single task status
    Returns: { success, code, message, data: { id, status, result, ... } }
    """
    api_key, api_base = get_config()
    url = f"{api_base}/api/open/tasks/{task_id}"

    return _request("GET", url, headers={
        "Authorization": f"Bearer {api_key}",
    })


def upload_image(file_path: str) -> dict:
    """
    Upload image to R2
    Returns: { success, data: { file_key, file_url, file_size, width, height } }
    """
    api_key, api_base = get_config()
    url = f"{api_base}/api/open/upload"

    if not os.path.isfile(file_path):
        return {"success": False, "code": "FILE_NOT_FOUND", "message": f"File not found: {file_path}"}

    return _upload_multipart(url, file_path, headers={
        "Authorization": f"Bearer {api_key}",
    })


def describe_image(image_url: str, focus: str = "general") -> dict:
    """
    Call VL model to describe image content
    Returns: { success, data: { description, model, tokens_used } }
    """
    api_key, api_base = get_config()
    url = f"{api_base}/api/open/describe"

    return _request("POST", url, data={
        "image_url": image_url,
        "focus": focus,
    }, headers={
        "Authorization": f"Bearer {api_key}",
    })


def batch_get_tasks(task_ids: list) -> dict:
    """
    Batch query tasks
    Returns: { success, data: [ { id, status, result, ... }, ... ] }
    """
    api_key, api_base = get_config()
    ids_str = ",".join(str(tid) for tid in task_ids)
    url = f"{api_base}/api/open/tasks/batch?ids={ids_str}"

    return _request("GET", url, headers={
        "Authorization": f"Bearer {api_key}",
    })


def validate_api_key() -> dict:
    """
    Validate if API Key is valid
    Returns: { success, data: { valid, user_id } }
    """
    api_key, api_base = get_config()
    url = f"{api_base}/api/open/validate"

    return _request("GET", url, headers={
        "Authorization": f"Bearer {api_key}",
    })
