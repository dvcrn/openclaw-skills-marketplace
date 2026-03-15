#!/usr/bin/env python3
"""
Watcher: Monitors running Codex tasks and triggers callbacks on completion.
"""
import os
import sys
import json
import time
import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

def load_config():
    """Load codex-hook configuration"""
    config_path = Path.home() / ".config" / "codex-hook" / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {
        "result_dir": "/tmp/codex-results",
        "poll_interval": 5,
        "max_concurrent": 4,
        "heartbeat_integration": True,
        "pending_wake_file": "/tmp/codex-results/pending-wake.json",
        "latest_result_file": "/tmp/codex-results/latest.json"
    }

def load_task_meta(task_dir):
    """Load task metadata"""
    meta_file = task_dir / "task-meta.json"
    if meta_file.exists():
        with open(meta_file) as f:
            return json.load(f)
    return None

def save_task_meta(task_dir, task_meta):
    """Save task metadata"""
    meta_file = task_dir / "task-meta.json"
    with open(meta_file, 'w') as f:
        json.dump(task_meta, f, indent=2)

def is_process_running(pid):
    """Check if a process with given PID is still running"""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def read_output(task_dir):
    """Read task output from file"""
    output_file = task_dir / "output.txt"
    if output_file.exists():
        with open(output_file, 'r') as f:
            return f.read()
    return ""

