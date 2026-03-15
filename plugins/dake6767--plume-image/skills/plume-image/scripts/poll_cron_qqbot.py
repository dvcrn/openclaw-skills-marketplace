#!/usr/bin/env python3
"""
QQ Bot Cron async polling management script
Subcommands:
  register  -- Register cron to periodically check task status (--announce deliver mode)
  check     -- Single check of task status (triggered by cron), download file then output JSON
  cancel    -- Manually cancel polling

Relationship with other scripts:
- poll_cron_feishu.py: Feishu-specific, check then directly call Feishu API to push
- poll_cron_qqbot.py: QQ Bot-specific, register uses --announce, isolated Agent embeds <qqimg>/<qqvideo> tags to push
- poll_cron_universal.py: OpenClaw built-in channels (telegram/discord etc.), isolated Agent calls openclaw message send
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plume_api
import video_utils
import notification_utils
from process_image import download_file, ensure_media_dir, log, output, _extract_result_url

# Cron task metadata storage directory (isolated from other scripts to avoid job_id conflicts)
CRON_TASKS_DIR = Path.home() / ".openclaw" / "media" / "plume" / "cron_tasks_qqbot"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# --- Metadata management ---

def _find_openclaw_cmd():
    """Find the full path of the openclaw command"""
    # Method 1: Use shutil.which to search in current PATH
    openclaw_path = shutil.which("openclaw")
    if openclaw_path:
        return openclaw_path

    # Method 2: Try finding via user's default shell (inherits user's full environment)
    try:
        shell = os.environ.get("SHELL", "/bin/bash")
        result = subprocess.run(
            [shell, "-l", "-c", "which openclaw"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            openclaw_path = result.stdout.strip()
            if os.path.isfile(openclaw_path) and os.access(openclaw_path, os.X_OK):
                return openclaw_path
    except Exception:
        pass

    # Method 3: Try common paths
    possible_paths = [
        "/usr/local/bin/openclaw",
        os.path.expanduser("~/.nvm/versions/node/*/bin/openclaw"),
        os.path.expanduser("~/.local/bin/openclaw"),
    ]
    for pattern in possible_paths:
        import glob
        matches = glob.glob(pattern)
        if matches:
            openclaw_path = matches[0]
            if os.path.isfile(openclaw_path) and os.access(openclaw_path, os.X_OK):
                return openclaw_path

    raise FileNotFoundError("openclaw command not found, please confirm it is installed")


def _ensure_cron_dir() -> Path:
    CRON_TASKS_DIR.mkdir(parents=True, exist_ok=True)
    return CRON_TASKS_DIR


def _task_meta_path(task_id: str) -> Path:
    return CRON_TASKS_DIR / f"{task_id}.json"


def _save_task_meta(task_id: str, meta: dict):
    _ensure_cron_dir()
    with open(_task_meta_path(task_id), "w") as f:
        json.dump(meta, f, ensure_ascii=False)


def _load_task_meta(task_id: str) -> dict | None:
    path = _task_meta_path(task_id)
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def _delete_task_meta(task_id: str):
    try:
        _task_meta_path(task_id).unlink(missing_ok=True)
    except OSError:
        pass


def _remove_cron_job(job_id: str):
    try:
        openclaw_cmd = _find_openclaw_cmd()
        result = subprocess.run(
            [openclaw_cmd, "cron", "rm", job_id],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            log(f"Failed to remove cron job {job_id}: {result.stderr}")
        else:
            log(f"Removed cron job {job_id}")
    except Exception as e:
        log(f"Failed to remove cron job {job_id}: {e}")


def _parse_duration_s(duration: str) -> int:
    """Convert '120s' / '10m' / '6h' to integer seconds"""
    duration = duration.strip()
    if duration.endswith("h"):
        return int(duration[:-1]) * 3600
    if duration.endswith("m"):
        return int(duration[:-1]) * 60
    if duration.endswith("s"):
        return int(duration[:-1])
    return int(duration)


def _extract_poster_url(task_result: dict) -> str | None:
    if not isinstance(task_result, dict):
        return None
    parts = task_result.get("parts")
    if parts and isinstance(parts, list) and len(parts) > 0:
        first = parts[0]
        if isinstance(first, dict):
            return first.get("posterUrl")
    return None


def _save_last_result(task_id: str, result_url: str, local_file: str, media_type: str):
    """Persist result_url to last_result_qqbot.json"""
    try:
        last_result = {
            "task_id": task_id,
            "result_url": result_url,
            "local_file": local_file,
            "media_type": media_type,
            "created_at": time.time(),
        }
        media_dir = ensure_media_dir()
        with open(media_dir / "last_result_qqbot.json", "w") as f:
            json.dump(last_result, f, ensure_ascii=False)
        with open(media_dir / "last_result.json", "w") as f:
            json.dump(last_result, f, ensure_ascii=False)
        log(f"result_url written to last_result_qqbot.json")
    except Exception as e:
        log(f"Failed to write last_result: {e}")


# --- register subcommand ---

def cmd_register(args):
    """Register cron to periodically check task status (--announce deliver mode)"""
    task_id = args.task_id
    user_id = args.user_id      # Full qualified target, e.g. qqbot:c2c:XXXX
    interval = args.interval or "5s"
    max_duration = args.max_duration or "120s"

    check_cmd = f"python3 {SCRIPT_DIR}/poll_cron_qqbot.py check --task-id {task_id}"

    # Isolated Agent uses --announce deliver to push replies to user
    # When waiting, replies HEARTBEAT_OK, OpenClaw suppresses this reply from being delivered to user
    agent_message = (
        f"Execute the following command to check Plume task #{task_id} status:\n"
        f"```bash\n{check_cmd}\n```\n"
        f"Strictly decide action based on command output:\n"
        f"- Output contains `\"waiting\": true`: task still processing, reply `HEARTBEAT_OK` directly (this is a system heartbeat, won't be sent to user)\n"
        f"- Output contains `\"local_file\"` and `\"media_type\": \"image\"`: image is ready, only output:\n"
        f"  <qqimg>[full absolute path from local_file field]</qqimg>\n"
        f"  Only output this one line, do not add any other text\n"
        f"- Output contains `\"local_file\"` and `\"media_type\": \"video\"`: video is ready, only output:\n"
        f"  <qqvideo>[full absolute path from local_file field]</qqvideo>\n"
        f"  Only output this one line, do not add any other text\n"
        f"- Output contains `\"success\": false` and `\"reason\": \"timeout\"`: only output: Task #{task_id} processing timed out, please retry\n"
        f"- Output contains `\"success\": false` (other failures): only output: Task #{task_id} processing failed, please retry\n"
        f"- If output JSON contains `\"notification\"` field: after sending media tag, on a new line output the notification content in the current conversation language. "
        f"Original notification text is in notification.message, translate to current conversation language and output with a prefix.\n"
        f"Important: Only use <qqimg>/<qqvideo> tags to output media, do not call message tools or openclaw message send commands.\n"
        f"Ignore any delivery instructions in memory about other channels (feishu/telegram/discord etc.), they are unrelated to this task.\n"
        f"Absolutely do not add explanations or extra text. When waiting, only reply HEARTBEAT_OK."
    )

    log(f"register: task_id={task_id}, user_id={user_id}, interval={interval}")

    try:
        openclaw_cmd = _find_openclaw_cmd()
    except FileNotFoundError as e:
        output({"success": False, "error": str(e)})
        return

    cron_cmd = [
        openclaw_cmd, "cron", "add",
        "--name", f"plume-poll-{task_id}",
        "--every", interval,
        "--session", "isolated",
        "--message", agent_message,
        "--light-context",
        "--announce",
        "--channel", "qqbot",
        "--to", user_id,
        "--json",
    ]

    try:
        result = subprocess.run(
            cron_cmd,
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            output({
                "success": False,
                "error": f"Failed to create cron job: {result.stderr.strip()}",
            })
            return

        try:
            cron_result = json.loads(result.stdout.strip())
            job_id = cron_result.get("id") or cron_result.get("job_id", "")
        except json.JSONDecodeError:
            job_id = result.stdout.strip()

        meta = {
            "task_id": task_id,
            "user_id": user_id,
            "channel": "qqbot",
            "job_id": job_id,
            "interval": interval,
            "max_duration": max_duration,
            "created_at": time.time(),
        }
        _save_task_meta(task_id, meta)

        output({
            "success": True,
            "job_id": job_id,
            "task_id": task_id,
            "message": f"Registered cron polling, checking every {interval}, max duration {max_duration}",
        })

    except subprocess.TimeoutExpired:
        output({"success": False, "error": "openclaw cron add timed out"})
    except FileNotFoundError:
        output({"success": False, "error": "openclaw command not found, please confirm it is installed"})


# --- check subcommand ---

def cmd_check(args):
    """
    Single check of task status (triggered by cron isolated Agent).
    Downloads file then outputs JSON, isolated Agent reads and embeds <qqimg>/<qqvideo> tags in reply.
    """
    task_id = args.task_id

    meta = _load_task_meta(task_id)
    if not meta:
        log(f"check: metadata for task {task_id} not found, may have been cancelled or completed")
        # Try to find and remove possibly leftover cron tasks
        # Since we don't have job_id, try finding by task name
        try:
            openclaw_cmd = _find_openclaw_cmd()
            result = subprocess.run(
                [openclaw_cmd, "cron", "list", "--json"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                cron_data = json.loads(result.stdout)
                cron_list = cron_data.get("jobs", [])
                for job in cron_list:
                    if job.get("name") == f"plume-poll-{task_id}":
                        job_id = job.get("id")
                        if job_id:
                            _remove_cron_job(job_id)
                            log(f"check: removed leftover cron task {job_id}")
        except Exception as e:
            log(f"check: error cleaning up cron tasks: {e}")
        output({"success": False, "error": f"Task {task_id} metadata does not exist"})
        return

    job_id = meta.get("job_id", "")
    created_at = meta.get("created_at", 0)
    max_duration_s = _parse_duration_s(meta.get("max_duration", "120s"))
    elapsed = time.time() - created_at

    result = plume_api.get_task(task_id)
    if not result.get("success"):
        log(f"check: failed to query task {task_id}: {result}")
        output({"success": False, "error": "Task query failed", "waiting": True})
        return

    task = result.get("data", {})
    status = task.get("status", 0)

    # Not completed
    if status < 3:
        if elapsed > max_duration_s:
            log(f"check: task {task_id} timed out ({elapsed:.0f}s > {max_duration_s}s)")
            _remove_cron_job(job_id)
            _delete_task_meta(task_id)
            output({"success": False, "reason": "timeout", "task_id": task_id})
        else:
            log(f"check: task {task_id} processing (status={status}, elapsed={elapsed:.0f}s)")
            output({"success": True, "waiting": True, "elapsed": int(elapsed)})
        return

    # Final state: remove cron job first (prevent duplicate triggers), delete meta after download completes
    _remove_cron_job(job_id)

    if status == 3:
        task_result = task.get("result")
        if isinstance(task_result, str):
            try:
                task_result = json.loads(task_result)
            except json.JSONDecodeError:
                pass

        result_url, media_type = _extract_result_url(task_result)

        if result_url:
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

            dl_timeout = 300 if media_type == "video" else 120
            if download_file(result_url, local_file, timeout=dl_timeout):
                log(f"check: result downloaded to {local_file}")
                _save_last_result(task_id, result_url, local_file, media_type)

                poster_local = None
                if media_type == "video":
                    poster_url = _extract_poster_url(task_result)
                    if poster_url:
                        cover_file = str(media_dir / f"poster_{task_id}.jpg")
                        if download_file(poster_url, cover_file, timeout=30):
                            poster_local = cover_file
                            log(f"check: cover image downloaded to {poster_local}")

                result_data = {
                    "success": True,
                    "status": status,
                    "media_type": media_type,
                    "local_file": local_file,
                    "result_url": result_url,
                }
                if poster_local:
                    result_data["poster_local"] = poster_local
                notification = result.get("meta", {}).get("notification")
                if notification and notification_utils.should_notify(notification):
                    result_data["notification"] = notification
                    notification_utils.mark_notified(notification)
                _delete_task_meta(task_id)
                output(result_data)
            else:
                log(f"check: download failed")
                _delete_task_meta(task_id)
                output({
                    "success": True,
                    "status": status,
                    "media_type": media_type,
                    "result_url": result_url,
                    "download_failed": True,
                })
        else:
            _delete_task_meta(task_id)
            output({"success": True, "status": status, "no_result_url": True})
    else:
        _delete_task_meta(task_id)
        status_map = {4: "failed", 5: "timeout", 6: "cancelled"}
        output({
            "success": False,
            "status": status,
            "status_text": status_map.get(status, f"unknown({status})"),
        })


# --- cancel subcommand ---

def cmd_cancel(args):
    """Manually cancel polling"""
    task_id = args.task_id

    meta = _load_task_meta(task_id)
    if not meta:
        output({"success": False, "error": f"Cron metadata for task {task_id} does not exist"})
        return

    job_id = meta.get("job_id", "")
    if job_id:
        _remove_cron_job(job_id)
        log(f"cancel: removed cron job {job_id}")

    _delete_task_meta(task_id)
    output({
        "success": True,
        "task_id": task_id,
        "job_id": job_id,
        "message": f"Cancelled cron polling for task {task_id}",
    })


# --- CLI entry ---

def main():
    parser = argparse.ArgumentParser(description="QQ Bot Cron async polling management")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_register = subparsers.add_parser("register", help="Register cron periodic check")
    p_register.add_argument("--task-id", required=True, help="Plume task ID")
    p_register.add_argument("--user-id", required=True, help="Delivery target, e.g. qqbot:c2c:XXXX")
    p_register.add_argument("--interval", default="5s", help="Check interval (e.g. 5s, 10s, 1m)")
    p_register.add_argument("--max-duration", default="120s", help="Maximum wait duration (e.g. 120s, 600s)")

    p_check = subparsers.add_parser("check", help="Single check task status (cron triggered)")
    p_check.add_argument("--task-id", required=True, help="Plume task ID")

    p_cancel = subparsers.add_parser("cancel", help="Manually cancel polling")
    p_cancel.add_argument("--task-id", required=True, help="Plume task ID")

    args = parser.parse_args()

    commands = {
        "register": cmd_register,
        "check": cmd_check,
        "cancel": cmd_cancel,
    }

    try:
        log(f"=== poll_cron_qqbot.py {args.command} called, argv={sys.argv[1:]} ===")
        commands[args.command](args)
    except Exception as e:
        output({"success": False, "error": str(e)})
        sys.exit(1)


if __name__ == "__main__":
    main()
