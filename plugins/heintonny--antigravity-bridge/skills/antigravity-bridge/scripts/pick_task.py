#!/usr/bin/env python3
"""Gather project context for next-task selection.

Mirrors Antigravity's /next-task workflow pattern:
1. Reads tasks, git log, memory, sessions, rules, skills
2. Outputs structured JSON context
3. Agent (LLM) reasons about which tasks to recommend
4. Agent presents 2-3 options to user
5. User picks → agent spawns sub-agent

This script does NOT modify tasks.md or pick a task.
That's the agent's job after user selection.
"""
# SECURITY MANIFEST:
# Environment variables accessed: HOME (only)
# External endpoints called: none
# Local files read: .agent/tasks.md, .agent/memory/*, .agent/sessions/*,
#   .agent/rules/*, .agent/skills/*, .gemini/GEMINI.md, git log
# Local files written: none

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from utils import load_config


def read_tasks(agent_dir: str) -> dict:
    """Read tasks.md and extract structured task data."""
    tasks_path = Path(os.path.expanduser(agent_dir)) / "tasks.md"
    if not tasks_path.exists():
        return {"exists": False}

    content = tasks_path.read_text()
    lines = content.splitlines()

    stats = {
        "done": content.count("[x]"),
        "todo": content.count("[ ]"),
        "active": content.count("[>]"),
        "skipped": content.count("[-]"),
    }

    # Extract active tasks
    active_tasks = []
    for i, line in enumerate(lines):
        if "[>]" in line:
            active_tasks.append({
                "line_num": i + 1,
                "text": line.strip().lstrip("- "),
            })

    # Extract phases/sections with their todo tasks
    phases = []
    current_phase = None
    for i, line in enumerate(lines):
        # Detect phase headers (## or ### with phase-like content)
        if re.match(r'^#{1,3}\s+', line) and not line.startswith('####'):
            current_phase = {
                "header": line.strip().lstrip("#").strip(),
                "line_num": i + 1,
                "todo_tasks": [],
                "done_count": 0,
                "todo_count": 0,
            }
            phases.append(current_phase)
        elif current_phase:
            if "[x]" in line:
                current_phase["done_count"] += 1
            elif "[ ]" in line:
                current_phase["todo_count"] += 1
                # Only include first-level tasks (not sub-tasks indented too deep)
                indent = len(line) - len(line.lstrip())
                if indent <= 4:  # Top-level or one indent
                    task_text = re.sub(r'^[\s\-]*\[\s*\]\s*', '', line).strip()
                    if task_text:
                        current_phase["todo_tasks"].append({
                            "line_num": i + 1,
                            "text": task_text,
                        })

    # Filter to phases with remaining work
    phases_with_work = [p for p in phases if p["todo_count"] > 0]

    return {
        "exists": True,
        "stats": stats,
        "active_tasks": active_tasks,
        "phases_with_work": phases_with_work[:10],  # Top 10 phases
    }


def read_git_log(project_dir: str, count: int = 15) -> list[str]:
    """Read recent git commits."""
    try:
        result = subprocess.run(
            ["git", "log", f"--oneline", f"-{count}", "--no-decorate"],
            cwd=os.path.expanduser(project_dir),
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip().splitlines()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return []


def read_session_handoffs(agent_dir: str) -> list[dict]:
    """Read session continuation prompts."""
    sessions_dir = Path(os.path.expanduser(agent_dir)) / "sessions"
    if not sessions_dir.exists():
        return []

    handoffs = []
    for f in sorted(sessions_dir.glob("*.md")):
        content = f.read_text()
        handoffs.append({
            "file": f.name,
            "preview": content[:800],
        })
    return handoffs


def read_recent_memory(agent_dir: str, max_files: int = 10) -> list[dict]:
    """Read recent lessons learned (names + first line)."""
    memory_dir = Path(os.path.expanduser(agent_dir)) / "memory"
    if not memory_dir.exists():
        return []

    files = sorted(memory_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    result = []
    for f in files[:max_files]:
        first_line = ""
        with open(f) as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#"):
                    first_line = line[:200]
                    break
        result.append({
            "file": f.name,
            "first_line": first_line,
        })
    return result


def list_directory(agent_dir: str, subdir: str) -> list[str]:
    """List files in an .agent/ subdirectory."""
    dir_path = Path(os.path.expanduser(agent_dir)) / subdir
    if not dir_path.exists():
        return []
    if subdir == "skills":
        # Return skill directory names
        return sorted([d.name for d in dir_path.iterdir() if d.is_dir() and not d.name.startswith(".")])
    return sorted([f.name for f in dir_path.glob("*.md")])


def main():
    config = load_config()
    project_dir = config["project_dir"]
    agent_dir = config["agent_dir"]

    context = {
        "gathered_at": datetime.now().isoformat(),
        "project_dir": project_dir,
        "tasks": read_tasks(agent_dir),
        "recent_commits": read_git_log(project_dir),
        "session_handoffs": read_session_handoffs(agent_dir),
        "recent_memory": read_recent_memory(agent_dir),
        "rules": list_directory(agent_dir, "rules"),
        "skills": list_directory(agent_dir, "skills"),
        "workflows": list_directory(agent_dir, "workflows"),
    }

    print(json.dumps(context, indent=2))


if __name__ == "__main__":
    main()