def get_git_changes(workspace, limit=10):
    """Get recent git changes in workspace"""
    try:
        # Get recent commits
        result = subprocess.run(
            ["git", "-C", workspace, "log", f"--oneline", f"-n {limit}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
        else:
            commits = []
        
        # Get modified files in last commit
        result2 = subprocess.run(
            ["git", "-C", workspace, "diff", "--name-only", "HEAD~1..HEAD"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result2.returncode == 0:
            modified_files = result2.stdout.strip().split('\n') if result2.stdout.strip() else []
        else:
            modified_files = []
        
        return {
            "recent_commits": commits[:limit],
            "modified_files": modified_files[:20]
        }
    except Exception as e:
        return {"error": str(e)}

def truncate_output(output, max_chars=4000):
    """Truncate output if too long"""
    if len(output) <= max_chars:
        return output, False
    return output[-max_chars:], True

def write_pending_wake(task_meta, output, config):
    """Write to pending-wake.json for AGI heartbeat integration"""
    pending_wake_path = Path(config['pending_wake_file'])
    pending_wake_path.parent.mkdir(parents=True, exist_ok=True)

    summary = output[:500].replace('\n', ' ') if output else "No output"

    entry = {
        "task_id": task_meta['task_id'],
        "task_name": task_meta['task_name'],
        "status": task_meta['status'],
        "completed_at": datetime.utcnow().isoformat() + "Z",
        "summary": summary,
        "processed": False,
        "callback_channels": []
    }

    # Append entry as JSON line
    with open(pending_wake_path, 'a') as f:
        f.write(json.dumps(entry) + "\n")

def write_latest_result(task_meta, output, config, output_truncated=False):
    """Write latest result JSON"""
    latest_path = Path(config['latest_result_file'])
    latest_path.parent.mkdir(parents=True, exist_ok=True)

    result = {
        "task_id": task_meta['task_id'],
        "task_name": task_meta['task_name'],
        "status": task_meta['status'],
        "started_at": task_meta.get('started_at'),
        "completed_at": datetime.utcnow().isoformat() + "Z",
        "duration_seconds": None,
        "exit_code": task_meta.get('exit_code', 0),
        "output": output,
        "output_truncated": output_truncated,
        "session_key": task_meta.get('session_key'),
        "workspace": task_meta.get('workspace')
    }

    # Calculate duration
    if 'started_at' in task_meta:
        try:
            start = datetime.fromisoformat(task_meta['started_at'].rstrip('Z'))
            end = datetime.utcnow()
            result['duration_seconds'] = int((end - start).total_seconds())
        except:
            pass

    with open(latest_path, 'w') as f:
        json.dump(result, f, indent=2)

def format_duration(seconds):
    """Format duration in human readable form"""
    mins = seconds // 60
    secs = seconds % 60
    if mins > 0:
        return f"{mins}m {secs}s"
    return f"{secs}s"

def send_telegram_notification(task_meta, output, config):
    """Send enhanced notification to Telegram if configured"""
    try:
        default_group = config.get('default_group')
        print(f"[Telegram] Checking config: default_group={default_group}, task={task_meta.get('task_name')}")
        if not default_group:
            print(f"[Telegram] No default_group configured, skipping")
            return

        workspace = task_meta.get('workspace', 'N/A')
        duration_secs = task_meta.get('duration_seconds', 0)
        duration_str = format_duration(duration_secs) if duration_secs else "N/A"
        
        # Get git info if available
        git_info = ""
        if workspace and Path(workspace).exists():
            git_data = get_git_changes(workspace, limit=5)
            if git_data and not git_data.get('error'):
                if git_data['recent_commits']:
                    git_info += "\n📂 Recent commits:\n"
                    for commit in git_data['recent_commits'][:3]:
                        git_info += f"  • {commit}\n"
                if git_data['modified_files']:
                    git_info += "\n📝 Modified files:\n"
                    for f in git_data['modified_files'][:10]:
                        git_info += f"  • {f}\n"

        # Output summary
        output_summary = output[:800] if output else "No output"
        if len(output) > 800:
            output_summary += "\n... (truncated)"

        message = (
            f"🤖 *Codex Task Completed*\n"
            f"📋 Task: {task_meta['task_name']}\n"
            f"⏱️ Duration: {duration_str}\n"
            f"📊 Status: {task_meta['status']}\n"
            f"📁 Workspace: `{workspace}`\n"
            f"\n📝 Output Summary:\n"
            f"```\n{output_summary}\n```"
            f"{git_info}"
        )

        print(f"[Telegram] Sending to group {default_group}...")
        # Send via openclaw CLI
        result = subprocess.run([
            "openclaw", "message", "send",
            "--channel", "telegram",
            "--target", str(default_group),
            "--message", message
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"[Telegram] ✅ Sent successfully")
        else:
            print(f"[Telegram] ❌ Failed: {result.stderr}")
    except Exception as e:
        print(f"[Telegram] ❌ Exception: {e}", file=sys.stderr)

def process_task(task_dir, config):
    """Check and process a single task"""
    task_meta = load_task_meta(task_dir)
    if not task_meta:
        return None

    if task_meta['status'] not in ['starting', 'running']:
        return None

    # Check if process still running
    pid = task_meta.get('pid')
    if pid and not is_process_running(pid):
        # Process finished
        output = read_output(task_dir)

        # Determine exit status based on output content (simple heuristic)
        exit_code = 0 if output else 1
        status = "completed" if exit_code == 0 else "failed"

        task_meta['status'] = status
        task_meta['exit_code'] = exit_code
        task_meta['completed_at'] = datetime.utcnow().isoformat() + "Z"

        # Truncate output if needed
        output_max = config.get('output_max_chars', 4000)
        output_display, output_truncated = truncate_output(output, output_max)

        # Write updated meta
        save_task_meta(task_dir, task_meta)

        # Write latest result
        write_latest_result(task_meta, output, config, output_truncated)

        # Write pending wake
        write_pending_wake(task_meta, output, config)

        # Send notifications
        if status == "completed":
            send_telegram_notification(task_meta, output, config)

        print(f"✅ Task {task_meta['task_id']} finished with status {status}")
        return task_meta

    return None

def run_watcher(daemon=False, interval=5):
    """Main watcher loop"""
    config = load_config()
    result_dir = Path(config['result_dir'])
    tasks_dir = result_dir / "tasks"

    if daemon:
        print(f"[{datetime.utcnow().isoformat()}] 👀 Watcher daemon started (polling every {interval}s)")
        # Daemonize logic would go here; for now run in foreground loop
        while True:
            if tasks_dir.exists():
                for task_dir in tasks_dir.iterdir():
                    if task_dir.is_dir():
                        try:
                            result = process_task(task_dir, config)
                            if result:
                                print(f"[{datetime.utcnow().isoformat()}] ✅ Processed task {result['task_id']} -> {result['status']}")
                        except Exception as e:
                            print(f"[{datetime.utcnow().isoformat()}] ❌ Error processing {task_dir}: {e}", file=sys.stderr)
            time.sleep(interval)
    else:
        if not tasks_dir.exists():
            print("No tasks directory found")
            return
        print(f"[{datetime.utcnow().isoformat()}] 👀 Checking tasks...")
        processed_any = False
        for task_dir in tasks_dir.iterdir():
            if task_dir.is_dir():
                try:
                    result = process_task(task_dir, config)
                    if result:
                        print(f"[{datetime.utcnow().isoformat()}] ✅ Processed task {result['task_id']} -> {result['status']}")
                        processed_any = True
                except Exception as e:
                    print(f"[{datetime.utcnow().isoformat()}] ❌ Error processing {task_dir}: {e}", file=sys.stderr)
        if not processed_any:
            print(f"[{datetime.utcnow().isoformat()}] ℹ️  No tasks needed processing")

def main():
    parser = argparse.ArgumentParser(description="Watch Codex tasks for completion")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon (continuous polling)")
    parser.add_argument("--interval", type=int, default=5, help="Polling interval in seconds")
    parser.add_argument("--once", action="store_true", help="Run once and exit (default)")

    args = parser.parse_args()

    # If no --daemon, we default to --once behavior (single check)
    run_watcher(daemon=args.daemon, interval=args.interval)

if __name__ == "__main__":
    main()
