#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from lib.storage import load_history, save_history
from lib.safety import risk_level, requires_confirmation

def main():
    parser = argparse.ArgumentParser(description="Run a local shell command with safety checks")
    parser.add_argument("--command", required=True, help="Shell command to run")
    parser.add_argument("--cwd", default=".", help="Working directory")
    parser.add_argument("--yes", action="store_true", help="Confirm high-risk execution")
    args = parser.parse_args()

    risk = risk_level(args.command)
    if requires_confirmation(args.command) and not args.yes:
        print("Blocked: high-risk command requires explicit confirmation with --yes")
        print(f"Risk level: {risk}")
        sys.exit(2)

    try:
        completed = subprocess.run(
            args.command,
            shell=True,
            cwd=args.cwd,
            text=True,
            capture_output=True
        )
    except Exception as e:
        print(f"Execution failed: {e}")
        sys.exit(1)

    history = load_history()
    history["runs"].append({
        "timestamp": datetime.now().isoformat(),
        "command": args.command,
        "cwd": os.path.abspath(args.cwd),
        "risk": risk,
        "returncode": completed.returncode,
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-4000:]
    })
    save_history(history)

    print(f"Command: {args.command}")
    print(f"Risk: {risk}")
    print(f"Return code: {completed.returncode}")
    print("--- STDOUT ---")
    print(completed.stdout.rstrip() or "(empty)")
    print("--- STDERR ---")
    print(completed.stderr.rstrip() or "(empty)")

    sys.exit(completed.returncode)

if __name__ == "__main__":
    main()
