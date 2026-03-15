#!/usr/bin/env python3
"""
Callback handler for Codex task completions.
"""
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

def load_config():
    """Load codex-hook configuration"""
    config_path = Path.home() / ".config" / "codex-hook" / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {
        "result_dir": "/tmp/codex-results",
        "pending_wake_file": "/tmp/codex-results/pending-wake.json"
    }

def write_pending_wake(task_meta, output, config):
    """Write entry to pending-wake.json"""
    pending_wake_path = Path(config['pending_wake_file'])
    pending_wake_path.parent.mkdir(parents=True, exist_ok=True)

    summary = output[:500].replace('\n', ' ') if output else "No output"

    entry = {
        "task_id": task_meta['task_id'],
        "task_name": task_meta['task_name'],
        "status": task_meta['status'],
        "completed_at": task_meta.get('completed_at', datetime.utcnow().isoformat() + "Z"),
        "summary": summary,
        "session_key": task_meta.get('session_key', ''),
        "processed": False,
        "callback_channels": task_meta.get('callback_channels', [])
    }

    with open(pending_wake_path, 'a') as f:
        f.write(json.dumps(entry) + '\n')

def write_latest_result(task_meta, output, config):
    """Write latest result JSON"""
    latest_path = Path(config.get('latest_result_file', '/tmp/codex-results/latest.json'))
    latest_path.parent.mkdir(parents=True, exist_ok=True)

    output_truncated = len(output) > 4000
    output_save = output[-4000:] if output_truncated else output

    result = {
        "task_id": task_meta['task_id'],
        "task_name": task_meta['task_name'],
        "status": task_meta['status'],
        "started_at": task_meta['started_at'],
        "completed_at": task_meta.get('completed_at', datetime.utcnow().isoformat() + "Z"),
        "duration_seconds": task_meta.get('duration_seconds'),
        "exit_code": task_meta.get('exit_code'),
        "output": output_save,
        "output_truncated": output_truncated,
        "session_key": task_meta.get('session_key', ''),
        "workspace": task_meta['workspace']
    }

    with open(latest_path, 'w') as f:
        json.dump(result, f, indent=2)

def send_telegram_notification(task_meta, output, config):
    """Send Telegram notification"""
    channel = task_meta.get('callback_channel') or config.get('default_channel')
    group_id = task_meta.get('callback_group') or config.get('default_group')

    if channel != 'telegram' or not group_id:
        return False

    try:
        import subprocess

        start = datetime.fromisoformat(task_meta['started_at'].replace('Z', '+00:00'))
        completed = datetime.fromisoformat(task_meta.get('completed_at', datetime.utcnow().isoformat() + "Z").replace('Z', '+00:00'))
        duration = completed - start.replace(tzinfo=None)
        duration_str = f"{duration.seconds // 60}m {duration.seconds % 60}s"

        summary = output[:800] if output else "No output"
        status_emoji = "✅" if task_meta['status'] == 'completed' else "❌"

        message = f"""{status_emoji} *Codex Task Completed*
📋 Task: {task_meta['task_name']}
⏱️ Duration: {duration_str}
📊 Status: {task_meta['status']}

📝 Output Summary:
```
{summary}
```"""

        subprocess.run([
            "openclaw", "message", "send",
            "--channel", "telegram",
            "--target", group_id,
            "--message", message
        ], capture_output=True, timeout=30)

        return True
    except Exception as e:
        print(f"Failed to send Telegram: {e}", file=sys.stderr)
        return False

def send_webhook_notification(task_meta, output, webhook_url):
    """Send webhook notification"""
    if not webhook_url:
        return False

    try:
        import requests

        output_truncated = len(output) > 4000
        output_save = output[-4000:] if output_truncated else output

        payload = {
            "task_id": task_meta['task_id'],
            "task_name": task_meta['task_name'],
            "status": task_meta['status'],
            "completed_at": task_meta.get('completed_at', datetime.utcnow().isoformat() + "Z"),
            "duration_seconds": task_meta.get('duration_seconds'),
            "exit_code": task_meta.get('exit_code'),
            "output": output_save,
            "output_truncated": output_truncated,
            "session_key": task_meta.get('session_key', ''),
            "workspace": task_meta['workspace']
        }

        response = requests.post(webhook_url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send webhook: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Handle Codex task callback")
    parser.add_argument("--task-dir", required=True, help="Task directory with task-meta.json")
    parser.add_argument("--output", required=True, help="Task output text")
    parser.add_argument("--webhook-url", help="Webhook URL (overrides config)")

    args = parser.parse_args()

    task_dir = Path(args.task_dir)
    output = args.output

    config = load_config()

    # Load task metadata
    meta_file = task_dir / "task-meta.json"
    if not meta_file.exists():
        print(f"Task meta not found: {meta_file}")
        return 1

    with open(meta_file) as f:
        task_meta = json.load(f)

    # Write results
    write_latest_result(task_meta, output, config)
    write_pending_wake(task_meta, output, config)

    # Send callbacks
    callbacks_sent = []

    if send_telegram_notification(task_meta, output, config):
        callbacks_sent.append('telegram')

    webhook = args.webhook_url or task_meta.get('webhook_url') or config.get('default_webhook_url')
    if webhook and send_webhook_notification(task_meta, output, webhook):
        callbacks_sent.append('webhook')

    task_meta['callbacks_sent'] = callbacks_sent

    print(f"✅ Callback processed for {task_meta['task_id']}")
    print(f"   Callbacks: {', '.join(callbacks_sent) if callbacks_sent else 'none'}")

    # Save updated metadata
    task_meta['status'] = 'completed' if task_meta.get('exit_code', 0) == 0 else 'failed'
    task_meta['completed_at'] = datetime.utcnow().isoformat() + "Z"
    save_task_meta(task_dir, task_meta)

    return 0

def save_task_meta(task_dir, task_meta):
    """Save task metadata"""
    meta_file = task_dir / "task-meta.json"
    with open(meta_file, 'w') as f:
        json.dump(task_meta, f, indent=2)

if __name__ == "__main__":
    sys.exit(main())
