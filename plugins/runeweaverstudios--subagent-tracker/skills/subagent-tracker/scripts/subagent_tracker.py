#!/usr/bin/env python3
"""
Subagent Tracker - Monitor OpenClaw agents and subagents.

Reads OPENCLAW_HOME/agents/main/sessions/sessions.json (default ~/.openclaw).
Always detects all sessions in that file; use --active N to filter by recent activity.
Session keys: agent:main:main (main), agent:main:subagent:* (subagents), agent:main:cron:* (cron).

Usage:
    python3 subagent_tracker.py list [--include-main] [--include-cron] [--active MINUTES] [--json] [--summary]
    python3 subagent_tracker.py status <session-id|key> [--json]
    python3 subagent_tracker.py tail <session-id> [--lines N]
"""

import argparse
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

# Default OpenClaw sessions path (allow override for exec/sandbox)
OPENCLAW_HOME = Path(os.environ.get("OPENCLAW_HOME", str(Path.home() / ".openclaw")))
SESSIONS_PATH = OPENCLAW_HOME / "agents" / "main" / "sessions"
SESSIONS_JSON = SESSIONS_PATH / "sessions.json"
RUNS_JSON = OPENCLAW_HOME / "agents" / "main" / "subagents" / "runs.json"
RUNS_JSON_LEGACY = OPENCLAW_HOME / "subagents" / "runs.json"

def load_sessions():
    """Load sessions.json and return list of session dicts with added 'key' field."""
    if not SESSIONS_JSON.exists():
        print(f"Error: Sessions file not found at {SESSIONS_JSON}", file=sys.stderr)
        sys.exit(1)
    with open(SESSIONS_JSON, "r") as f:
        data = json.load(f)
    # sessions.json is a dict mapping session key -> session object
    sessions = []
    for key, session in data.items():
        if key.startswith("agent:"):
            session["key"] = key
            sessions.append(session)
    return sessions

def _load_runs_from_path(path):
    """Load runs from one JSON file; return dict key -> {taskIndex, totalTasks, task}."""
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}
    runs = data if isinstance(data, list) else data.get("runs", [])
    run_list = list(runs.values()) if isinstance(runs, dict) else (runs if isinstance(runs, list) else [])
    by_key = {}
    for r in run_list:
        if not isinstance(r, dict):
            continue
        key = r.get("childSessionKey") or r.get("sessionKey")
        session_id = r.get("sessionId")
        if not key and session_id:
            key = f"agent:main:subagent:{session_id}"
        if not key:
            continue
        task_index = r.get("taskIndex")
        total_tasks = r.get("totalTasks")
        task = r.get("task", "")
        blob = {"taskIndex": int(task_index) if task_index is not None else None, "totalTasks": int(total_tasks) if total_tasks is not None else None, "task": task}
        by_key[key] = blob
        if session_id:
            by_key[f"agent:main:subagent:{session_id}"] = blob
    return by_key


def load_runs_by_key():
    """Load runs from RUNS_JSON and legacy subagents/runs.json; return merged dict."""
    by_key = {}
    for path in (RUNS_JSON, RUNS_JSON_LEGACY):
        by_key.update(_load_runs_from_path(path))
    return by_key

def is_subagent(session_key):
    """Return True if session key indicates a subagent."""
    return session_key.startswith("agent:main:subagent:")


def is_main(session_key):
    """Return True if session key is the main/orchestrator session."""
    return session_key == "agent:main:main"


def is_cron(session_key):
    """Return True if session key is a cron job session (may include :run: suffix)."""
    return session_key.startswith("agent:main:cron:")


def session_role(key):
    """Return 'main' | 'subagent' | 'cron' for session key; None for other agent keys."""
    if is_main(key):
        return "main"
    if is_subagent(key):
        return "subagent"
    if is_cron(key):
        return "cron"
    return None

def get_model_display(session):
    """Extract model display string from session."""
    model = session.get("modelOverride") or session.get("model")
    provider = session.get("providerOverride") or session.get("provider")
    if model and provider:
        return f"{provider}/{model}"
    elif model:
        return model
    else:
        return "unknown"

