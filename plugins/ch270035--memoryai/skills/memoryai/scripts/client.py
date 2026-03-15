#!/usr/bin/env python3
"""MemoryAI — Standalone client for OpenClaw skill.

No pip install required. Uses only urllib from stdlib.
Configure via config.json or environment variables HM_ENDPOINT / HM_API_KEY.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent
CONFIG_PATH = SCRIPT_DIR / "config.json"
VERSION = "1.0.0"


def load_config():
    endpoint = os.environ.get("HM_ENDPOINT", "")
    api_key = os.environ.get("HM_API_KEY", "")
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
        endpoint = endpoint or cfg.get("endpoint", "")
        api_key = api_key or cfg.get("api_key", "")
    if not endpoint:
        print("Error: No endpoint configured. Set HM_ENDPOINT or edit config.json", file=sys.stderr)
        sys.exit(1)
    if not api_key:
        print("Error: No API key configured. Set HM_API_KEY or edit config.json", file=sys.stderr)
        sys.exit(1)
    return endpoint.rstrip("/"), api_key


def api_call(method: str, path: str, body=None):
    endpoint, api_key = load_config()
    url = f"{endpoint}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"MemoryAI-Skill/{VERSION}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode() if e.fp else ""
        print(f"API error {e.code}: {body_text}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


# ── Core Commands ─────────────────────────────────────────

def cmd_store(args):
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
    body = {
        "content": args.content,
        "tags": tags,
        "priority": args.priority,
    }
    if args.source:
        body["source"] = args.source
    if args.content_type:
        body["content_type"] = args.content_type
    if args.memory_type:
        body["memory_type"] = args.memory_type
    if args.retention:
        body["retention"] = args.retention
    result = api_call("POST", "/v1/store", body)
    print(json.dumps(result, indent=2))


def cmd_recall(args):
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
    body = {
        "query": args.query,
        "depth": args.depth,
        "limit": args.limit,
        "min_score": args.min_score,
        "tags": tags,
    }
    result = api_call("POST", "/v1/recall", body)
    if not result.get("results"):
        print("No relevant memories found.")
        return
    for r in result["results"]:
        score_pct = int(r["score"] * 100)
        tags_str = f' (tags: {", ".join(r["tags"])})' if r.get("tags") else ""
        print(f"[{score_pct}%] {r['content']}{tags_str}\n")


def cmd_stats(args):
    result = api_call("GET", "/v1/stats")
    print(json.dumps(result, indent=2))


def cmd_compact(args):
    body = {"content": args.content}
    if args.task_context:
        body["task_context"] = args.task_context
    if args.content_type:
        body["content_type"] = args.content_type
    result = api_call("POST", "/v1/context/compact", body)
    print(json.dumps(result, indent=2))


def cmd_restore(args):
    body = {
        "task_description": args.task_description,
        "limit": args.limit,
    }
    result = api_call("POST", "/v1/context/restore", body)
    if not result.get("chunks"):
        print("No relevant context found.")
        return
    count = result.get("count", len(result["chunks"]))
    tokens = result.get("total_tokens_est", "?")
    print(f"Restored {count} chunks (~{tokens} tokens):\n")
    for c in result["chunks"]:
        score_pct = int(c.get("score", 0) * 100)
        content = c.get("content", "")
        preview = f"{content[:200]}..." if len(content) > 200 else content
        print(f"[{score_pct}%] {preview}\n")


def cmd_check(args):
    result = api_call("POST", "/v1/context/check", {})
    print(json.dumps(result, indent=2))


def cmd_reflect(args):
    body = {"hours_back": args.hours, "max_insights": args.max_insights}
    result = api_call("POST", "/v1/reflect", body)
    print(json.dumps(result, indent=2))


# ── Session Handoff Commands ──────────────────────────────

def cmd_handoff_start(args):
    """Start session handoff: send old session conversation to server."""
    if args.conversation:
        try:
            conversation = json.loads(args.conversation)
        except json.JSONDecodeError:
            conversation = [{"role": "user", "content": args.conversation}]
    else:
        raw = sys.stdin.read()
        try:
            conversation = json.loads(raw)
        except json.JSONDecodeError:
            conversation = [{"role": "user", "content": raw}]

    body = {"conversation": conversation}
    if args.metadata:
        try:
            body["metadata"] = json.loads(args.metadata)
        except json.JSONDecodeError:
            body["metadata"] = {"info": args.metadata}

    result = api_call("POST", "/v1/session/handoff/start", body)
    print(json.dumps(result, indent=2))


def cmd_handoff_restore(args):
    """Restore old session conversation + memories for new session."""
    body = {
        "include_memories": not args.no_memories,
        "memory_limit": args.memory_limit,
    }
    if args.handoff_id:
        body["handoff_id"] = args.handoff_id

    result = api_call("POST", "/v1/session/handoff/restore", body)

    if result.get("status") == "not_found":
        print("No pending handoff found.")
        return

    conv = result.get("conversation", [])
    mems = result.get("memories", [])
    print(f"Handoff {result.get('handoff_id')}: {len(conv)} turns, {len(mems)} memories\n")

    if conv:
        print("=== Old Session Conversation ===")
        for t in conv[-20:]:
            role = t.get("role", "?")
            content = t.get("content", "")[:300]
            print(f"[{role}] {content}")
        print()

    if mems:
        print("=== Related Memories ===")
        for m in mems:
            score = int(m.get("score", 0) * 100)
            print(f"[{score}%] {m.get('content', '')[:200]}")


def cmd_handoff_complete(args):
    """Complete handoff: archive old session into MemoryAI."""
    body = {"archive_to_memory": not args.no_archive}
    if args.handoff_id:
        body["handoff_id"] = args.handoff_id
    result = api_call("POST", "/v1/session/handoff/complete", body)
    print(json.dumps(result, indent=2))


def cmd_handoff_status(args):
    """Check handoff status."""
    result = api_call("GET", "/v1/session/handoff/status")
    print(json.dumps(result, indent=2))


# ── CLI Parser ────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="MemoryAI — Persistent memory for AI agents",
        epilog="https://memoryai.dev",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # store
    p = sub.add_parser("store", help="Store a memory")
    p.add_argument("-c", "--content", required=True)
    p.add_argument("-s", "--source", default=None)
    p.add_argument("-t", "--tags", default="", help="Comma-separated tags")
    p.add_argument("-p", "--priority", default="warm", choices=["hot", "warm", "cold"])
    p.add_argument("--content-type", default=None, choices=["conversation", "code"])
    p.add_argument("--memory-type", default=None,
                   choices=["fact", "decision", "preference", "error", "goal", "episodic"])
    p.add_argument("--retention", default=None,
                   choices=["forever", "6m", "1y", "auto"])
    p.set_defaults(func=cmd_store)

    # recall
    p = sub.add_parser("recall", help="Recall memories")
    p.add_argument("-q", "--query", required=True)
    p.add_argument("-d", "--depth", default="deep", choices=["fast", "deep", "exhaustive"])
    p.add_argument("-l", "--limit", type=int, default=5)
    p.add_argument("--min-score", type=float, default=0.0)
    p.add_argument("-t", "--tags", default="", help="Comma-separated tags")
    p.set_defaults(func=cmd_recall)

    # stats
    p = sub.add_parser("stats", help="Memory statistics")
    p.set_defaults(func=cmd_stats)

    # compact
    p = sub.add_parser("compact", help="Compact text into memory")
    p.add_argument("-c", "--content", required=True)
    p.add_argument("-t", "--task-context", default=None)
    p.add_argument("--content-type", default=None, choices=["conversation", "code"])
    p.set_defaults(func=cmd_compact)

    # restore
    p = sub.add_parser("restore", help="Restore context for a task")
    p.add_argument("-t", "--task-description", required=True)
    p.add_argument("-l", "--limit", type=int, default=5)
    p.set_defaults(func=cmd_restore)

    # check
    p = sub.add_parser("check", help="Check context token usage")
    p.set_defaults(func=cmd_check)

    # reflect
    p = sub.add_parser("reflect", help="Auto-reflection — find patterns")
    p.add_argument("--hours", type=int, default=24)
    p.add_argument("--max-insights", type=int, default=5)
    p.set_defaults(func=cmd_reflect)

    # handoff-start
    p = sub.add_parser("handoff-start", help="Start session handoff (send old conversation)")
    p.add_argument("-c", "--conversation", default=None,
                   help="JSON array of {role, content} turns. Reads stdin if omitted.")
    p.add_argument("-m", "--metadata", default=None, help="JSON metadata")
    p.set_defaults(func=cmd_handoff_start)

    # handoff-restore
    p = sub.add_parser("handoff-restore", help="Restore old session for new session")
    p.add_argument("--handoff-id", default=None)
    p.add_argument("--no-memories", action="store_true", help="Skip MemoryAI memories")
    p.add_argument("--memory-limit", type=int, default=5)
    p.set_defaults(func=cmd_handoff_restore)

    # handoff-complete
    p = sub.add_parser("handoff-complete", help="Complete handoff (archive old session)")
    p.add_argument("--handoff-id", default=None)
    p.add_argument("--no-archive", action="store_true")
    p.set_defaults(func=cmd_handoff_complete)

    # handoff-status
    p = sub.add_parser("handoff-status", help="Check handoff status")
    p.set_defaults(func=cmd_handoff_status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
