#!/usr/bin/env python3
"""Sync Antigravity knowledge into OpenClaw context.

v1.2.0: Produces a structured state file + diff output.
The agent reads the diff and updates MEMORY.md / daily logs.

Outputs JSON to stdout with:
- current: full current state snapshot
- diff: what changed since last sync
- is_first_sync: true if no previous state exists
"""
# SECURITY MANIFEST:
# Environment variables accessed: HOME (only)
# External endpoints called: none
# Local files read: ~/.gemini/antigravity/knowledge/*, .agent/tasks.md,
#   .agent/memory/*, .agent/sessions/*, .agent/rules/*, .agent/skills/*,
#   .agent/workflows/*, .gemini/GEMINI.md, antigravity-sync-state.json
# Local files written: <workspace>/antigravity-sync-state.json

import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from utils import load_config, safe_load_json

STATE_PATH = os.path.expanduser("~/.openclaw/workspace/antigravity-sync-state.json")


def file_hash(path: str) -> str:
    """MD5 hash of file contents for change detection."""
    try:
        return hashlib.md5(Path(path).read_bytes()).hexdigest()
    except (OSError, IOError):
        return ""


def read_ki_topics(knowledge_dir: str) -> dict:
    """Read all Knowledge Item metadata into a structured dict."""
    ki_dir = Path(os.path.expanduser(knowledge_dir))
    if not ki_dir.exists():
        return {}

    topics = {}
    for topic_dir in sorted(ki_dir.iterdir()):
        if not topic_dir.is_dir() or topic_dir.name.startswith("."):
            continue
        meta_path = topic_dir / "metadata.json"
        if not meta_path.exists():
            continue

        meta = safe_load_json(str(meta_path))
        if not meta:
            continue

        # Count artifacts
        artifact_dir = topic_dir / "artifacts"
        artifacts = []
        if artifact_dir.exists():
            artifacts = [str(a.relative_to(artifact_dir)) for a in sorted(artifact_dir.rglob("*.md"))]

        # Get timestamps
        ts_path = topic_dir / "timestamps.json"
        updated = ""
        if ts_path.exists():
            ts = safe_load_json(str(ts_path))
            if ts:
                updated = ts.get("updated", "")

        topics[topic_dir.name] = {
            "title": meta.get("title", topic_dir.name),
            "summary": meta.get("summary", ""),
            "artifact_count": len(artifacts),
            "artifacts": artifacts,
            "updated": updated,
            "meta_hash": file_hash(str(meta_path)),
        }

    return topics


def read_tasks(agent_dir: str) -> dict:
    """Read tasks.md and extract stats + active tasks."""
    tasks_path = Path(os.path.expanduser(agent_dir)) / "tasks.md"
    if not tasks_path.exists():
        return {"exists": False}

    content = tasks_path.read_text()
    done = content.count("[x]")
    todo = content.count("[ ]")
    active = content.count("[>]")
    skipped = content.count("[-]")

    active_tasks = []
    for line in content.splitlines():
        if "[>]" in line:
            active_tasks.append(line.strip().lstrip("- "))

    return {
        "exists": True,
        "done": done,
        "todo": todo,
        "active": active,
        "skipped": skipped,
        "active_tasks": active_tasks,
        "file_hash": file_hash(str(tasks_path)),
    }


def read_directory_inventory(base_dir: str, subdir: str) -> dict:
    """Read a directory and return file names + hashes."""
    dir_path = Path(os.path.expanduser(base_dir)) / subdir
    if not dir_path.exists():
        return {}

    inventory = {}
    for f in sorted(dir_path.rglob("*.md")):
        rel = str(f.relative_to(dir_path))
        inventory[rel] = {
            "hash": file_hash(str(f)),
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            "size": f.stat().st_size,
        }
    return inventory