def get_transcript_path(session_id):
    """Return path to JSONL transcript for given session ID."""
    return SESSIONS_PATH / f"{session_id}.jsonl"

def read_transcript_lines(session_id, max_lines=None):
    """Read transcript lines, optionally limit."""
    path = get_transcript_path(session_id)
    if not path.exists():
        return []
    lines = []
    with open(path, "r") as f:
        for line in f:
            lines.append(line.strip())
            if max_lines and len(lines) >= max_lines:
                break
    return lines

def parse_transcript_event(line):
    """Parse a JSONL line into a dict, or None if invalid."""
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None

def session_age_ms(session):
    """Calculate age in milliseconds based on updatedAt."""
    updated_at = session.get("updatedAt")
    if not updated_at:
        return None
    # updatedAt is milliseconds since epoch
    now_ms = int(time.time() * 1000)
    age_ms = now_ms - updated_at
    return age_ms

def format_duration(ms):
    """Format milliseconds as human-readable duration."""
    if ms is None:
        return "unknown"
    seconds = ms / 1000
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = seconds / 60
    if minutes < 60:
        return f"{minutes:.1f}m"
    hours = minutes / 60
    return f"{hours:.1f}h"

# ASCII header for human-readable output (skip with --no-header or --json)
ASCII_HEADER = r"""
╔══════════════════════════════════════════════════════════╗
║  SUBAGENT TRACKER                                        ║
║  Monitoring • Coordinating • Dominating                  ║
╚══════════════════════════════════════════════════════════╝
""".strip()

def print_tracker_header(no_header=False):
    """Print the ASCII header unless no_header or output is not for humans."""
    if not no_header:
        print(ASCII_HEADER)
        print()

def _task_label(run_info):
    """Format Task X/Y from run_info if available."""
    if not run_info or run_info.get("taskIndex") is None or run_info.get("totalTasks") is None:
        return None
    return f"Task {run_info['taskIndex']}/{run_info['totalTasks']}"

