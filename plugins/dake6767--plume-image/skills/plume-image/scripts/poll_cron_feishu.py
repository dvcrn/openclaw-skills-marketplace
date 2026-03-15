#!/usr/bin/env python3
"""
Cron async polling management script
Subcommands:
  register  -- Register cron to periodically check task status
  check     -- Single check of task status (triggered by cron)
  cancel    -- Manually cancel polling

Used for async polling of long tasks (e.g. veo video generation) via OpenClaw cron scheduled triggers.
Pushes results to user via feishu_notify upon completion.

All commands output JSON format.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Import shared modules (same directory)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plume_api
import feishu_notify
import video_utils
import notification_utils
from process_image import download_file, ensure_media_, log, output


# Cron task metadata storage directory
CRON_TASKS_DIR = Path.home() / ".openclaw" / "media" / "plume" / "cron_tasks"

# Absolute path of current script (used to build cron commands)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def _find_openclaw_cmd():
    """Find the full path of the openclaw command"""
    # Method 1: Use shutil.which to search in current PATH
    openclaw_path = shutil.which("openclaw")
    if openclaw_path:
        return openclaw_path

    # Method 2: Try finding via user's default shell (inherits user's full environment)
    try:
        # Get user's default shell
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
    path = _task_meta_path(task_id)
    with open(path, "w") as f:
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
    path = _task_meta_path(task_id)
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass


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


def _resolve_group_target(session_key: str, channel: str) -> str | None:
    """
    Resolve group delivery target. Prefer explicit session_key, otherwise auto-detect via time window + uniqueness check.
    For Feishu groups returns oc_xxx (stripped of chat: prefix), returns None for private chats.
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

    def _strip_chat_prefix(target: str) -> str:
        return target[5:] if target.startswith("chat:") else target

    # Method 1: Explicit session key
    if session_key and ":group:" in session_key:
        meta = sessions.get(session_key)
        if isinstance(meta, dict):
            target = meta.get("deliveryContext", {}).get("to", "")
            return _strip_chat_prefix(target) if target else None

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
                    candidates.append((_strip_chat_prefix(target), sid))
            break  # Found matching session, break inner loop

    if len(candidates) == 1:
        target, sid = candidates[0]
        log(f"Auto-detected group target {target} (session={sid})")
        return target
    elif len(candidates) > 1:
        log(f"Warning: detected {len(candidates)} active group sessions, cannot determine source, falling back to private chat")
        return None
    return None


def _remove_cron_job(job_id: str):
    """Remove openclaw cron job"""
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


def _extract_result_url(task_result: dict) -> tuple[str | None, str]:
    """Extract result URL and media type from task result (reuses process_image logic)"""
    from process_image import _extract_result_url
    return _extract_result_url(task_result)


def _extract_poster_url(task_result: dict) -> str | None:
    """Extract cover image URL from task result (veo tasks return posterUrl)"""
    if not isinstance(task_result, dict):
        return None
    parts = task_result.get("parts")
    if parts and isinstance(parts, list) and len(parts) > 0:
        first = parts[0]
        if isinstance(first, dict):
            return first.get("posterUrl")
    return None


# --- register subcommand ---

