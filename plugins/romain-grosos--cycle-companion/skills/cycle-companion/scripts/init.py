#!/usr/bin/env python3
"""
cycle-companion init - Validate config and schedule first cron notification.
Run after setup.py. The agent reads the cron payload output and creates the job.
Usage:
  init.py        Validate config + print cron payload for next transition
"""

import sys
import json
import os
import subprocess
from datetime import date

CONFIG_PATH = os.path.expanduser("~/.openclaw/config/cycle-companion/config.json")
CYCLE_SCRIPT = os.path.join(os.path.dirname(__file__), "cycle.py")


def main():
    if not os.path.exists(CONFIG_PATH):
        print(json.dumps({"status": "error", "message": f"Config not found: {CONFIG_PATH}. Run setup.py first."}))
        sys.exit(1)

    with open(CONFIG_PATH, encoding="utf-8") as f:
        cfg = json.load(f)

    # Required fields
    required = ["last_period_date", "cycle_length", "luteal_length", "language"]
    missing = [k for k in required if k not in cfg or cfg[k] is None]
    if missing:
        print(json.dumps({"status": "error", "message": f"Missing config keys: {missing}"}))
        sys.exit(1)

    # Validate date
    try:
        d = date.fromisoformat(cfg["last_period_date"])
        if d > date.today():
            print(json.dumps({"status": "error", "message": "last_period_date is in the future"}))
            sys.exit(1)
    except ValueError:
        print(json.dumps({"status": "error", "message": f"Invalid last_period_date: {cfg['last_period_date']}"}))
        sys.exit(1)

    # Cross-parameter validation (delegate to cycle.py which will validate and exit on error)
    # Get current status
    result = subprocess.run(
        [sys.executable, CYCLE_SCRIPT, "status"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        error_msg = stderr or stdout or "Unknown error from cycle.py status"
        print(json.dumps({"status": "error", "message": error_msg}))
        sys.exit(1)

    status = json.loads(result.stdout)

    # Get cron payload for next transition
    cron_result = subprocess.run(
        [sys.executable, CYCLE_SCRIPT, "schedule-cron"],
        capture_output=True, text=True
    )
    if cron_result.returncode != 0:
        stderr = cron_result.stderr.strip()
        stdout = cron_result.stdout.strip()
        error_msg = stderr or stdout or "Unknown error from cycle.py schedule-cron"
        print(json.dumps({"status": "error", "message": error_msg}))
        sys.exit(1)

    cron_payload = json.loads(cron_result.stdout)

    print(json.dumps({
        "status": "ok",
        "config": {
            "last_period_date": cfg["last_period_date"],
            "cycle_length": cfg["cycle_length"],
            "luteal_length": cfg["luteal_length"],
            "menstruation_days": cfg.get("menstruation_days", 5),
            "pms_days": cfg.get("pms_days", 7),
            "notification_time": cfg.get("notification_time", "08:00"),
            "language": cfg["language"],
            "outputs": cfg.get("outputs", []),
        },
        "current_phase": status["phase_name"],
        "day_in_cycle": status["day_in_cycle"],
        "fertility": status.get("fertility_window", {}).get("current_level", "unknown"),
        "next_transition_date": status["next_transition_date"],
        "next_phase": status["next_phase_name"],
        "cron_payload": cron_payload,
        "message": "Config valid. Use cron_payload to schedule the next phase notification.",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
