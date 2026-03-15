#!/usr/bin/env python3
"""
Night School Runner — Pulls payload, executes tasks, submits morning report.

Usage:
  python3 night-school-run.py --base-url URL --session-id ID --callback-token TOKEN [--dry-run]

This script handles the mechanical parts (API calls).
The actual "thinking" (research, content generation) is done by the calling agent
who reads the payload and generates the report content.

Modes:
  - pull:   Fetch and display the payload for this session
  - submit: Submit a report JSON (read from stdin or --report-file)
  - check:  Check if a report already exists for this session
"""

import argparse
import json
import sys
import urllib.request
import urllib.error


def api_get(url: str) -> dict:
    """GET request, return parsed JSON."""
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


def api_post(url: str, data: dict, callback_token: str = None) -> dict:
    """POST JSON request, return parsed JSON."""
    body = json.dumps(data).encode()
    headers = {"Content-Type": "application/json"}
    if callback_token:
        headers["X-Callback-Token"] = callback_token
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode() if e.fp else ""
        print(f"HTTP {e.code}: {err_body}", file=sys.stderr)
        sys.exit(1)


def cmd_pull(args):
    """Pull and display the payload."""
    url = f"{args.base_url}/api/enrollments/{args.session_id}/payload"
    payload = api_get(url)
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def cmd_check(args):
    """Check if a report already exists."""
    url = f"{args.base_url}/api/enrollments/{args.session_id}/payload"
    payload = api_get(url)
    exists = payload.get("reportExists", False)
    print(f"Report exists: {exists}")
    return 0 if not exists else 1


def cmd_submit(args):
    """Submit a report."""
    # Read report from file or stdin
    if args.report_file:
        with open(args.report_file, "r") as f:
            report = json.load(f)
    else:
        print("Reading report JSON from stdin...", file=sys.stderr)
        report = json.load(sys.stdin)

    # callbackToken goes inside the JSON body (not as a header)
    report["callbackToken"] = args.callback_token

    if args.dry_run:
        print("=== DRY RUN — would submit: ===")
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    url = f"{args.base_url}/api/enrollments/{args.session_id}/report"
    result = api_post(url, report)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result.get("ok"):
        report_url = f"{args.base_url}{result.get('reportPageUrl', '')}"
        print(f"\n✅ Report submitted! View at: {report_url}", file=sys.stderr)
    else:
        print(f"\n❌ Submission failed: {result.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Night School Runner")
    parser.add_argument("--base-url", required=True, help="Night School platform URL")
    parser.add_argument("--session-id", required=True, help="Enrollment session ID")
    parser.add_argument("--callback-token", help="Report callback token")
    parser.add_argument("--dry-run", action="store_true", help="Print report without submitting")
    parser.add_argument("--report-file", help="Path to report JSON file (otherwise reads stdin)")

    sub = parser.add_subparsers(dest="command")
    sub.add_parser("pull", help="Pull payload for this session")
    sub.add_parser("check", help="Check if report already exists")
    sub.add_parser("submit", help="Submit a report")

    args = parser.parse_args()

    if not args.command:
        # Default: pull
        args.command = "pull"

    if args.command == "pull":
        cmd_pull(args)
    elif args.command == "check":
        sys.exit(cmd_check(args))
    elif args.command == "submit":
        if not args.callback_token:
            print("Error: --callback-token required for submit", file=sys.stderr)
            sys.exit(1)
        cmd_submit(args)


if __name__ == "__main__":
    main()