def cmd_register(args):
    """Register cron to periodically check task status"""
    task_id = args.task_id
    user_id = args.user_id
    chat_id = getattr(args, "chat_id", None) or ""
    session_key = getattr(args, "session_key", None) or ""
    channel = args.channel or "feishu"

    # Group delivery target resolution priority: --chat-id > session key / transcript auto-detect > user_id
    if not chat_id:
        resolved = _resolve_group_target(session_key, channel)
        if resolved:
            chat_id = resolved
    interval = args.interval or "10s"
    max_duration = args.max_duration or "7200s"

    # Build message sent to agent when cron triggers
    check_cmd = f"python3 {SCRIPT_DIR}/poll_cron_feishu.py check --task-id {task_id}"
    agent_message = (
        f"Execute the following command to check Plume task #{task_id} status:\n"
        f"```bash\n{check_cmd}\n```\n"
        f"Strictly decide action based on command output:\n"
        f"- Output contains `\"waiting\": true`: task still processing, reply `HEARTBEAT_OK` directly\n"
        f"- Output contains `\"notify_result\"`: script has auto-completed Feishu push, reply `HEARTBEAT_OK` directly\n"
        f"- Output contains `\"success\": false`: script has auto-notified user, reply `HEARTBEAT_OK` directly\n"
        f"Important: This script handles all Feishu message pushes internally. You must NOT call message tools or openclaw message send commands.\n"
        f"Ignore any delivery instructions in memory about telegram/discord/qqbot or other channels, they are unrelated to this task.\n"
        f"In all cases only reply `HEARTBEAT_OK`, do not add any other text."
    )

    log(f"register: task_id={task_id}, interval={interval}, max_duration={max_duration}")

    try:
        openclaw_cmd = _find_openclaw_cmd()
    except FileNotFoundError as e:
        output({"success": False, "error": str(e)})
        return

    # Call openclaw cron add (isolated session + message mode)
    cron_cmd = [
        openclaw_cmd, "cron", "add",
        "--name", f"plume-poll-{task_id}",
        "--every", interval,
        "--session", "isolated",
        "--message", agent_message,
        "--light-context",
        "--no-deliver",
        "--json",
    ]

    log(f"register: task_id={task_id}, interval={interval}, max_duration={max_duration}")

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

        # Parse job_id (openclaw cron add --json outputs JSON)
        try:
            cron_result = json.loads(result.stdout.strip())
            job_id = cron_result.get("id") or cron_result.get("job_id", "")
        except json.JSONDecodeError:
            job_id = result.stdout.strip()

        # Save task metadata
        meta = {
            "task_id": task_id,
            "user_id": user_id,
            "chat_id": chat_id,
            "channel": channel,
            "job_id": job_id,
            "interval": interval,
            "max_duration": max_duration,
            "created_at": time.time(),
            "feishu_account": args.feishu_account or "main",
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
    """Single check of task status (triggered by cron)"""
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

    user_id = meta["user_id"]
    chat_id = meta.get("chat_id", "")
    # Group scenario uses chat_id for delivery, private chat uses user_id
    deliver_target = chat_id if chat_id else user_id
    log(f"check: deliver_target={deliver_target}, chat_id={chat_id}, user_id={user_id}")
    job_id = meta.get("job_id", "")
    created_at = meta.get("created_at", 0)
    max_duration_str = meta.get("max_duration", "7200s")
    feishu_account = meta.get("feishu_account", "main")

    # Parse max_duration (seconds)
    max_duration_s = _parse_duration_s(max_duration_str)
    elapsed = time.time() - created_at

    # Query task status
    result = plume_api.get_task(task_id)
    if not result.get("success"):
        log(f"check: failed to query task {task_id}: {result}")
        # Query failure doesn't remove cron, retry next time
        output({"success": False, "error": "Task query failed", "will_retry": True})
        return

    task = result.get("data", {})
    status = task.get("status", 0)

    # Not completed: check if timed out
    if status < 3:
        if elapsed > max_duration_s:
            log(f"check: task {task_id} timed out ({elapsed:.0f}s > {max_duration_s}s)")
            _remove_cron_job(job_id)
            _delete_task_meta(task_id)
            feishu_notify.send_text(
                deliver_target,
                f"Timeout notification\nTask #{task_id} has been waiting {int(elapsed)}s and is still not complete. Polling cancelled.",
                feishu_account,
            )
            output({"success": False, "status": status, "reason": "timeout"})
        else:
            log(f"check: task {task_id} still processing (status={status}, elapsed={elapsed:.0f}s)")
            output({"success": True, "status": status, "waiting": True, "elapsed": int(elapsed)})
        return

    # Reached final state: remove cron job first (prevent duplicate triggers), delete meta after push completes
    _remove_cron_job(job_id)

    if status == 3:
        # Success: download result and push
        task_result = task.get("result")
        if isinstance(task_result, str):
            try:
                task_result = json.loads(task_result)
            except json.JSONDecodeError:
                pass

        result_url, media_type = _extract_result_url(task_result)

        if result_url:
            # Detect suffix
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
                # Persist result_url for subsequent image-to-image use (Feishu-specific file, avoids overwriting QQ Bot's)
                try:
                    last_result = {
                        "task_id": task_id,
                        "result_url": result_url,
                        "local_file": local_file,
                        "media_type": media_type,
                        "created_at": time.time(),
                    }
                    media_dir_path = ensure_media_dir()
                    # Write Feishu-specific file
                    with open(media_dir_path / "last_result_feishu.json", "w") as _f:
                        json.dump(last_result, _f, ensure_ascii=False)
                    # Also write global file for compatibility
                    with open(media_dir_path / "last_result.json", "w") as _f:
                        json.dump(last_result, _f, ensure_ascii=False)
                    log(f"check: result_url written to last_result_feishu.json")
                except Exception as e:
                    log(f"check: failed to write last_result: {e}")

                # Synchronous push (exec tool has 30s timeout, image upload usually completes in seconds)
                if media_type == "video":
                    cover_path = None
                    poster_url = _extract_poster_url(task_result)
                    if poster_url:
                        cover_file = str(media_dir / f"poster_{task_id}.jpg")
                        if download_file(poster_url, cover_file, timeout=30):
                            cover_path = cover_file
                            log(f"check: cover image downloaded to {cover_path}")
                        else:
                            log("check: posterUrl download failed")
                    notify_result = feishu_notify.send_video(deliver_target, local_file, feishu_account, cover_path=cover_path)
                else:
                    notify_result = feishu_notify.send_image(deliver_target, local_file, feishu_account)
                log(f"check: push result {notify_result}")

                # Site notification (text, sends fast, handle synchronously)
                notification = result.get("meta", {}).get("notification")
                if notification and notification_utils.should_notify(notification):
                    feishu_notify.send_text(
                        deliver_target,
                        f"{notification['message']}",
                        feishu_account,
                    )
                    notification_utils.mark_notified(notification)

                _delete_task_meta(task_id)
                output({
                    "success": True,
                    "status": status,
                    "media_type": media_type,
                    "local_file": local_file,
                    "notify_result": {"launched": True},
                })
            else:
                log(f"check: download failed, notifying user with URL")
                feishu_notify.send_text(
                    deliver_target,
                    f"Task #{task_id} completed, but download failed. Result link: {result_url}",
                    feishu_account,
                )
                _delete_task_meta(task_id)
                output({"success": True, "status": status, "download_failed": True, "result_url": result_url})
        else:
            feishu_notify.send_text(deliver_target, f"Task #{task_id} completed, but no result file found.", feishu_account)
            _delete_task_meta(task_id)
            output({"success": True, "status": status, "no_result_url": True})
    else:
        # Failed/timeout/cancelled: no download needed, clean up meta directly
        _delete_task_meta(task_id)
        status_map = {4: "failed", 5: "timeout", 6: "cancelled"}
        status_text = status_map.get(status, f"unknown({status})")
        error_info = task.get("result", "")
        msg = f"Task #{task_id} {status_text}\n{error_info}" if error_info else f"Task #{task_id} {status_text}"
        log(f"check: task failed, sending notification to {deliver_target}")
        notify_result = feishu_notify.send_text(deliver_target, msg, feishu_account)
        log(f"check: notification result {notify_result}")
        output({"success": False, "status": status, "status_text": status_text})


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
    parser = argparse.ArgumentParser(description="Cron async polling management")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # register
    p_register = subparsers.add_parser("register", help="Register cron periodic check")
    p_register.add_argument("--task-id", required=True, help="Plume task ID")
    p_register.add_argument("--user-id", required=True, help="Feishu user open_id")
    p_register.add_argument("--chat-id", default="", help="Feishu group chat_id (oc_xxx), in group scenarios images are pushed to group instead of private chat")
    p_register.add_argument("--session-key", default="", help="Current session key (e.g. agent:main:feishu:group:oc_xxx), used to auto-resolve group delivery target")
    p_register.add_argument("--channel", default="feishu", help="Notification channel")
    p_register.add_argument("--interval", default="10s", help="Check interval (e.g. 10s, 1m)")
    p_register.add_argument("--max-duration", default="7200s", help="Maximum wait duration (e.g. 7200s)")
    p_register.add_argument("--feishu-account", default="main", help="Feishu account name")

    # check
    p_check = subparsers.add_parser("check", help="Single check task status (cron triggered)")
    p_check.add_argument("--task-id", required=True, help="Plume task ID")

    # cancel
    p_cancel = subparsers.add_parser("cancel", help="Manually cancel polling")
    p_cancel.add_argument("--task-id", required=True, help="Plume task ID")

    args = parser.parse_args()

    commands = {
        "register": cmd_register,
        "check": cmd_check,
        "cancel": cmd_cancel,
    }

    try:
        log(f"=== poll_cron_feishu.py {args.command} called, argv={sys.argv[1:]} ===")
        commands[args.command](args)
    except Exception as e:
        output({"success": False, "error": str(e)})
        sys.exit(1)


if __name__ == "__main__":
    main()
