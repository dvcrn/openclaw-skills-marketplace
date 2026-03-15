#!/usr/bin/env python3
"""
Image processing orchestration script
Subcommands:
  transfer  -- Transfer Feishu image to R2
  create    -- Create AI task
  poll      -- Poll task status, download result image on success

All commands output JSON format for Agent parsing.
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
import ssl
from pathlib import Path

# Import plume_api module (same directory)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plume_api
import video_utils
import feishu_auth

# Result image download directory (under OpenClaw allowed media directory)
MEDIA_DIR = Path.home() / ".openclaw" / "media" / "plume"

# SSL context for downloading
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE


def log(msg: str):
    """Output debug log to stderr (does not affect stdout JSON output)"""
    print(f"[plume-image] {msg}", file=sys.stderr, flush=True)


def output(data: dict):
    """Output JSON result to stdout"""
    print(json.dumps(data, ensure_ascii=False))


def ensure_media_dir() -> Path:
    """Ensure media directory exists"""
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    return MEDIA_DIR


def _download_feishu_image(image_key: str, token: str, output_path: str) -> bool:
    """Download image from Feishu API to local"""
    url = f"{feishu_auth.FEISHU_API_BASE}/im/v1/images/{image_key}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
    })
    try:
        with urllib.request.urlopen(req, timeout=60, context=SSL_CONTEXT) as resp:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(resp.read())
        return True
    except Exception as e:
        log(f"Feishu image download failed: {e}")
        return False


def download_file(url: str, output_path: str, timeout: int = 120) -> bool:
    """Download file to local"""
    req = urllib.request.Request(url, headers={"User-Agent": "Plume-Image/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT) as resp:
            with open(output_path, "wb") as f:
                while True:
                    chunk = resp.read(1024 * 1024)  # 1MB chunks
                    if not chunk:
                        break
                    f.write(chunk)
        # Verify file is not empty
        if os.path.getsize(output_path) == 0:
            log(f"Download error: file is empty {output_path}")
            os.remove(output_path)
            return False
        return True
    except (urllib.error.URLError, IOError, TimeoutError) as e:
        log(f"Download failed: {e}")
        # Clean up possible empty file
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
        except OSError:
            pass
        return False


# --- transfer subcommand ---

def _upload_to_r2(file_path: str) -> dict:
    """Upload local file to R2, return unified output dict"""
    upload_result = plume_api.upload_image(file_path)

    if not upload_result.get("success"):
        return {"success": False, "step": "upload_to_r2",
                "error": upload_result.get("message", "R2 upload failed")}

    data = upload_result.get("data", {})
    return {
        "success": True,
        "image_url": data.get("file_url"),
        "file_key": data.get("file_key"),
        "file_size": data.get("file_size"),
        "width": data.get("width"),
        "height": data.get("height"),
    }


def cmd_transfer(args):
    """
    Transfer image to R2, supports two sources:
    1. --image-key: Feishu image_key, download via Feishu API then upload to R2
    2. --file: Local file path (e.g. OpenClaw inbound image), upload directly to R2
    """
    local_file = args.file
    image_key = args.image_key

    if not local_file and not image_key:
        output({"success": False, "error": "Must specify either --image-key or --file"})
        return

    # Mode A: Upload local file directly
    if local_file:
        # Strip possible file:// prefix
        if local_file.startswith("file://"):
            local_file = local_file[7:]

        if not os.path.exists(local_file):
            output({"success": False, "error": f"File not found: {local_file}"})
            return

        log(f"transfer: uploading local file to R2, file={local_file}")
        output(_upload_to_r2(local_file))
        return

    # Mode B: Download from Feishu image_key then upload
    account = args.feishu_account or "main"

    token = feishu_auth.get_token(account)
    if not token:
        output({"success": False, "error": "Failed to get Feishu tenant_access_token"})
        return

    media_dir = ensure_media_dir()
    tmp_path = str(media_dir / f"transfer_{image_key}.jpg")

    try:
        if not _download_feishu_image(image_key, token, tmp_path):
            output({"success": False, "step": "download_from_feishu",
                     "error": "Feishu image download failed"})
            return

        output(_upload_to_r2(tmp_path))

    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except OSError:
            pass


# --- create subcommand ---

def _is_local_path(url: str) -> bool:
    """Check if path is a local file path (not a remote URL)"""
    if not url:
        return False
    return url.startswith("file://") or url.startswith("/")


def _auto_transfer_local_file(file_path: str) -> str | None:
    """Auto-upload local file to R2, return remote URL. Returns None on failure."""
    # Strip file:// prefix
    if file_path.startswith("file://"):
        file_path = file_path[7:]

    if not os.path.exists(file_path):
        return None

    log(f"auto-transfer: detected local file, auto-uploading to R2: {file_path}")
    upload_result = plume_api.upload_image(file_path)

    if not upload_result.get("success"):
        log(f"auto-transfer: upload failed: {upload_result.get('message', 'unknown')}")
        return None

    r2_url = upload_result.get("data", {}).get("file_url")
    log(f"auto-transfer: upload successful -> {r2_url}")
    return r2_url


VALID_CATEGORIES = {"BananaPro", "Banana2", "remove-bg", "remove-watermark", "seedream", "veo", "seedance2"}


def cmd_create(args):
    """
    Create AI task

    content structure must align with executor:
    - processing_mode: text_to_image / image_to_image / multi_image_blend
    - prompt: description text
    - imageUrls: reference image URL array
    - generationConfig: { imageConfig: { image_size, aspectRatio }, responseModalities }
    """
    category = args.category

    # Category whitelist validation
    if category not in VALID_CATEGORIES:
        output({
            "success": False,
            "error": f"Invalid category: '{category}'. "
                     f"Only allowed: {', '.join(sorted(VALID_CATEGORIES))}. "
                     f"For style transfer, use category='Banana2' and describe the target style in --prompt.",
        })
        return

    content = {}

    # Handle --image-urls (multi-image blend): comma-separated multiple URLs
    multi_image_urls = None
    if args.image_urls:
        multi_image_urls = [u.strip() for u in args.image_urls.split(",") if u.strip()]
        # Auto-upload local files to R2
        for i, url in enumerate(multi_image_urls):
            if _is_local_path(url):
                r2_url = _auto_transfer_local_file(url)
                if not r2_url:
                    output({
                        "success": False,
                        "error": f"Failed to upload local file to R2: {url}. Please use transfer --file first.",
                    })
                    return
                multi_image_urls[i] = r2_url

    # Intercept local file paths: auto-upload to R2
    if args.image_url and _is_local_path(args.image_url):
        r2_url = _auto_transfer_local_file(args.image_url)
        if not r2_url:
            output({
                "success": False,
                "error": f"Failed to upload local file to R2: {args.image_url}. Please use transfer --file first.",
            })
            return
        args.image_url = r2_url

    log(f"create: category={category}, prompt={args.prompt}, image_url={args.image_url}, image_urls={multi_image_urls}, mode={args.processing_mode}")

    # processing_mode (required for non remove-bg/remove-watermark)
    if category in ("remove-bg", "remove-watermark"):
        # Background/watermark removal doesn't need processing_mode and prompt
        if args.image_url:
            content["imageUrls"] = [args.image_url]
    elif category == "veo":
        # veo video generation: uses videoConfig instead of generationConfig
        # processing_mode: text_to_video / image_to_video
        has_image = args.image_url or args.first_frame_url or args.last_frame_url or args.reference_url
        if args.processing_mode:
            content["processing_mode"] = args.processing_mode
        elif has_image:
            content["processing_mode"] = "image_to_video"
        else:
            content["processing_mode"] = "text_to_video"

        if args.prompt:
            content["prompt"] = args.prompt

        # Build imageUrls with fixed 3 slots: [0]=first frame, [1]=last frame, [2]=reference
        # --image-url is equivalent to --first-frame-url (most common image-to-video scenario)
        first_frame = args.first_frame_url or args.image_url or ""
        last_frame = args.last_frame_url or ""
        reference = args.reference_url or ""
        if first_frame or last_frame or reference:
            content["imageUrls"] = [first_frame, last_frame, reference]

        video_config = {}
        video_config["model"] = "veo3.1-fast"
        if args.aspect_ratio:
            video_config["aspectRatio"] = args.aspect_ratio
        else:
            video_config["aspectRatio"] = "9:16"
        duration = getattr(args, "duration", None)
        video_config["durationSeconds"] = int(duration) if duration else 6
        content["videoConfig"] = video_config
    elif category == "seedance2":
        # seedance2 video generation: uses videoConfig, images passed via imageUrls (URL)
        # processing_mode: text_to_video / first_frame / first_last_frame / universal_reference
        has_image = args.image_url or args.first_frame_url or args.last_frame_url or args.reference_url
        if args.processing_mode:
            content["processing_mode"] = args.processing_mode
        elif has_image:
            content["processing_mode"] = "first_frame"
        else:
            content["processing_mode"] = "text_to_video"

        if args.prompt:
            content["prompt"] = args.prompt

        # imageUrls: image URL array (first frame, last frame, etc.)
        first_frame = args.first_frame_url or args.image_url or ""
        last_frame = args.last_frame_url or ""
        reference = args.reference_url or ""
        image_urls = [u for u in [first_frame, last_frame, reference] if u]
        if image_urls:
            content["imageUrls"] = image_urls

        # videoConfig: model determines duration (seedance2-5s/10s/15s), default seedance2-5s
        video_config = {}
        duration = getattr(args, "duration", None)
        if duration:
            video_config["model"] = f"seedance2-{int(duration)}s"
        else:
            video_config["model"] = args.model or "seedance2-5s"
        if args.aspect_ratio:
            video_config["aspectRatio"] = args.aspect_ratio
        else:
            video_config["aspectRatio"] = "9:16"
        content["videoConfig"] = video_config
    else:
        # Image categories (BananaPro/Banana2/seedream etc.)
        # Determine processing_mode
        if args.processing_mode:
            content["processing_mode"] = args.processing_mode
        elif multi_image_urls and len(multi_image_urls) > 1:
            content["processing_mode"] = "image_to_image"
        elif args.image_url:
            content["processing_mode"] = "image_to_image"
        else:
            content["processing_mode"] = "text_to_image"

        if args.prompt:
            content["prompt"] = args.prompt
        if multi_image_urls:
            content["imageUrls"] = multi_image_urls
        elif args.image_url:
            content["imageUrls"] = [args.image_url]

        # generationConfig
        image_config = {}
        if args.image_size:
            image_config["image_size"] = args.image_size
        if args.aspect_ratio:
            image_config["aspectRatio"] = args.aspect_ratio

        if image_config or category in ("BananaPro", "Banana2"):
            # Has specified params or BananaPro/Banana2 series default with generationConfig
            if not image_config.get("image_size"):
                image_config["image_size"] = "2K"
            if not image_config.get("aspectRatio"):
                image_config["aspectRatio"] = "9:16"
            gen_config = {
                "responseModalities": ["IMAGE"],
                "imageConfig": image_config,
            }
            # seedream doesn't need responseModalities
            if category == "seedream":
                del gen_config["responseModalities"]
                if not image_config.get("image_size"):
                    image_config["image_size"] = "2K"
            content["generationConfig"] = gen_config

    result = plume_api.create_task(
        category=category,
        content=content,
        project_id=args.project_id,
        widget_mapping=json.loads(args.widget_mapping) if args.widget_mapping else None,
        title=args.title,
    )

    log(f"create result: {json.dumps(result, ensure_ascii=False)[:500]}")

    if result.get("success"):
        task_data = result.get("data", {})
        output({
            "success": True,
            "task_id": task_data.get("id"),
            "status": task_data.get("status"),
            "credits_cost": task_data.get("credits_cost"),
        })
    else:
        output({
            "success": False,
            "code": result.get("code"),
            "error": result.get("message", "Task creation failed"),
        })


# --- poll subcommand ---

def _extract_result_url(task_result: dict) -> tuple[str | None, str]:
    """Extract result URL and media type from task result
    Returns (url, media_type), media_type is 'image' or 'video'
    """
    if not isinstance(task_result, dict):
        return None, "image"
    # Check video fields first (veo returns: {"parts": [{"videoUrl": "https://...", "duration": 6}]})
    if task_result.get("parts"):
        parts = task_result["parts"]
        if isinstance(parts, list) and len(parts) > 0:
            first_part = parts[0]
            if isinstance(first_part, dict) and first_part.get("videoUrl"):
                return first_part["videoUrl"], "video"
    # Then check image fields
    url = task_result.get("imageUrl") or task_result.get("url")
    if not url and task_result.get("imageUrls"):
        url = task_result["imageUrls"][0]
    if not url and task_result.get("parts"):
        parts = task_result["parts"]
        if isinstance(parts, list) and len(parts) > 0:
            first_part = parts[0]
            if isinstance(first_part, dict):
                url = first_part.get("imageUrl") or first_part.get("url")
    # Check nested data.file structure (e.g. remove-watermark returns: {"status": 200, "data": {"file": "https://..."}})
    if not url:
        data = task_result.get("data")
        if isinstance(data, dict):
            url = data.get("file") or data.get("imageUrl") or data.get("url")
    return url, "image"


def cmd_poll(args):
    """
    Poll task status until completion, auto-download result image to ~/.openclaw/media/plume/ on success
    Returns local file path for Agent to send directly to user.
    """
    task_id = args.task_id
    max_attempts = args.max_attempts or 60
    interval = args.interval or 3
    log(f"poll: task_id={task_id}, max_attempts={max_attempts}, interval={interval}")

    for attempt in range(1, max_attempts + 1):
        result = plume_api.get_task(task_id)

        if not result.get("success"):
            output({
                "success": False,
                "error": result.get("message", "Task query failed"),
                "attempt": attempt,
            })
            return

        task = result.get("data", {})
        status = task.get("status", 0)

        # Final state check
        if status >= 3:
            if status == 3:
                # Parse result
                task_result = task.get("result")
                if isinstance(task_result, str):
                    try:
                        task_result = json.loads(task_result)
                    except json.JSONDecodeError:
                        pass

                result_url, media_type = _extract_result_url(task_result)

                if result_url:
                    # Detect file suffix (check video suffix first, then image suffix)
                    video_suffix = video_utils.get_video_suffix(result_url)
                    if video_suffix:
                        suffix = video_suffix
                        media_type = "video"
                    elif ".jpg" in result_url.lower() or ".jpeg" in result_url.lower():
                        suffix = ".jpg"
                    elif ".webp" in result_url.lower():
                        suffix = ".webp"
                    else:
                        suffix = ".png"

                    media_dir = ensure_media_dir()
                    local_file = str(media_dir / f"result_{task_id}{suffix}")

                    # Use larger timeout for video files
                    dl_timeout = 300 if media_type == "video" else 120
                    if download_file(result_url, local_file, timeout=dl_timeout):
                        file_size = os.path.getsize(local_file)
                        label = "video" if media_type == "video" else "image"
                        log(f"OK: {label} downloaded to {local_file} ({file_size} bytes)")
                        output({
                            "success": True,
                            "status": status,
                            "status_text": "success",
                            "media_type": media_type,
                            "local_file": local_file,
                            "result_url": result_url,
                            "attempts": attempt,
                            "IMPORTANT": f"When sending {label}, filePath must use this full absolute path: {local_file}",
                        })
                    else:
                        log(f"WARN: download failed, returning URL")
                        output({
                            "success": True,
                            "status": status,
                            "status_text": "success",
                            "media_type": media_type,
                            "result_url": result_url,
                            "download_failed": True,
                            "attempts": attempt,
                        })
                else:
                    log("WARN: result_url not found")
                    output({
                        "success": True,
                        "status": status,
                        "status_text": "success",
                        "result": task_result,
                        "attempts": attempt,
                    })
            else:
                status_map = {4: "failed", 5: "timeout", 6: "cancelled"}
                output({
                    "success": False,
                    "status": status,
                    "status_text": status_map.get(status, f"unknown({status})"),
                    "result": task.get("result"),
                    "attempts": attempt,
                })
            return

        # Not in final state, wait then continue polling
        if attempt < max_attempts:
            time.sleep(interval)

    # Exceeded max poll attempts
    output({
        "success": False,
        "error": f"Poll timeout: task not completed within {max_attempts * interval} seconds",
        "task_id": task_id,
        "attempts": max_attempts,
    })


# --- CLI entry ---

def main():
    parser = argparse.ArgumentParser(description="Plume image processing orchestration script")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # transfer
    p_transfer = subparsers.add_parser("transfer", help="Transfer image to R2 (Feishu image_key or local file)")
    p_transfer.add_argument("--image-key", help="Feishu image_key")
    p_transfer.add_argument("--file", help="Local file path (e.g. OpenClaw inbound image)")
    p_transfer.add_argument("--feishu-account", default="main", help="Feishu account name")

    # create
    p_create = subparsers.add_parser("create", help="Create AI task")
    p_create.add_argument("--category", required=True, help="Task type (BananaPro/Banana2/remove-bg/remove-watermark/seedream/...)")
    p_create.add_argument("--prompt", help="Text description prompt")
    p_create.add_argument("--image-url", help="Reference image URL (image-to-image; equivalent to --first-frame-url for veo)")
    p_create.add_argument("--image-urls", help="Multiple reference image URLs, comma-separated (for multi-image blend), overrides --image-url")
    p_create.add_argument("--first-frame-url", help="veo first frame URL (imageUrls[0])")
    p_create.add_argument("--last-frame-url", help="veo last frame URL (imageUrls[1])")
    p_create.add_argument("--reference-url", help="veo reference image URL (imageUrls[2], components mode)")
    p_create.add_argument("--processing-mode", help="text_to_image / image_to_image / multi_image_blend / text_to_video / image_to_video")
    p_create.add_argument("--image-size", default=None, help="Image resolution: 1K / 2K / 4K")
    p_create.add_argument("--aspect-ratio", default=None, help="Image aspect ratio: 1:1 / 16:9 / 9:16 / 4:3 / 3:4")
    p_create.add_argument("--duration", type=int, default=None, help="Video duration (seconds), only for veo/seedance2 category")
    p_create.add_argument("--model", default=None, help="Model name, e.g. seedance2-5s/seedance2-10s/seedance2-15s")
    p_create.add_argument("--title", help="Task title")
    p_create.add_argument("--project-id", help="Associated project ID")
    p_create.add_argument("--widget-mapping", help="Widget mapping (JSON string)")

    # poll
    p_poll = subparsers.add_parser("poll", help="Poll task status and download result")
    p_poll.add_argument("--task-id", required=True, help="Task ID")
    p_poll.add_argument("--max-attempts", type=int, default=60, help="Maximum poll attempts")
    p_poll.add_argument("--interval", type=int, default=3, help="Poll interval (seconds)")

    args = parser.parse_args()

    commands = {
        "transfer": cmd_transfer,
        "create": cmd_create,
        "poll": cmd_poll,
    }

    try:
        log(f"=== process_image.py {args.command} called, argv={sys.argv[1:]} ===")
        commands[args.command](args)
    except Exception as e:
        output({"success": False, "error": str(e)})
        sys.exit(1)


if __name__ == "__main__":
    main()
