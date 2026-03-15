#!/usr/bin/env python3
"""
Feishu message push script
Subcommands:
  text   -- Send text message
  image  -- Send image message (upload image to Feishu then send)
  video  -- Send video message (upload video to Feishu then send)
  auto   -- Auto-select image/video based on file extension

All commands output JSON format.
"""

import argparse
import json
import os
import ssl
import sys
import urllib.request
import urllib.error
from pathlib import Path

# Import shared modules (same directory)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import feishu_auth
import video_utils

FEISHU_API_BASE = feishu_auth.FEISHU_API_BASE

SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE


def log(msg: str):
    print(f"[feishu-notify] {msg}", file=sys.stderr, flush=True)


def output(data: dict):
    print(json.dumps(data, ensure_ascii=False))


# --- Feishu API calls ---

def _send_message(token: str, receive_id: str, msg_type: str, content: dict) -> dict:
    """Send message via Feishu API (auto-detect target type)

    Args:
        receive_id: Feishu open_id (ou_xxx -> private chat) or chat_id (oc_xxx -> group)
    """
    # Auto-select receive_id_type based on ID prefix
    if receive_id.startswith("oc_"):
        receive_id_type = "chat_id"
    else:
        receive_id_type = "open_id"

    url = f"{FEISHU_API_BASE}/im/v1/messages?receive_id_type={receive_id_type}"
    data = json.dumps({
        "receive_id": receive_id,
        "msg_type": msg_type,
        "content": json.dumps(content),
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    })
    try:
        with urllib.request.urlopen(req, timeout=30, context=SSL_CONTEXT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"code": e.code, "msg": body}
    except Exception as e:
        return {"code": -1, "msg": str(e)}


def _upload_image(token: str, file_path: str) -> str | None:
    """Upload image to Feishu, return image_key"""
    url = f"{FEISHU_API_BASE}/im/v1/images"
    return _upload_file_multipart(token, url, file_path, {
        "image_type": "message",
    }, file_field_name="image")


def _upload_file(token: str, file_path: str, file_type: str = "stream") -> str | None:
    """Upload file to Feishu (video etc.), return file_key"""
    url = f"{FEISHU_API_BASE}/im/v1/files"
    extra_fields = {
        "file_type": file_type,
        "file_name": os.path.basename(file_path),
    }
    return _upload_file_multipart(token, url, file_path, extra_fields, key_field="file_key")


def _upload_file_multipart(token: str, url: str, file_path: str,
                           extra_fields: dict, key_field: str = "image_key",
                           file_field_name: str = "file") -> str | None:
    """Generic multipart upload to Feishu"""
    from uuid import uuid4
    import mimetypes

    boundary = f"----FeishuUpload{uuid4().hex}"
    filename = os.path.basename(file_path)
    content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

    # Build multipart body
    parts = []
    for field_name, field_value in extra_fields.items():
        parts.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{field_name}"\r\n\r\n'
            f"{field_value}\r\n"
        )

    file_header = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{file_field_name}"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    )

    with open(file_path, "rb") as f:
        file_data = f.read()

    body = "".join(parts).encode("utf-8") + file_header.encode("utf-8") + file_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=120, context=SSL_CONTEXT) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        if result.get("code") != 0:
            log(f"Upload failed: {result}")
            return None
        return result.get("data", {}).get(key_field)
    except Exception as e:
        log(f"Upload error: {e}")
        return None


# --- Public send functions (for direct import by poll_cron_feishu.py etc.) ---

def send_text(user_id: str, message: str, account: str = "main") -> dict:
    """Send text message"""
    token = feishu_auth.get_token(account)
    if not token:
        return {"success": False, "error": "Failed to get Feishu token"}
    result = _send_message(token, user_id, "text", {"text": message})
    success = result.get("code") == 0
    return {"success": success, "result": result}


def send_image(user_id: str, file_path: str, account: str = "main") -> dict:
    """Send image message"""
    token = feishu_auth.get_token(account)
    if not token:
        return {"success": False, "error": "Failed to get Feishu token"}

    image_key = _upload_image(token, file_path)
    if not image_key:
        return {"success": False, "error": "Failed to upload image to Feishu"}

    result = _send_message(token, user_id, "image", {"image_key": image_key})
    success = result.get("code") == 0
    return {"success": success, "image_key": image_key, "result": result}


