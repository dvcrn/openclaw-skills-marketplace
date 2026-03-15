#!/usr/bin/env python3
"""Write directly to Antigravity's native Knowledge Item system."""
# SECURITY MANIFEST:
# Environment variables accessed: HOME (only)
# External endpoints called: none
# Local files read: ~/.openclaw/antigravity-bridge.json
# Local files written: ~/.gemini/antigravity/knowledge/<topic>/*

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
             artifact_name: str, content: str, references: list | None = None):
    """Write or update a Knowledge Item."""
    ki_dir = Path(os.path.expanduser(knowledge_dir)) / topic
    artifacts_dir = ki_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # metadata.json — merge with existing
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
                meta = {"title": title, "summary": summary, "references": references or []}
        if title:
            meta["title"] = title
        if summary and summary not in meta.get("summary", ""):
            meta["summary"] = summary
        if references:
            existing_refs = {json.dumps(r, sort_keys=True) for r in meta.get("references", [])}
            for ref in references:
                if json.dumps(ref, sort_keys=True) not in existing_refs:
                    meta.setdefault("references", []).append(ref)
    else:
        meta = {
            "title": title,
            "summary": summary,
            "references": references or []
        }

    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=4)

    # timestamps.json
    ts_path = ki_dir / "timestamps.json"
    if ts_path.exists():
        with open(ts_path) as f:
            ts = json.load(f)
        ts["updated"] = now
    else:
        ts = {"created": now, "updated": now}

    with open(ts_path, "w") as f:
        json.dump(ts, f, indent=4)

    # artifact
    artifact_path = artifacts_dir / f"{artifact_name}.md"
    with open(artifact_path, "w") as f:
        f.write(content)

    print(f"✅ KI written: knowledge/{topic}/artifacts/{artifact_name}.md")
    print(f"   Title: {meta['title']}")
    print(f"   Artifacts: {len(list(artifacts_dir.rglob('*.md')))}")


def main():
    parser = argparse.ArgumentParser(description="Write to Antigravity Knowledge Items")
    parser.add_argument("--topic", required=True, help="Topic directory name (snake_case)")
    parser.add_argument("--title", required=True, help="Human-readable title")
    parser.add_argument("--summary", required=True, help="KI summary (2-4 sentences)")
    parser.add_argument("--artifact", required=True, help="Artifact filename (without .md)")
    parser.add_argument("--content", help="Artifact content (reads stdin if omitted)")
    parser.add_argument("--ref-file", action="append", help="Add file reference")
    parser.add_argument("--ref-conversation", action="append", help="Add conversation ID reference")
    args = parser.parse_args()

    config = load_config()

    content = args.content
    if content is None:
        if not sys.stdin.isatty():
            content = sys.stdin.read()
        else:
            print("Error: provide --content or pipe content via stdin")
            sys.exit(1)

    references = []
    for ref in (args.ref_file or []):
        references.append({"type": "file", "value": ref})
    for ref in (args.ref_conversation or []):
        references.append({"type": "conversation_id", "value": ref})

    write_ki(
        config["knowledge_dir"],
        args.topic,
        args.title,
        args.summary,
        args.artifact,
        content,
        references,
    )


if __name__ == "__main__":
    main()
