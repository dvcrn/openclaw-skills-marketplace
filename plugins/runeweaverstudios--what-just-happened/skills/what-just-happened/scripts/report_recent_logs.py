#!/usr/bin/env python3
"""
What Just Happened — Summarize recent gateway restarts/reconnects from logs.
Output: short message suitable for posting (e.g. to chat) so the user knows what happened.

Checks two gateway log locations:
1. Main OpenClaw (TUI/CLI) gateway: OPENCLAW_HOME/logs/gateway.log (~/.openclaw/logs)
2. OverClaw gateway (port 18800): WORKSPACE/.overstory/logs/overclaw-gateway.log
   (OVERCLAW_WORKSPACE or script walk-up to find workspace with .overstory/logs)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone, timedelta

OPENCLAW_HOME = Path(os.environ.get("OPENCLAW_HOME", str(Path.home() / ".openclaw")))
LOGS_DIR = OPENCLAW_HOME / "logs"
GATEWAY_LOG = LOGS_DIR / "gateway.log"
GUARD_RESTART_LOG = LOGS_DIR / "gateway-guard.restart.log"


def _overclaw_log_dir() -> Optional[Path]:
    """Resolve OverClaw workspace .overstory/logs (for overclaw-gateway.log, nanobot-agent.log)."""
    for env in ("OVERCLAW_WORKSPACE", "OPENCLAW_WORKSPACE", "WORKSPACE"):
        val = os.environ.get(env, "").strip()
        if val:
            p = Path(val).resolve()
            if (p / ".overstory" / "logs").is_dir():
                return p / ".overstory" / "logs"
    # Walk up from this script to find workspace with .overstory/logs
    candidate = Path(__file__).resolve().parent
    for _ in range(12):
        log_dir = candidate / ".overstory" / "logs"
        if log_dir.is_dir():
            return log_dir
        parent = candidate.parent
        if parent == candidate:
            break
        candidate = parent
    return None


OVERCLAW_LOG_DIR = _overclaw_log_dir()
OVERCLAW_GATEWAY_LOG = OVERCLAW_LOG_DIR / "overclaw-gateway.log" if OVERCLAW_LOG_DIR else None
NANOBOT_AGENT_LOG = OVERCLAW_LOG_DIR / "nanobot-agent.log" if OVERCLAW_LOG_DIR else None

def parse_iso_ts(line: str):
    """Extract ISO timestamp from log line; return None if not found. Always returns timezone-aware UTC."""
    m = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)", line.strip())
    if m:
        s = m.group(1).replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            pass
    return None


def parse_python_log_ts(line: str):
    """Parse Python logging style timestamp (YYYY-MM-DD HH:MM:SS or YYYY-MM-DD HH:MM:SS,mmm). Returns naive local-like; treat as UTC for cutoff."""
    m = re.match(r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})(?:[.,]\d+)?", line.strip())
    if m:
        try:
            return datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None

def read_tail(path: Path, max_lines: int = 200) -> list[str]:
    if not path.exists():
        return []
    with open(path, "r") as f:
        lines = f.readlines()
    return lines[-max_lines:] if len(lines) > max_lines else lines

def analyze_last_n_minutes(minutes: int) -> dict:
    """Analyze gateway.log and guard log for the last N minutes."""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    out = {
        "restart": False,
        "reload": False,
        "sigusr1": False,
        "sigterm": False,
        "auth_or_config": False,
        "guard_restart": False,
        "snippets": [],
        "summary": "",
        "suggestGatewayGuard": False,
    }
    snippets = []

    for path in [GATEWAY_LOG, GUARD_RESTART_LOG]:
        if path == GUARD_RESTART_LOG and not path.exists():
            continue
        for line in read_tail(path, 300):
            ts = parse_iso_ts(line)
            if ts and ts < cutoff:
                continue
            line_lower = line.lower()
            if "sigusr1" in line_lower or "restarting" in line_lower:
                out["sigusr1"] = True
                out["restart"] = True
                snippets.append(line.strip())
            if "sigterm" in line_lower and "shutting down" in line_lower:
                out["sigterm"] = True
                out["restart"] = True
            if "[reload]" in line and ("config change" in line or "gateway.auth" in line):
                out["reload"] = True
                out["auth_or_config"] = True
                snippets.append(line.strip())
            if "listening on ws://" in line_lower:
                snippets.append(line.strip())
            if path == GUARD_RESTART_LOG and ("restart" in line_lower or "ensure" in line_lower):
                out["guard_restart"] = True

    if out["restart"] or out["reload"]:
        parts = []
        if out["reload"] and out["auth_or_config"]:
            parts.append("Gateway restarted due to config change (e.g. gateway.auth or meta).")
            out["suggestGatewayGuard"] = True
        elif out["sigusr1"]:
            parts.append("Gateway received SIGUSR1 and restarted.")
        elif out["sigterm"]:
            parts.append("Gateway was stopped (SIGTERM) and has since come back up.")
        else:
            parts.append("Gateway restarted recently.")
        parts.append("Reconnected.")
        if out["suggestGatewayGuard"]:
            parts.append(
                "Tip: use gateway-guard to keep auth stable and avoid unnecessary restarts. "
                "Install: clawhub install gateway-guard — https://clawhub.ai/skills/gateway-guard"
            )
        out["summary"] = " ".join(parts)
    else:
        out["summary"] = "No recent gateway restart or reload in the last {} minutes.".format(minutes)

    out["snippets"] = snippets[-10:]
    return out


def analyze_overclaw_last_n_minutes(minutes: int) -> dict:
    """Analyze OverClaw gateway (port 18800) and optionally nanobot-agent logs under workspace .overstory/logs."""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    out = {
        "overclaw_restart": False,
        "overclaw_started": False,
        "overclaw_errors": [],
        "overclaw_log_path": str(OVERCLAW_GATEWAY_LOG) if OVERCLAW_GATEWAY_LOG else None,
        "nanobot_log_path": str(NANOBOT_AGENT_LOG) if NANOBOT_AGENT_LOG else None,
        "summary_overclaw": "",
    }
    if not OVERCLAW_GATEWAY_LOG or not OVERCLAW_GATEWAY_LOG.exists():
        out["summary_overclaw"] = "OverClaw gateway log not found (no workspace .overstory/logs/overclaw-gateway.log)."
        return out

    for path in [OVERCLAW_GATEWAY_LOG, NANOBOT_AGENT_LOG]:
        if path is None or not path.exists():
            continue
        for line in read_tail(path, 300):
            ts = parse_python_log_ts(line) or parse_iso_ts(line)
            if ts and ts < cutoff:
                continue
            line_lower = line.lower()
            if "overclaw gateway starting" in line_lower or "uvicorn running" in line_lower or "started server" in line_lower:
                out["overclaw_started"] = True
                out["overclaw_restart"] = True
            if "error" in line_lower or "traceback" in line_lower or "exception" in line_lower:
                out["overclaw_errors"].append(line.strip()[:200])
    out["overclaw_errors"] = out["overclaw_errors"][-5:]

    if out["overclaw_restart"] or out["overclaw_started"]:
        out["summary_overclaw"] = (
            "OverClaw gateway (port 18800) logs show recent startup/restart. "
            "Log: {}".format(out["overclaw_log_path"])
        )
    elif out["overclaw_errors"]:
        out["summary_overclaw"] = "OverClaw gateway (port 18800) logs show recent errors. Check {}.".format(out["overclaw_log_path"])
    else:
        out["summary_overclaw"] = "No recent OverClaw gateway (18800) restart in the last {} minutes. Log: {}.".format(
            minutes, out["overclaw_log_path"]
        )
    return out


def main():
    ap = argparse.ArgumentParser(description="Report recent gateway restarts/reconnects from logs")
    ap.add_argument("--minutes", type=int, default=5, help="Look at last N minutes of logs")
    ap.add_argument("--json", action="store_true", help="Output JSON only")
    ap.add_argument("--overclaw-only", action="store_true", help="Only check OverClaw gateway logs (workspace .overstory/logs)")
    args = ap.parse_args()

    result = {}
    if args.overclaw_only:
        result = analyze_overclaw_last_n_minutes(args.minutes)
        if args.json:
            print(json.dumps({k: v for k, v in result.items() if k not in ("overclaw_errors",) or v}))
        else:
            print(result.get("summary_overclaw", "No OverClaw log path found."))
        sys.exit(0)

    if GATEWAY_LOG.exists():
        result = analyze_last_n_minutes(args.minutes)
    else:
        result = {"summary": "", "snippets": []}

    overclaw = analyze_overclaw_last_n_minutes(args.minutes)
    result["overclaw"] = overclaw

    if not GATEWAY_LOG.exists() and not (OVERCLAW_GATEWAY_LOG and OVERCLAW_GATEWAY_LOG.exists()):
        print("No gateway log found. Tried: {} and OverClaw workspace .overstory/logs/overclaw-gateway.log".format(GATEWAY_LOG), file=sys.stderr)
        sys.exit(1)

    if args.json:
        out = {k: v for k, v in result.items() if k != "snippets" or v}
        if "overclaw" in out and "overclaw_errors" in out["overclaw"]:
            out["overclaw"]["overclaw_errors"] = out["overclaw"]["overclaw_errors"][:5]
        print(json.dumps(out))
        return

    lines = [result["summary"]]
    if overclaw.get("summary_overclaw"):
        lines.append(overclaw["summary_overclaw"])
    print(" ".join(lines) if len(lines) == 1 else "\n".join(lines))

if __name__ == "__main__":
    main()
