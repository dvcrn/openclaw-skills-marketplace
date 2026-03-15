#!/usr/bin/env python3
"""Show task changes since last sync."""
# SECURITY MANIFEST:
# Environment variables accessed: HOME (only)
# External endpoints called: none
# Local files read: .agent/tasks.md, ~/.openclaw/antigravity-bridge-state.json
# Local files written: ~/.openclaw/antigravity-bridge-state.json

import hashlib
import json
import os
import re
import sys
from pathlib import Path

CONFIG_PATH = os.path.expanduser("~/.openclaw/antigravity-bridge.json")
STATE_PATH = os.path.expanduser("~/.openclaw/antigravity-bridge-state.json")


def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        print(f"Error: Config not found at {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return json.load(f)


def load_state() -> dict:
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            return json.load(f)
    return {}


def save_state(state: dict):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def parse_tasks(content: str) -> dict[str, str]:
    """Parse tasks into {task_text: status} dict."""
    tasks = {}
    pattern = re.compile(r"- \[(.)\] \*\*(.+?)\*\*")
    for line in content.splitlines():
        m = pattern.search(line)
        if m:
            status, name = m.group(1), m.group(2)
            tasks[name] = status
    return tasks


def main():
    config = load_config()
    state = load_state()

    tasks_path = Path(os.path.expanduser(config["agent_dir"])) / "tasks.md"
    if not tasks_path.exists():
        print("No tasks.md found")
        sys.exit(1)

    content = tasks_path.read_text()
    current_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
    previous_hash = state.get("tasks_hash", "")

    if current_hash == previous_hash:
        print("📋 No changes since last sync.")
        return

    current_tasks = parse_tasks(content)
    previous_tasks = state.get("tasks_snapshot", {})

    # Find changes
    newly_done = []
    newly_active = []
    newly_added = []

    for name, status in current_tasks.items():
        prev_status = previous_tasks.get(name)
        if prev_status is None:
            newly_added.append(name)
        elif prev_status != "x" and status == "x":
            newly_done.append(name)
        elif prev_status != ">" and status == ">":
            newly_active.append(name)

    if newly_done:
        print("✅ Newly completed:")
        for t in newly_done:
            print(f"   - {t}")

    if newly_active:
        print("🔄 Newly active:")
        for t in newly_active:
            print(f"   - {t}")

    if newly_added:
        print("🆕 New tasks:")
        for t in newly_added:
            print(f"   - {t}")

    if not (newly_done or newly_active or newly_added):
        print("📝 Tasks changed but no status transitions detected.")

    # Update state
    state["tasks_hash"] = current_hash
    state["tasks_snapshot"] = current_tasks
    save_state(state)
    print(f"\n📌 State saved. {len(current_tasks)} tasks tracked.")


if __name__ == "__main__":
    main()
