from __future__ import annotations

import argparse
import json
import subprocess

from common import append_jsonl, load_json, utc_now_iso, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Record execution of an approved X action.")
    parser.add_argument("--mission", default="data/mission.json", help="Mission JSON path.")
    parser.add_argument("--action", default="data/action.json", help="Action JSON path.")
    parser.add_argument("--log", default="data/execution_log.jsonl", help="Execution log JSONL path.")
    parser.add_argument("--approved", action="store_true", help="Mark the action as user approved.")
    parser.add_argument("--mode", choices=["dry-run", "record-only", "x-api"], default="dry-run", help="Execution mode.")
    args = parser.parse_args()

    mission = load_json(args.mission)
    action = load_json(args.action)

    if action.get("requires_approval", True) and not args.approved:
        raise SystemExit("Refusing to execute without --approved.")

    execution_output = None
    if args.mode == "x-api":
        completed = subprocess.run(
            ["python3", "scripts/execute_x_action.py", "--action", args.action],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise SystemExit(completed.stderr.strip() or completed.stdout.strip() or "X execution failed")
        execution_output = completed.stdout.strip()

    result = {
        "executed_at": utc_now_iso(),
        "mode": args.mode,
        "mission_name": mission.get("name", ""),
        "action_id": action.get("id"),
        "action_type": action.get("action_type"),
        "target_url": action.get("target_url"),
        "target_account": action.get("target_account"),
        "draft_text": action.get("draft_text"),
        "status": "recorded" if args.mode == "record-only" else "executed" if args.mode == "x-api" else "dry_run_executed",
    }
    if execution_output:
        try:
            result["provider_result"] = json.loads(execution_output)
        except json.JSONDecodeError:
            result["provider_result_raw"] = execution_output
    append_jsonl(args.log, result)

    action["status"] = "executed"
    action["executed_at"] = result["executed_at"]
    action["execution_mode"] = args.mode
    write_json(args.action, action)

    print(f"Execution recorded for {action.get('id')} in {args.mode} mode")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