def list_subagents(args):
    """List subagent sessions; optionally include main and cron sessions (always detect all)."""
    sessions = load_sessions()
    runs_by_key = load_runs_by_key()
    now_ms = int(time.time() * 1000)
    active_threshold_ms = args.active * 60 * 1000 if getattr(args, "active", None) else None
    include_main = getattr(args, "include_main", False)
    include_cron = getattr(args, "include_cron", False)

    result_list = []
    seen_session_ids = set()

    # Subagents (always included)
    for s in sessions:
        key = s.get("key", "")
        if not is_subagent(key):
            continue
        age_ms = session_age_ms(s)
        if active_threshold_ms is not None and age_ms is not None and age_ms > active_threshold_ms:
            continue
        run_info = runs_by_key.get(key, {})
        s["_run_info"] = run_info if isinstance(run_info, dict) else {}
        s["_role"] = "subagent"
        result_list.append(s)

    # Main session(s)
    if include_main:
        for s in sessions:
            key = s.get("key", "")
            if not is_main(key):
                continue
            age_ms = session_age_ms(s)
            if active_threshold_ms is not None and age_ms is not None and age_ms > active_threshold_ms:
                continue
            s["_run_info"] = {}
            s["_role"] = "main"
            result_list.append(s)
            break

    # Cron sessions (dedupe by sessionId: keep agent:main:cron:uuid, skip agent:main:cron:uuid:run:sessionId)
    if include_cron:
        cron_by_session_id = {}
        for s in sessions:
            key = s.get("key", "")
            if not is_cron(key):
                continue
            if ":run:" in key:
                continue
            sid = s.get("sessionId")
            if not sid:
                continue
            age_ms = session_age_ms(s)
            if active_threshold_ms is not None and age_ms is not None and age_ms > active_threshold_ms:
                continue
            cron_by_session_id[sid] = s
        for s in cron_by_session_id.values():
            s["_run_info"] = runs_by_key.get(s.get("key"), {}) or {}
            s["_role"] = "cron"
            result_list.append(s)

    subagents = result_list

    # One-line summary for chat (orchestrator can paste this)
    if getattr(args, "summary", False):
        print_tracker_header(getattr(args, "no_header", False))
        if not subagents:
            print("No subagents active right now.")
            return
        lines = []
        for i, s in enumerate(subagents, 1):
            model = get_model_display(s)
            age = format_duration(session_age_ms(s))
            run_info = s.get("_run_info", {})
            task_label = _task_label(run_info)
            if task_label:
                lines.append(f"Agent {i} ({task_label}): {model} ({age})")
            else:
                lines.append(f"Agent {i}: {model} ({age})")
        print("Here are your active subagents:")
        print()
        for line in lines:
            print(f" - {line}")
        return

    if args.json:
        output = []
        for i, s in enumerate(subagents, 1):
            run_info = s.get("_run_info", {})
            role = s.get("_role", "subagent")
            entry = {
                "agentIndex": i,
                "role": role,
                "key": s.get("key"),
                "sessionId": s.get("sessionId"),
                "updatedAt": s.get("updatedAt"),
                "ageMs": session_age_ms(s),
                "model": get_model_display(s),
                "modelOverride": s.get("modelOverride"),
                "providerOverride": s.get("providerOverride"),
                "spawnedBy": s.get("spawnedBy"),
                "inputTokens": s.get("inputTokens"),
                "outputTokens": s.get("outputTokens"),
                "channel": s.get("channel"),
            }
            if run_info.get("taskIndex") is not None and run_info.get("totalTasks") is not None:
                entry["taskIndex"] = run_info["taskIndex"]
                entry["totalTasks"] = run_info["totalTasks"]
            # Task: prefer runs.json, then session fields (gateway may use various keys)
            params = s.get("params") if isinstance(s.get("params"), dict) else {}
            entry["task"] = (
                run_info.get("task")
                or s.get("task")
                or s.get("spawnTask")
                or params.get("task")
                or s.get("initialTask")
                or (s.get("spawnParams") or {}).get("task") if isinstance(s.get("spawnParams"), dict) else None
                or ""
            ) or ""
            output.append(entry)
        print(json.dumps(output, indent=2))
        return

    print_tracker_header(getattr(args, "no_header", False))
    if not subagents:
        print("No sessions found" + (" (active within window)" if active_threshold_ms else ""))
        return

    print(f"Found {len(subagents)} session(s):")
    for i, s in enumerate(subagents, 1):
        key = s.get("key", "")
        session_id = s.get("sessionId", "unknown")
        age = format_duration(session_age_ms(s))
        model = get_model_display(s)
        tokens_in = s.get("inputTokens", 0) or 0
        tokens_out = s.get("outputTokens", 0) or 0
        spawned_by = s.get("spawnedBy", "")
        run_info = s.get("_run_info", {})
        task_label = _task_label(run_info)
        prefix = f"Agent {i} ({task_label}):" if task_label else f"Agent {i}:"
        print(f"  {prefix}  {session_id[:8]}...  age:{age:>6}  model:{model:>30}  tokens:{tokens_in}+{tokens_out}")
        print(f"    key: {key}")
        if spawned_by:
            print(f"    spawned by: {spawned_by}")

