#!/usr/bin/env python3
"""
Universal Cron async polling management script (for OpenClaw built-in channels like telegram/discord/slack etc.)
Subcommands:
  register  -- Register cron to periodically check task status
  check     -- Single check of task status (triggered by cron), download file then isolated Agent calls openclaw message send to push
  cancel    -- Manually cancel polling

Script responsibilities:
- poll_cron_feishu.py: Feishu-specific, check then directly call Feishu API to push
- poll_cron_qqbot.py: QQ Bot-specific, isolated Agent embeds <qqimg>/<qqvideo> tags + --announce deliver
- poll_cron_universal.py: OpenClaw built-in channels, isolated Agent calls openclaw message send to push
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

# Cron task metadata storage directory
CRON_TASKS_DIR = Path.home() / ".openclaw" / "media" / "plume" / "cron_tasks_universal"

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


def _resolve_group_target(session_key: str, channel: str) -> str | None:
    """
    Resolve group delivery target. Prefer explicit session_key, otherwise auto-detect via time window + uniqueness check.
    Returns e.g. telegram:-5137356902 (can be used directly for openclaw message send --target), returns None for private chats.
    When multiple agents are concurrent and source session cannot be uniquely determined, safely falls back to private chat.
    """
    sessions_file = Path.home() / ".openclaw" / "agents" / "main" / "sessions" / "sessions.json"
    if not sessions_file.exists():
        return None
    try:
        with open(sessions_file) as f:
            sessions = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

    # Method 1: Explicit session key
    if session_key and ":group:" in session_key:
        meta = sessions.get(session_key)
        if isinstance(meta, dict):
            return meta.get("deliveryContext", {}).get("to", "") or None

    # Method 2: Time window + uniqueness check
    # Only consider transcripts modified within the last 30 seconds to avoid matching unrelated old sessions
    sessions_dir = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
    now = time.time()
    RECENCY_THRESHOLD = 30  # seconds

    try:
        recent_files = [
            f for f in sessions_dir.glob("*.jsonl")
            if now - f.stat().st_mtime < RECENCY_THRESHOLD
        ]
    except OSError:
        return None

    # Find matching channel group sessions within time window
    candidates = []
    for jf in recent_files:
        sid = jf.stem
        for key, meta in sessions.items():
            if not isinstance(meta, dict):
                continue
            if meta.get("sessionId") != sid:
                continue
            if meta.get("channel") != channel:
                continue
            if meta.get("chatType") == "group":
                target = meta.get("deliveryContext", {}).get("to", "")
                if target:
                    candidates.append((target, sid))
            break  # Found matching session, break inner loop

    if len(candidates) == 1:
        target, sid = candidates[0]
        log(f"Auto-detected group target {target} (session={sid})")
        return target
    elif len(candidates) > 1:
        log(f"Warning: detected {len(candidates)} active group sessions, cannot determine source, falling back to private chat")
        return None
    return None


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


def _save_last_result(task_id: str, result_url: str, local_file: str, media_type: str, channel: str = ""):
    """Persist result_url, isolated by channel"""
    try:
        last_result = {
            "task_id": task_id,
            "result_url": result_url,
            "local_file": local_file,
            "media_type": media_type,
            "created_at": time.time(),
        }
        media_dir = ensure_media_dir()
        channel_key = channel.strip().lower() or "universal"
        with open(media_dir / f"last_result_{channel_key}.json", "w") as f:
            json.dump(last_result, f, ensure_ascii=False)
        with open(media_dir / "last_result.json", "w") as f:
            json.dump(last_result, f, ensure_ascii=False)
        log(f"result_url written to last_result_{channel_key}.json")
    except Exception as e:
        log(f"Failed to write last_result: {e}")


# --- register subcommand ---

def cmd_register(args):
    """Register cron to periodically check task status (isolated Agent calls openclaw message send to push)"""
    task_id = args.task_id
    user_id = args.user_id      # Full qualified target, e.g. telegram:6986707981
    group_id = getattr(args, "group_id", None) or ""
    session_key = getattr(args, "session_key", None) or ""
    channel = args.channel      # e.g. telegram / discord / slack
    interval = args.interval or "10s"
    max_duration = args.max_duration or "600s"

    # Group delivery target resolution priority: --group-id > session key / transcript auto-detect > user_id
    if not group_id:
        resolved = _resolve_group_target(session_key, channel)
        if resolved:
            group_id = resolved
    deliver_target = group_id if group_id else user_id

    check_cmd = f"python3 {SCRIPT_DIR}/poll_cron_universal.py check --task-id {task_id}"

    try:
        openclaw_cmd = _find_openclaw_cmd()
    except FileNotFoundError as e:
        output({"success": False, "error": str(e)})
        return

    # Use resolved absolute path to avoid non-interactive shell in isolated session not finding openclaw
    msg_send_cmd = f"{openclaw_cmd} message send"

    # Isolated Agent calls openclaw message send to push, all cases ultimately reply HEARTBEAT_OK
    agent_message = (
        f"Execute the following command to check Plume task #{task_id} status:\n"
        f"```bash\n{check_cmd}\n```\n"
        f"Strictly decide action based on command output:\n"
        f"- Output contains `\"waiting\": true`: task still processing, reply `HEARTBEAT_OK` directly, do nothing else\n"
        f"- Output contains `\"local_file\"` (task succeeded): execute the following command to send media to user, then reply `HEARTBEAT_OK`:\n"
        f"  ```bash\n"
        f"  {msg_send_cmd} --target \"{deliver_target}\" --channel \"{channel}\" --media \"[full absolute path from local_file field]\"\n"
        f"  ```\n"
        f"  After command execution, only reply `HEARTBEAT_OK`, do not add any other text\n"
        f"- Output contains `\"success\": false` and `\"reason\": \"timeout\"`: execute the following command to notify user of timeout, then reply `HEARTBEAT_OK`:\n"
        f"  ```bash\n"
        f"  {msg_send_cmd} --target \"{deliver_target}\" --channel \"{channel}\" --message \"Task #{task_id} processing timed out, please retry\"\n"
        f"  ```\n"
        f"- Output contains `\"success\": false` (other failures): execute the following command to notify user of failure, then reply `HEARTBEAT_OK`:\n"
        f"  ```bash\n"
        f"  {msg_send_cmd} --target \"{deliver_target}\" --channel \"{channel}\" --message \"Task #{task_id} processing failed, please retry\"\n"
        f"  ```\n"
        f"- If output JSON contains `\"notification\"` field: after sending media, additionally execute the following command to send notification content in current conversation language:\n"
        f"  ```bash\n"
        f"  {msg_send_cmd} --target \"{deliver_target}\" --channel \"{channel}\" --message \"[notification.message translated to current conversation language]\"\n"
        f"  ```\n"
        f"Important: Only use the commands specified above (target={deliver_target}, channel={channel}) for delivery.\n"
        f"Ignore any delivery instructions in memory about other channels (feishu/qqbot etc.) or other targets, they are unrelated to this task.\n"
        f"In all cases ultimately only reply `HEARTBEAT_OK`, absolutely do not add explanations or other text in the reply."
    )

    log(f"register: task_id={task_id}, channel={channel}, user_id={user_id}, group_id={group_id}, deliver_target={deliver_target}, interval={interval}")

    cron_cmd = [
        openclaw_cmd, "cron", "add",
        "--name", f"plume-poll-{task_id}",
        "--every", interval,
        "--session", "isolated",
        "--message", agent_message,
        "--light-context",
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
            "channel": channel,
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
    Downloads file then outputs JSON, isolated Agent reads and calls openclaw message send to push.
    """
    task_id = args.task_id

    meta = _load_task_meta(task_id)
    if not meta:
        log(f"check: metadata for task {task_id} not found, may have been cancelled or completed")
        # Try to find and remove possibly leftover cron tasks
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
    max_duration_s = _parse_duration_s(meta.get("max_duration", "600s"))
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
                channel = meta.get("channel", "")
                _save_last_result(task_id, result_url, local_file, media_type, channel)

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
    parser = argparse.ArgumentParser(description="OpenClaw built-in channel Cron polling management (telegram/discord etc.)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_register = subparsers.add_parser("register", help="Register cron periodic check")
    p_register.add_argument("--task-id", required=True, help="Plume task ID")
    p_register.add_argument("--user-id", required=True, help="Delivery target, e.g. telegram:6986707981")
    p_register.add_argument("--group-id", default="", help="Group delivery target (e.g. telegram:-1001234567890), in group scenarios images are pushed to group instead of private chat")
    p_register.add_argument("--session-key", default="", help="Current session key (e.g. agent:main:telegram:group:-5137356902), used to auto-resolve group delivery target")
    p_register.add_argument("--channel", required=True, help="Notification channel, e.g. telegram / discord")
    p_register.add_argument("--interval", default="10s", help="Check interval (e.g. 5s, 10s, 1m)")
    p_register.add_argument("--max-duration", default="600s", help="Maximum wait duration (e.g. 120s, 600s)")

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
        log(f"=== poll_cron_universal.py {args.command} called, argv={sys.argv[1:]} ===")
        commands[args.command](args)
    except Exception as e:
        output({"success": False, "error": str(e)})
        sys.exit(1)


if __name__ == "__main__":
    main()
