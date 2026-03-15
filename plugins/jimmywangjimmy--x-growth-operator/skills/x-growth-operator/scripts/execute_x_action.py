from __future__ import annotations

import argparse
import json
import subprocess
from urllib.parse import urlparse

from common import load_json


def tweet_id_from_url(url: str) -> str | None:
    path = urlparse(url).path.strip("/")
    parts = path.split("/")
    if len(parts) >= 3 and parts[-2] == "status":
        return parts[-1]
    return None


def build_command(action: dict) -> list[str]:
    action_type = action.get("action_type")
    draft_text = action.get("draft_text", "")
    target_url = action.get("target_url", "")
    target_id = tweet_id_from_url(target_url or "")

    if action_type == "reply":
        if not target_id:
            raise SystemExit("Reply action requires target_url containing a tweet id.")
        return ["node", "scripts/x_oauth_cli.js", "post", "--text", draft_text, "--reply-to", target_id]

    if action_type == "quote_post":
        if not target_id:
            raise SystemExit("Quote action requires target_url containing a tweet id.")
        return ["node", "scripts/x_oauth_cli.js", "post", "--text", draft_text, "--quote", target_id]

    if action_type == "post":
        return ["node", "scripts/x_oauth_cli.js", "post", "--text", draft_text]

    if action_type == "thread":
        parts = action.get("thread_parts") or [segment.strip() for segment in draft_text.split("\n\n") if segment.strip()]
        if not parts:
            raise SystemExit("Thread action requires thread_parts or split-able draft_text.")
        cmd = ["node", "scripts/x_oauth_cli.js", "thread", "--parts"]
        cmd.extend(parts)
        return cmd

    raise SystemExit(f"Unsupported action_type for X execution: {action_type}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute an action.json against the X OAuth CLI.")
    parser.add_argument("--action", default="data/action.json", help="Action JSON path.")
    parser.add_argument("--print-command", action="store_true", help="Print the underlying command instead of executing.")
    args = parser.parse_args()

    action = load_json(args.action)
    cmd = build_command(action)
    if args.print_command:
        print(" ".join(json.dumps(part) for part in cmd))
        return 0

    completed = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        if completed.stderr.strip():
            raise SystemExit(completed.stderr.strip())
        raise SystemExit(completed.stdout.strip() or "X execution failed")

    print(completed.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