def send_video(user_id: str, file_path: str, account: str = "main", cover_path: str | None = None) -> dict:
    """Send video message (Feishu requires media messages to provide both file_key and image_key)

    Args:
        cover_path: Cover image path. posterUrl from veo task result can be used as cover.
                    If no cover image, will fallback to text notification.
    """
    token = feishu_auth.get_token(account)
    if not token:
        return {"success": False, "error": "Failed to get Feishu token"}

    duration_ms = video_utils.get_mp4_duration_ms(file_path)
    log(f"Video duration: {duration_ms}ms" if duration_ms else "Unable to parse video duration")

    # Upload video to Feishu (using mp4 type)
    file_key = _upload_file(token, file_path, file_type="mp4")
    if not file_key:
        return {"success": False, "error": "Failed to upload video to Feishu"}

    # Try to upload cover image
    image_key = None
    if cover_path and os.path.isfile(cover_path):
        image_key = _upload_image(token, cover_path)
        if not image_key:
            log("Failed to upload cover image to Feishu")

    if image_key:
        # Has cover image: use media message type to send playable video
        result = _send_message(token, user_id, "media", {
            "file_key": file_key,
            "image_key": image_key,
        })
    else:
        # No cover image: fallback to text notification
        log("No cover image, falling back to text notification")
        result = _send_message(token, user_id, "text", {
            "text": "Video generation complete, but missing cover image so cannot push video file directly. Please contact admin.",
        })

    success = result.get("code") == 0
    return {"success": success, "file_key": file_key, "image_key": image_key, "result": result}


def send_auto(user_id: str, file_path: str, account: str = "main") -> dict:
    """Auto-select send method based on file extension"""
    if video_utils.is_video_file(file_path):
        return send_video(user_id, file_path, account)
    else:
        return send_image(user_id, file_path, account)


# --- CLI subcommands ---

def cmd_text(args):
    result = send_text(args.user_id, args.message, args.feishu_account)
    output(result)


def cmd_image(args):
    if not os.path.isfile(args.file):
        output({"success": False, "error": f"File not found: {args.file}"})
        return
    result = send_image(args.user_id, args.file, args.feishu_account)
    output(result)


def cmd_video(args):
    if not os.path.isfile(args.file):
        output({"success": False, "error": f"File not found: {args.file}"})
        return
    cover_path = getattr(args, "cover", None)
    result = send_video(args.user_id, args.file, args.feishu_account, cover_path=cover_path)
    output(result)


def cmd_auto(args):
    if not os.path.isfile(args.file):
        output({"success": False, "error": f"File not found: {args.file}"})
        return
    result = send_auto(args.user_id, args.file, args.feishu_account)
    output(result)


# --- CLI entry ---

def main():
    parser = argparse.ArgumentParser(description="Feishu message push")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Common arguments
    def add_common_args(p):
        p.add_argument("--user-id", required=True, help="Feishu user open_id")
        p.add_argument("--feishu-account", default="main", help="Feishu account name")

    # text
    p_text = subparsers.add_parser("text", help="Send text message")
    add_common_args(p_text)
    p_text.add_argument("--message", required=True, help="Message content")

    # image
    p_image = subparsers.add_parser("image", help="Send image message")
    add_common_args(p_image)
    p_image.add_argument("--file", required=True, help="Image file path")

    # video
    p_video = subparsers.add_parser("video", help="Send video message")
    add_common_args(p_video)
    p_video.add_argument("--file", required=True, help="Video file path")
    p_video.add_argument("--cover", help="Cover image path (Feishu video messages require a cover image)")

    # auto
    p_auto = subparsers.add_parser("auto", help="Auto-detect type and send")
    add_common_args(p_auto)
    p_auto.add_argument("--file", required=True, help="File path")

    args = parser.parse_args()

    commands = {
        "text": cmd_text,
        "image": cmd_image,
        "video": cmd_video,
        "auto": cmd_auto,
    }

    try:
        log(f"=== feishu_notify.py {args.command} called ===")
        commands[args.command](args)
    except Exception as e:
        output({"success": False, "error": str(e)})
        sys.exit(1)


if __name__ == "__main__":
    main()