def read_memory_previews(agent_dir: str, max_files: int = 10) -> dict:
    """Read memory files with previews for new file detection."""
    memory_dir = Path(os.path.expanduser(agent_dir)) / "memory"
    if not memory_dir.exists():
        return {}

    files = sorted(memory_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    result = {}
    for f in files[:max_files]:
        content = f.read_text()
        result[f.name] = {
            "hash": file_hash(str(f)),
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            "preview": content[:300],
        }
    return result


def read_sessions(agent_dir: str) -> dict:
    """Read session handoff files."""
    sessions_dir = Path(os.path.expanduser(agent_dir)) / "sessions"
    if not sessions_dir.exists():
        return {}

    result = {}
    for f in sorted(sessions_dir.glob("*.md")):
        content = f.read_text()
        result[f.name] = {
            "hash": file_hash(str(f)),
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            "preview": content[:500],
        }
    return result


def load_previous_state() -> dict | None:
    """Load previous sync state."""
    if not os.path.exists(STATE_PATH):
        return None
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def compute_diff(previous: dict | None, current: dict) -> dict:
    """Compute what changed between previous and current state."""
    if previous is None:
        return {
            "is_first_sync": True,
            "summary": "First sync — all data is new.",
            "ki_topics": {"added": list(current["ki_topics"].keys()), "removed": [], "changed": []},
            "tasks": {"changed": True, "details": current["tasks"]},
            "memory": {"added": list(current["memory"].keys()), "removed": [], "changed": []},
            "rules": {"added": list(current["rules"].keys()), "removed": [], "changed": []},
            "skills": {"added": list(current["skills"].keys()), "removed": [], "changed": []},
            "workflows": {"added": list(current["workflows"].keys()), "removed": [], "changed": []},
            "sessions": {"added": list(current["sessions"].keys()), "removed": [], "changed": []},
        }

    diff = {"is_first_sync": False, "changes": []}

    # KI topics diff
    prev_ki = set(previous.get("ki_topics", {}).keys())
    curr_ki = set(current["ki_topics"].keys())
    ki_added = sorted(curr_ki - prev_ki)
    ki_removed = sorted(prev_ki - curr_ki)
    ki_changed = []
    for topic in sorted(curr_ki & prev_ki):
        prev_hash = previous["ki_topics"][topic].get("meta_hash", "")
        curr_hash = current["ki_topics"][topic].get("meta_hash", "")
        prev_count = previous["ki_topics"][topic].get("artifact_count", 0)
        curr_count = current["ki_topics"][topic].get("artifact_count", 0)
        if prev_hash != curr_hash or prev_count != curr_count:
            ki_changed.append({
                "topic": topic,
                "title": current["ki_topics"][topic]["title"],
                "artifacts_before": prev_count,
                "artifacts_after": curr_count,
            })
    diff["ki_topics"] = {"added": ki_added, "removed": ki_removed, "changed": ki_changed}
    if ki_added or ki_removed or ki_changed:
        diff["changes"].append(f"KI: +{len(ki_added)} added, -{len(ki_removed)} removed, ~{len(ki_changed)} changed")

    # Tasks diff
    prev_tasks = previous.get("tasks", {})
    curr_tasks = current["tasks"]
    tasks_changed = prev_tasks.get("file_hash") != curr_tasks.get("file_hash")
    task_details = {}
    if tasks_changed and prev_tasks.get("exists") and curr_tasks.get("exists"):
        task_details = {
            "done_delta": curr_tasks["done"] - prev_tasks.get("done", 0),
            "todo_delta": curr_tasks["todo"] - prev_tasks.get("todo", 0),
            "done_before": prev_tasks.get("done", 0),
            "done_after": curr_tasks["done"],
            "todo_before": prev_tasks.get("todo", 0),
            "todo_after": curr_tasks["todo"],
            "active_tasks": curr_tasks.get("active_tasks", []),
        }
        diff["changes"].append(
            f"Tasks: {task_details['done_delta']:+d} done, {task_details['todo_delta']:+d} todo "
            f"(now {curr_tasks['done']} done / {curr_tasks['todo']} todo)"
        )
    diff["tasks"] = {"changed": tasks_changed, "details": task_details}

    # Generic directory diffs
    for key in ["memory", "rules", "skills", "workflows", "sessions"]:
        prev_items = set(previous.get(key, {}).keys())
        curr_items = set(current[key].keys())
        added = sorted(curr_items - prev_items)
        removed = sorted(prev_items - curr_items)
        changed = []
        for item in sorted(curr_items & prev_items):
            prev_hash = previous[key][item].get("hash", "")
            curr_hash = current[key][item].get("hash", "")
            if prev_hash != curr_hash:
                changed.append(item)
        diff[key] = {"added": added, "removed": removed, "changed": changed}
        if added or removed or changed:
            diff["changes"].append(f"{key.capitalize()}: +{len(added)} added, -{len(removed)} removed, ~{len(changed)} changed")

    # Summary
    if diff["changes"]:
        diff["summary"] = " | ".join(diff["changes"])
    else:
        diff["summary"] = "No changes since last sync."

    return diff


def save_state(current: dict):
    """Save current state for future diffing."""
    state = {
        "synced_at": datetime.now().isoformat(),
        "ki_topics": current["ki_topics"],
        "tasks": current["tasks"],
        "memory": {k: {"hash": v["hash"]} for k, v in current["memory"].items()},
        "rules": {k: {"hash": v["hash"]} for k, v in current["rules"].items()},
        "skills": {k: {"hash": v["hash"]} for k, v in current["skills"].items()},
        "workflows": {k: {"hash": v["hash"]} for k, v in current["workflows"].items()},
        "sessions": {k: {"hash": v["hash"]} for k, v in current["sessions"].items()},
    }
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def main():
    config = load_config()

    # Gather current state
    current = {
        "ki_topics": read_ki_topics(config["knowledge_dir"]),
        "tasks": read_tasks(config["agent_dir"]),
        "memory": read_memory_previews(config["agent_dir"]),
        "rules": read_directory_inventory(config["agent_dir"], "rules"),
        "skills": read_directory_inventory(config["agent_dir"], "skills"),
        "workflows": read_directory_inventory(config["agent_dir"], "workflows"),
        "sessions": read_sessions(config["agent_dir"]),
    }

    # Load previous state and compute diff
    previous = load_previous_state()
    diff = compute_diff(previous, current)

    # Save new state
    save_state(current)

    # Output structured result to stdout
    output = {
        "synced_at": datetime.now().isoformat(),
        "diff": diff,
        "current": {
            "ki_topic_count": len(current["ki_topics"]),
            "ki_topics": {k: {"title": v["title"], "summary": v["summary"], "artifact_count": v["artifact_count"]}
                          for k, v in current["ki_topics"].items()},
            "tasks": current["tasks"],
            "memory_count": len(current["memory"]),
            "memory_files": list(current["memory"].keys()),
            "rules_count": len(current["rules"]),
            "rules_files": list(current["rules"].keys()),
            "skills_count": len(current["skills"]),
            "skills_dirs": list(set(f.split("/")[0] for f in current["skills"].keys())),
            "workflows_count": len(current["workflows"]),
            "workflows_files": list(current["workflows"].keys()),
            "sessions": {k: {"preview": v["preview"]} for k, v in current["sessions"].items()},
        },
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
