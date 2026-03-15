#!/usr/bin/env python3
"""Context Guard v4.0 — Lightweight context check via OpenClaw sessions.json.
No LLM call, no API call required. Reads token usage directly from OpenClaw data.
Saves old session ID to WAL for handoff to new session.

Usage:
    python context_check.py
    python context_check.py --session "agent:main:main"
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Context budget
DEFAULT_CONTEXT_TOKENS = 200000

# Thresholds — v3.3
THRESHOLD_COMPACT = 0.45  # 45% → compact backup
THRESHOLD_SWITCH = 0.60   # 60% → session switch

# Paths — auto-detect OpenClaw directory (works on Windows, Linux, Mac)
OPENCLAW_DIR = Path(os.environ.get("OPENCLAW_DIR", str(Path.home() / ".openclaw")))
WORKSPACE = Path(os.environ.get("WORKSPACE", str(OPENCLAW_DIR / "workspace")))
SESSIONS_JSON = OPENCLAW_DIR / "agents" / "main" / "sessions" / "sessions.json"
WAL_PATH = WORKSPACE / "memory" / "wal.json"
WARMUP_TOKENS = 25000

TZ_VN = timezone(timedelta(hours=7))


def get_session_info(session_key: str = "agent:main:main") -> dict | None:
    """Get real token usage + session ID from OpenClaw sessions.json file."""
    # Primary: read sessions.json directly (always available)
    try:
        with open(SESSIONS_JSON, encoding="utf-8") as f:
            sessions = json.load(f)
        if session_key in sessions:
            s = sessions[session_key]
            return {
                "key": session_key,
                "sessionId": s.get("sessionId", ""),
                "sessionFile": s.get("sessionFile", ""),
                "totalTokens": s.get("totalTokens", 0),
                "contextTokens": s.get("contextTokens", DEFAULT_CONTEXT_TOKENS),
                "inputTokens": s.get("inputTokens", 0),
                "outputTokens": s.get("outputTokens", 0),
            }
    except Exception:
        pass

    return None


def load_wal() -> dict:
    """Load WAL from disk."""
    if WAL_PATH.exists():
        try:
            with open(WAL_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"entries": [], "last_updated": ""}


def save_wal(wal: dict):
    """Save WAL to disk."""
    WAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    wal["last_updated"] = datetime.now(TZ_VN).isoformat()
    with open(WAL_PATH, "w", encoding="utf-8") as f:
        json.dump(wal, f, indent=2, ensure_ascii=False)


def get_pending_switch(wal: dict) -> dict | None:
    """Get pending session-switch entry from WAL."""
    for e in wal.get("entries", []):
        if e.get("action") == "session-switch" and e.get("status") == "pending":
            return e
    return None


def mark_wal_done(wal: dict):
    """Mark all pending session-switch entries as done."""
    changed = False
    for e in wal.get("entries", []):
        if e.get("action") == "session-switch" and e.get("status") == "pending":
            e["status"] = "done"
            e["completed_at"] = datetime.now(TZ_VN).isoformat()
            changed = True
    if changed:
        save_wal(wal)


def add_switch_entry(wal: dict, old_session_key: str, old_session_id: str,
                     old_session_file: str, old_tokens: int):
    """Add a new session-switch WAL entry with old session info."""
    # Clean old done entries (keep last 5)
    wal["entries"] = [e for e in wal.get("entries", []) if e.get("status") != "done"][-5:]

    wal["entries"].append({
        "action": "session-switch",
        "status": "pending",
        "ts": datetime.now(TZ_VN).isoformat(),
        "old_session_key": old_session_key,
        "old_session_id": old_session_id,
        "old_session_file": old_session_file,
        "old_tokens": old_tokens,
    })
    save_wal(wal)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Context Guard — Lightweight check")
    parser.add_argument("--session", default="agent:main:main")
    parser.add_argument("--context-tokens", type=int, default=DEFAULT_CONTEXT_TOKENS)
    args = parser.parse_args()

    # Step 1: Get real context from OpenClaw
    info = get_session_info(args.session)
    if info is None:
        print(json.dumps({"action": "none", "reason": "api_unreachable"}))
        return

    # Extract token usage
    total_tokens = (info.get("totalTokens") or info.get("total_tokens")
                    or info.get("tokenCount") or 0)
    context_tokens = (info.get("contextTokens") or info.get("context_tokens")
                      or args.context_tokens)
    if context_tokens <= 0:
        context_tokens = args.context_tokens

    # Extract session identifiers for handoff
    session_id = info.get("id") or info.get("sessionId") or ""
    session_file = info.get("file") or info.get("sessionFile") or ""
    session_key = info.get("key") or info.get("sessionKey") or args.session

    usage_percent = total_tokens / context_tokens if context_tokens > 0 else 0

    # Step 2: Check WAL
    wal = load_wal()
    pending = get_pending_switch(wal)

    # Step 3: WAL warm-up gate
    if pending:
        if total_tokens < WARMUP_TOKENS:
            print(json.dumps({
                "action": "none",
                "reason": "warmup_gate",
                "total_tokens": total_tokens,
                "warmup_target": WARMUP_TOKENS,
                "usage_percent": round(usage_percent * 100, 1),
                "old_session_key": pending.get("old_session_key", ""),
            }))
            return
        else:
            # New session is warm enough — compact old session & mark done
            print(json.dumps({
                "action": "compact_old",
                "reason": "warmup_complete",
                "total_tokens": total_tokens,
                "usage_percent": round(usage_percent * 100, 1),
                "old_session_key": pending.get("old_session_key", ""),
                "old_session_id": pending.get("old_session_id", ""),
                "old_session_file": pending.get("old_session_file", ""),
                "old_tokens": pending.get("old_tokens", 0),
            }))
            mark_wal_done(wal)
            return

    # Step 4: Determine urgency
    if usage_percent >= THRESHOLD_SWITCH:
        action = "switch"
        urgency = "critical"
        # Save old session info for handoff
        add_switch_entry(wal, session_key, session_id, session_file, total_tokens)
    elif usage_percent >= THRESHOLD_COMPACT:
        action = "compact"
        urgency = "high"
    else:
        action = "none"
        urgency = "medium"

    result = {
        "action": action,
        "urgency": urgency,
        "total_tokens": total_tokens,
        "context_tokens": context_tokens,
        "usage_percent": round(usage_percent * 100, 1),
        "session_key": session_key,
        "session_id": session_id,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