def status_subagent(args):
    """Show detailed status of a specific subagent."""
    target = args.session_id_or_key
    sessions = load_sessions()
    
    # Find session by sessionId or key
    session = None
    for s in sessions:
        if s.get("sessionId") == target or s.get("key") == target:
            session = s
            break
    
    if not session:
        print(f"Session not found: {target}", file=sys.stderr)
        sys.exit(1)
    
    session_id = session.get("sessionId")
    transcript_lines = read_transcript_lines(session_id, max_lines=100)
    
    # Parse events
    events = []
    for line in transcript_lines:
        event = parse_transcript_event(line)
        if event:
            events.append(event)
    
    # Count tool calls
    tool_calls = []
    for ev in events:
        if ev.get("type") == "message":
            msg = ev.get("message", {})
            content = msg.get("content", [])
            for c in content:
                if c.get("type") == "toolCall":
                    tool_calls.append(c.get("name"))
    
    # Last activity
    last_event = events[-1] if events else None
    
    if args.json:
        output = {
            "session": session,
            "toolCallCount": len(tool_calls),
            "toolCalls": tool_calls,
            "lastEventType": last_event.get("type") if last_event else None,
            "transcriptLineCount": len(transcript_lines),
        }
        print(json.dumps(output, indent=2))
        return
    
    print_tracker_header(getattr(args, "no_header", False))
    print(f"Session: {session.get('key')}")
    print(f"  ID: {session_id}")
    print(f"  Model: {get_model_display(session)}")
    print(f"  Spawned by: {session.get('spawnedBy', 'unknown')}")
    print(f"  Channel: {session.get('channel', 'unknown')}")
    print(f"  Updated: {format_duration(session_age_ms(s))} ago")
    print(f"  Input tokens: {session.get('inputTokens', 0) or 0}")
    print(f"  Output tokens: {session.get('outputTokens', 0) or 0}")
    print(f"  Transcript lines: {len(transcript_lines)}")
    print(f"  Tool calls: {len(tool_calls)}")
    if tool_calls:
        from collections import Counter
        counts = Counter(tool_calls)
        print("    " + ", ".join([f"{name}:{count}" for name, count in counts.items()]))
    if last_event:
        print(f"  Last event: {last_event.get('type')} at {last_event.get('timestamp')}")

def tail_subagent(args):
    """Tail transcript lines."""
    session_id = args.session_id
    lines = read_transcript_lines(session_id, max_lines=args.lines)
    if not lines:
        print(f"No transcript found for {session_id}", file=sys.stderr)
        return
    print_tracker_header(getattr(args, "no_header", False))
    for line in lines[-args.lines:]:
        event = parse_transcript_event(line)
        if not event:
            print(line)
            continue
        ev_type = event.get("type")
        timestamp = event.get("timestamp", "")
        # Simplify display
        if ev_type == "message":
            msg = event.get("message", {})
            role = msg.get("role")
            if role == "assistant":
                content = msg.get("content", [])
                tool_calls = [c for c in content if c.get("type") == "toolCall"]
                if tool_calls:
                    for tc in tool_calls:
                        print(f"{timestamp} {ev_type}:{role} toolCall {tc.get('name')}")
                else:
                    print(f"{timestamp} {ev_type}:{role} thinking")
            elif role == "toolResult":
                print(f"{timestamp} {ev_type}:{role} {msg.get('toolName')}")
            else:
                print(f"{timestamp} {ev_type}:{role}")
        else:
            print(f"{timestamp} {ev_type}")

def _normalize_task(task_str):
    """Normalize task string for duplicate comparison: strip and collapse whitespace."""
    if not task_str or not isinstance(task_str, str):
        return ""
    return " ".join(task_str.split())


def check_duplicate_task(args):
    """
    Check if the given task is already running as a subagent.
    Used by the orchestrator before calling sessions_spawn to avoid duplicate tasks.
    Returns JSON: {"duplicate": true|false, "reason": "running"|null, "sessionId": "...", "key": "..."}
    """
    task_str = args.task.strip() if args.task else ""
    if not task_str:
        out = {"duplicate": False, "error": "empty task"}
        print(json.dumps(out))
        return
    normalized = _normalize_task(task_str)
    sessions = load_sessions()
    runs_by_key = load_runs_by_key()
    session_keys = {s.get("key") for s in sessions if s.get("key")}
    for key, run_info in runs_by_key.items():
        run_task = run_info.get("task") or ""
        if _normalize_task(run_task) != normalized:
            continue
        if key in session_keys:
            session = next((s for s in sessions if s.get("key") == key), None)
            session_id = (session or {}).get("sessionId", "")
            out = {
                "duplicate": True,
                "reason": "running",
                "sessionId": session_id,
                "key": key,
            }
            if args.json:
                print(json.dumps(out))
            else:
                print(f"Duplicate task (already running): sessionId={session_id} key={key}")
            return
    out = {"duplicate": False}
    if args.json:
        print(json.dumps(out))
    else:
        print("No duplicate; safe to spawn.")


