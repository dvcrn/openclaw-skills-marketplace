#!/usr/bin/env python3
"""
Gateway-back watcher for what-just-happened skill.
Runs periodically (e.g. every 15s via LaunchAgent). When it detects the gateway
transition from down → up, it triggers an agent turn with the what-just-happened
message and announce delivery so the user sees the response in TUI or Telegram.

Usage: run as a daemon (LaunchAgent). Install with install_gateway_back_watcher.sh
"""

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

OPENCLAW_HOME = Path(os.environ.get("OPENCLAW_HOME", str(Path.home() / ".openclaw")))
OPENCLAW_BIN = os.environ.get("OPENCLAW_BIN", "openclaw")  # full path from install script for LaunchAgent
STATE_FILE = OPENCLAW_HOME / "logs" / "what-just-happened.gateway-state.json"
INTERVAL_SEC = 15
MESSAGE = (
    "Are you finished with your task? Check the logs from the last 5 minutes. "
    "Run: python3 {skill_dir}/scripts/report_recent_logs.py --minutes 5. "
    "Briefly describe any errors. Propose a quality solution. Announce your summary to the user."
).format(skill_dir=OPENCLAW_HOME / "workspace" / "skills" / "what-just-happened")


def _log(msg: str) -> None:
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    line = f"{ts} [what-just-happened] {msg}"
    print(line, flush=True)
    print(line, file=sys.stderr, flush=True)


def _gateway_port() -> int:
    """Read gateway port from openclaw.json; default 18789."""
    cfg = OPENCLAW_HOME / "openclaw.json"
    if not cfg.exists():
        return 18789
    try:
        with open(cfg) as f:
            data = json.load(f)
        return int(data.get("gateway", {}).get("port", 18789))
    except (json.JSONDecodeError, KeyError, TypeError):
        return 18789


def gateway_is_up() -> bool:
    """Probe gateway by TCP connect to port (avoids openclaw CLI which can fail in LaunchAgent)."""
    port = _gateway_port()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            s.connect(("127.0.0.1", port))
        return True
    except (OSError, socket.error):
        return False


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"last_was_up": False, "last_check_ts": None}
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"last_was_up": False, "last_check_ts": None}


def save_state(last_was_up: bool) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump({
            "last_was_up": last_was_up,
            "last_check_ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }, f, indent=2)


def trigger_what_just_happened() -> None:
    """Run one agent turn with the what-just-happened message and announce."""
    env = {**os.environ, "OPENCLAW_HOME": str(OPENCLAW_HOME), "WJH_MSG": MESSAGE}

    def run_cmd(args, e=None):
        return subprocess.run(
            args,
            env=e or env,
            cwd=str(OPENCLAW_HOME),
            timeout=120,
            capture_output=True,
            text=True,
        )

    cmd = [OPENCLAW_BIN, "agent", "--message", MESSAGE, "--deliver"]
    try:
        r = run_cmd(cmd)
        if r.returncode != 0:
            # LaunchAgent can break Node's uv_interface_addresses; try login shell
            _log(f"trigger exit={r.returncode} stderr={r.stderr[:300] if r.stderr else 'none'}")
            r2 = run_cmd(
                ["bash", "-l", "-c", f'exec "{OPENCLAW_BIN}" agent --message "$WJH_MSG" --deliver'],
                e={**env, "WJH_MSG": MESSAGE},
            )
            if r2.returncode == 0:
                _log("trigger succeeded via login shell")
            elif r2.stderr:
                _log(f"login shell trigger exit={r2.returncode} stderr={r2.stderr[:300]}")
    except FileNotFoundError as e:
        _log(f"trigger failed: openclaw not found (set OPENCLAW_BIN or run install script): {e}")
    except subprocess.TimeoutExpired as e:
        _log(f"trigger failed: timeout {e}")


def main() -> int:
    state = load_state()
    now_up = gateway_is_up()
    last_up = state.get("last_was_up", False)

    # Log every run (so logs show watcher is alive; keep one line)
    _log(f"check gateway_up={now_up} last_was_up={last_up}")

    # Only trigger when gateway transitions from down to up (not on first run when already up)
    if now_up and not last_up:
        if STATE_FILE.exists():
            _log("Gateway just came back online; triggering what-just-happened.")
            trigger_what_just_happened()
        # else: first run, no prior state; just record current state without triggering

    save_state(now_up)
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--loop":
        _log("Gateway-back watcher started (loop every %ss)." % INTERVAL_SEC)
        while True:
            main()
            time.sleep(INTERVAL_SEC)
    else:
        sys.exit(main())
