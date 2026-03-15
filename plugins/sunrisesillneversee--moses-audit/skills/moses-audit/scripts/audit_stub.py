#!/usr/bin/env python3
"""
MO§ES™ Audit Stub — SHA-256 chained append-only ledger
Usage:
  python3 audit_stub.py log   [--agent X] [--action X] [--detail X] [--outcome X]
  python3 audit_stub.py verify
  python3 audit_stub.py recent [--n 10]
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

LEDGER_PATH = os.path.expanduser("~/.openclaw/audits/moses/audit_ledger.jsonl")
STATE_PATH = os.path.expanduser("~/.openclaw/governance/state.json")


def ensure_dirs():
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)


def load_state():
    if not os.path.exists(STATE_PATH):
        return {"mode": "high-integrity", "posture": "defense", "role": "primary", "vault": []}
    with open(STATE_PATH) as f:
        return json.load(f)


def get_previous_hash():
    if not os.path.exists(LEDGER_PATH):
        return "0" * 64
    with open(LEDGER_PATH) as f:
        lines = f.readlines()
    if not lines:
        return "0" * 64
    last = json.loads(lines[-1])
    return last.get("hash", "0" * 64)


def compute_hash(entry: dict) -> str:
    content = json.dumps(entry, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()


def cmd_log(args):
    ensure_dirs()
    state = load_state()
    previous_hash = get_previous_hash()

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": args.agent or state.get("role", "unknown"),
        "component": "moses-governance",
        "action": args.action or "unspecified",
        "detail": args.detail or "",
        "outcome": args.outcome or "logged",
        "mode": state.get("mode", "unknown"),
        "posture": state.get("posture", "unknown"),
        "role": state.get("role", "unknown"),
        "previous_hash": previous_hash,
    }
    entry["hash"] = compute_hash({k: v for k, v in entry.items() if k != "hash"})

    with open(LEDGER_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"[AUDIT] Entry logged. Hash: {entry['hash'][:16]}...")
    return entry["hash"]


def cmd_verify(args):
    if not os.path.exists(LEDGER_PATH):
        print("[VERIFY] No ledger found. Chain is empty.")
        return True

    with open(LEDGER_PATH) as f:
        lines = [l.strip() for l in f if l.strip()]

    if not lines:
        print("[VERIFY] Ledger is empty.")
        return True

    previous_hash = "0" * 64
    for i, line in enumerate(lines):
        entry = json.loads(line)
        stored_hash = entry.get("hash")
        entry_without_hash = {k: v for k, v in entry.items() if k != "hash"}
        computed = compute_hash(entry_without_hash)

        if computed != stored_hash:
            print(f"[VERIFY FAILED] Entry {i+1}: hash mismatch. Chain broken.")
            sys.exit(1)
        if entry.get("previous_hash") != previous_hash:
            print(f"[VERIFY FAILED] Entry {i+1}: previous_hash broken. Chain tampered.")
            sys.exit(1)
        previous_hash = stored_hash

    print(f"[VERIFY OK] Chain intact. {len(lines)} entries verified.")
    return True


def cmd_recent(args):
    if not os.path.exists(LEDGER_PATH):
        print("[RECENT] No ledger found.")
        return

    with open(LEDGER_PATH) as f:
        lines = [l.strip() for l in f if l.strip()]

    n = getattr(args, "n", 10)
    recent = lines[-n:]
    for line in recent:
        e = json.loads(line)
        print(f"[{e['timestamp']}] {e['agent'].upper()} | {e['action']} | {e['mode']}/{e['posture']} | {e['hash'][:12]}...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MO§ES™ Audit Ledger")
    subparsers = parser.add_subparsers(dest="command")

    log_p = subparsers.add_parser("log")
    log_p.add_argument("--agent")
    log_p.add_argument("--action")
    log_p.add_argument("--detail")
    log_p.add_argument("--outcome")

    verify_p = subparsers.add_parser("verify")

    recent_p = subparsers.add_parser("recent")
    recent_p.add_argument("--n", type=int, default=10)

    args = parser.parse_args()

    if args.command == "log":
        cmd_log(args)
    elif args.command == "verify":
        cmd_verify(args)
    elif args.command == "recent":
        cmd_recent(args)
    else:
        parser.print_help()
