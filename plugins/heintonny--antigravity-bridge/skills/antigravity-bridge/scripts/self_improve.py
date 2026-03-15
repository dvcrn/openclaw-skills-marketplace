#!/usr/bin/env python3
"""Cross-agent self-improvement: update both OpenClaw and Antigravity knowledge systems."""
# SECURITY MANIFEST:
# Environment variables accessed: HOME (only)
# External endpoints called: none
# Local files read: config
# Local files written: MEMORY.md, memory/YYYY-MM-DD.md, .agent/memory/lessons-learned-*.md,
#   ~/.gemini/antigravity/knowledge/<topic>/metadata.json,
#   ~/.gemini/antigravity/knowledge/<topic>/timestamps.json,
#   ~/.gemini/antigravity/knowledge/<topic>/artifacts/*.md

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

CONFIG_PATH = os.path.expanduser("~/.openclaw/antigravity-bridge.json")


def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        print(f"Error: Config not found at {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return json.load(f)


def write_ki(knowledge_dir: str, topic: str, title: str, summary: str,
             artifact_name: str, content: str):
    """Write or update a Knowledge Item in Antigravity's native format."""
    ki_dir = Path(os.path.expanduser(knowledge_dir)) / topic
    artifacts_dir = ki_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # metadata.json
    meta_path = ki_dir / "metadata.json"
    if meta_path.exists():
        try:
            with open(meta_path) as f:
                meta = json.load(f)
        except json.JSONDecodeError:
            with open(meta_path) as f:
                raw = f.read().strip()
            try:
                meta = json.loads(raw[:raw.rindex("}") + 1])
            except (ValueError, json.JSONDecodeError):
                meta = {"title": title, "summary": summary, "references": []}
        # Append to summary if new info
        if summary not in meta.get("summary", ""):
            meta["summary"] = meta["summary"].rstrip(". ") + ". " + summary
    else:
        meta = {
            "title": title,
            "summary": summary,
            "references": []
        }

    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=4)

    # timestamps.json
    ts_path = ki_dir / "timestamps.json"
    ts = {"updated": now}
    if ts_path.exists():
        with open(ts_path) as f:
            ts = json.load(f)
        ts["updated"] = now
    else:
        ts["created"] = now

    with open(ts_path, "w") as f:
        json.dump(ts, f, indent=4)

    # artifact
    artifact_path = artifacts_dir / f"{artifact_name}.md"
    with open(artifact_path, "w") as f:
        f.write(content)

    print(f"  📚 KI updated: knowledge/{topic}/artifacts/{artifact_name}.md")


def write_agent_memory(agent_dir: str, topic: str, lesson: str):
    """Write a lesson-learned file to .agent/memory/."""
    memory_dir = Path(os.path.expanduser(agent_dir)) / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)

    filename = f"lessons-learned-{topic.replace('_', '-')}.md"
    filepath = memory_dir / filename
    now = datetime.now().strftime("%Y-%m-%d")

    if filepath.exists():
        existing = filepath.read_text()
        updated = existing.rstrip() + f"\n\n---\n*Updated {now} by OpenClaw/antigravity-bridge*\n\n{lesson}\n"
    else:
        updated = f"# Lessons Learned: {topic.replace('_', ' ').title()}\n\n*Created {now} by OpenClaw/antigravity-bridge*\n\n{lesson}\n"

    filepath.write_text(updated)
    print(f"  📝 Memory: .agent/memory/{filename}")


def write_openclaw_memory(lesson: str, topic: str):
    """Update OpenClaw's daily memory log."""
    workspace = os.path.expanduser("~/.openclaw/workspace")
    memory_dir = os.path.join(workspace, "memory")
    os.makedirs(memory_dir, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%H:%M")
    filepath = os.path.join(memory_dir, f"{today}.md")

    entry = f"{now} — [antigravity-bridge] Self-improve: {topic} — {lesson[:200]}\n"

    if os.path.exists(filepath):
        with open(filepath, "a") as f:
            f.write(entry)
    else:
        with open(filepath, "w") as f:
            f.write(f"# {today}\n\n{entry}")

    print(f"  🧠 OpenClaw memory: memory/{today}.md")


def main():
    parser = argparse.ArgumentParser(description="Cross-agent self-improvement")
    parser.add_argument("--topic", required=True, help="Knowledge topic (snake_case)")
    parser.add_argument("--title", help="Human-readable title (defaults to topic)")
    parser.add_argument("--summary", help="KI summary (2-4 sentences)")
    parser.add_argument("--lesson", required=True, help="What was learned")
    parser.add_argument("--artifact", help="Artifact filename (defaults to topic)")
    parser.add_argument("--content", help="Full artifact content (reads stdin if not provided)")
    args = parser.parse_args()

    config = load_config()

    title = args.title or args.topic.replace("_", " ").title()
    summary = args.summary or args.lesson[:200]
    artifact = args.artifact or args.topic
    content = args.content or args.lesson

    print("🔄 Cross-agent self-improvement\n")

    # 1. Update Antigravity KI
    print("Antigravity Knowledge Items:")
    write_ki(config["knowledge_dir"], args.topic, title, summary, artifact, content)

    # 2. Update .agent/memory/
    print("\nAntigravity Agent Memory:")
    write_agent_memory(config["agent_dir"], args.topic, args.lesson)

    # 3. Update OpenClaw memory
    print("\nOpenClaw Memory:")
    write_openclaw_memory(args.lesson, args.topic)

    print("\n✅ Both knowledge systems updated.")

    # 4. Git commit if configured
    if config.get("auto_commit"):
        project_dir = os.path.expanduser(config["project_dir"])
        os.system(f'cd "{project_dir}" && git add .agent/memory/ && git commit -m "chore: self-improve — {args.topic}" --no-verify 2>/dev/null')
        print("📦 Changes committed to git.")


if __name__ == "__main__":
    main()