def check_stalled(args):
    """Check for stalled subagents."""
    sessions = load_sessions()
    stall_threshold_ms = args.stall_minutes * 60 * 1000
    now_ms = int(time.time() * 1000)
    
    stalled = []
    for s in sessions:
        if not is_subagent(s.get("key", "")):
            continue
        age_ms = session_age_ms(s)
        if age_ms and age_ms > stall_threshold_ms:
            stalled.append((s, age_ms))
    
    if args.json:
        output = []
        for s, age_ms in stalled:
            output.append({
                "key": s.get("key"),
                "sessionId": s.get("sessionId"),
                "updatedAt": s.get("updatedAt"),
                "ageMs": age_ms,
                "model": get_model_display(s),
                "spawnedBy": s.get("spawnedBy"),
            })
        print(json.dumps(output, indent=2))
        if stalled:
            sys.exit(1)
        else:
            sys.exit(0)
    
    print_tracker_header(getattr(args, "no_header", False))
    if not stalled:
        print("All subagents are active.")
        sys.exit(0)
    
    print(f"Found {len(stalled)} stalled subagent(s):")
    for s, age_ms in stalled:
        key = s.get("key", "")
        session_id = s.get("sessionId", "unknown")
        age = format_duration(age_ms)
        model = get_model_display(s)
        spawned_by = s.get("spawnedBy", "")
        print(f"  {session_id[:8]}...  age:{age:>6}  model:{model:>30}  spawned by:{spawned_by}")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Subagent Tracker")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # list command
    list_parser = subparsers.add_parser("list", help="List subagents; optionally include main and cron (always detects all in sessions.json)")
    list_parser.add_argument("--active", type=int, default=None, help="Only show sessions active within N minutes (default: no filter, show all)")
    list_parser.add_argument("--include-main", action="store_true", help="Include main/orchestrator session in output")
    list_parser.add_argument("--include-cron", action="store_true", help="Include cron job sessions in output")
    list_parser.add_argument("--json", action="store_true", help="JSON output")
    list_parser.add_argument("--summary", action="store_true", help="Chat-friendly block: 'Here are your active subagents' with Agent 1 (Task X/Y): model (age) per line")
    list_parser.add_argument("--no-header", action="store_true", help="Skip ASCII header (for piping/scripts)")
    
    # status command
    status_parser = subparsers.add_parser("status", help="Show subagent status")
    status_parser.add_argument("session_id_or_key", help="Session ID or key")
    status_parser.add_argument("--json", action="store_true", help="JSON output")
    status_parser.add_argument("--no-header", action="store_true", help="Skip ASCII header")
    
    # tail command
    tail_parser = subparsers.add_parser("tail", help="Tail transcript")
    tail_parser.add_argument("session_id", help="Session ID")
    tail_parser.add_argument("--lines", type=int, default=20, help="Number of lines to show")
    tail_parser.add_argument("--no-header", action="store_true", help="Skip ASCII header")
    
    # check command
    check_parser = subparsers.add_parser("check", help="Check for stalled subagents")
    check_parser.add_argument("--stall-minutes", type=int, default=30, help="Consider stalled if inactive for N minutes (default 30)")
    check_parser.add_argument("--json", action="store_true", help="JSON output")
    check_parser.add_argument("--no-header", action="store_true", help="Skip ASCII header")

    # check-duplicate command (before sessions_spawn to prevent duplicate subagent tasks)
    dup_parser = subparsers.add_parser("check-duplicate", help="Check if this task is already running; use before sessions_spawn")
    dup_parser.add_argument("task", nargs="?", default="", help="Task string (same as you would pass to sessions_spawn)")
    dup_parser.add_argument("--task", dest="task_opt", metavar="TASK", help="Task string (use when task contains leading dashes)")
    dup_parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_subagents(args)
    elif args.command == "status":
        status_subagent(args)
    elif args.command == "tail":
        tail_subagent(args)
    elif args.command == "check":
        check_stalled(args)
    elif args.command == "check-duplicate":
        args.task = (getattr(args, "task_opt", None) or "").strip() or (getattr(args, "task", None) or "")
        check_duplicate_task(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()