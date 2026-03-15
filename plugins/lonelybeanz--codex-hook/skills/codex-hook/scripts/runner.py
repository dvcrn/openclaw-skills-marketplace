#!/usr/bin/env python3
"""
Runner: Spawns a Codex task using ACP sessions with proper concurrency isolation.
"""
import os
import sys
import json
import time
import uuid
import argparse
import subprocess
import requests
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
        "pending_wake_file": "/tmp/codex-results/pending-wake.json",
        "latest_result_file": "/tmp/codex-results/latest.json"
    }

def generate_task_id():
    """Generate unique task ID"""
    timestamp = int(time.time())
    return f"codex-{timestamp}-{uuid.uuid4().hex[:8]}"

def is_safe_path(path, base_dir=None):
    """Validate path is safe (no path traversal)"""
    try:
        path = Path(path).resolve()
        if base_dir:
            base_dir = Path(base_dir).resolve()
            try:
                path.relative_to(base_dir)
            except ValueError:
                return False
        if '..' in str(path):
            return False
        return True
    except Exception:
        return False

def ensure_result_dir(result_dir):
    """Ensure result directory exists with proper permissions"""
    # Validate path before creating
    if not is_safe_path(result_dir):
        raise ValueError(f"Invalid result directory path: {result_dir}")
    
    Path(result_dir).mkdir(parents=True, exist_ok=True)
    try:
        Path(result_dir).chmod(0o700)
    except:
        pass

def write_task_meta(task_dir, task_meta):
    """Write task metadata JSON"""
    meta_file = task_dir / "task-meta.json"
    with open(meta_file, 'w') as f:
        json.dump(task_meta, f, indent=2)

def spawn_acp_session(task):
    """
    Spawn task via OpenClaw agent command.
    Returns (session_key, run_id).
    """
    # Build command for openclaw agent
    cmd = [
        "openclaw", "agent",
        "--local",
        "--message", task['prompt'],
        "--timeout", str(task.get('timeout', 3600)),
        "--json"
    ]

    # Add agent if specified
    if task.get('agent_id'):
        cmd.extend(["--agent", task['agent_id']])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=task.get('timeout', 300)
        )
        if result.returncode != 0:
            raise RuntimeError(f"openclaw agent failed: {result.stderr}")

        # Parse JSON response
        try:
            resp = json.loads(result.stdout)
        except:
            resp = {"raw": result.stdout[:500]}

        session_key = f"agent-{task.get('agent_id', 'main')}-{task['task_id']}"
        run_id = task['task_id']

        return session_key, run_id, resp

    except subprocess.TimeoutExpired:
        raise RuntimeError("openclaw agent timeout after 30s")
    except Exception as e:
        raise RuntimeError(f"Failed to spawn agent: {e}")

def main():
    parser = argparse.ArgumentParser(description="Run Codex task with ACP")
    parser.add_argument("-t", "--task", required=True, help="Task prompt")
    parser.add_argument("-n", "--name", required=True, help="Task name")
    parser.add_argument("-w", "--workspace", default="~/projects", help="Workspace directory")
    parser.add_argument("--agent-id", default="codex", help="Agent ID from openclaw config")
    parser.add_argument("--model", help="Model override (e.g., openai-codex/gpt-5.2)")
    parser.add_argument("--timeout", type=int, default=3600, help="Total timeout in seconds")
    parser.add_argument("--operation-timeout", type=int, default=300, help="Per-operation timeout")
    parser.add_argument("--context-messages", type=int, default=10, help="Context window size")
    parser.add_argument("--result-dir", help="Override result directory")
    parser.add_argument("--priority", choices=["low", "normal", "high"], default="normal")

    args = parser.parse_args()

    # Load config
    config = load_config()
    result_dir = Path(args.result_dir or config['result_dir'])
    ensure_result_dir(result_dir)

    # Generate task ID and create task directory
    task_id = generate_task_id()
    task_dir = result_dir / "tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    # Build task metadata
    task_meta = {
        "task_id": task_id,
        "task_name": args.name,
        "prompt": args.task,
        "workspace": args.workspace,
        "agent_id": args.agent_id,
        "model": args.model,
        "timeout": args.timeout,
        "operation_timeout": args.operation_timeout,
        "context_messages": args.context_messages,
        "priority": args.priority,
        "status": "starting",
        "started_at": datetime.utcnow().isoformat() + "Z",
        "result_dir": str(task_dir)
    }

    # Write initial metadata
    write_task_meta(task_dir, task_meta)

    try:
        # Spawn ACP session
        print(f"🚀 Starting Codex task: {task_id}")
        print(f"   Task: {args.name}")
        print(f"   Workspace: {args.workspace}")

        session_key, run_id, resp = spawn_acp_session(task_meta)
        task_meta["session_key"] = session_key
        task_meta["run_id"] = run_id
        task_meta["status"] = "running"

        # Update metadata
        write_task_meta(task_dir, task_meta)

        print(f"✅ Task spawned successfully")
        print(f"   Session: {session_key}")
        print(f"   Run ID: {run_id}")
        print(f"   Task ID: {task_id}")
        print(f"   Monitor: codex-tasks status {task_id}")
        print("")
        print("The watcher will automatically detect completion and send callbacks.")

        # Return task_id (for dispatcher to capture)
        return task_id

    except Exception as e:
        task_meta["status"] = "failed"
        task_meta["error"] = str(e)
        task_meta["completed_at"] = datetime.utcnow().isoformat() + "Z"
        write_task_meta(task_dir, task_meta)
        print(f"❌ Failed to start task: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    result = main()
    if result:
        # Output task_id for dispatcher
        print(f"TASK_ID:{result}")
        sys.exit(0)
    else:
        sys.exit(1)
