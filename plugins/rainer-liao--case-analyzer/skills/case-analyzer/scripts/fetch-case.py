#!/usr/bin/env python3
"""Fetch all traces for a specific conversation/case from Langfuse.

Looks up matching traces in the local index (or queries the API),
then fetches full trace details for each.

Requires env vars: LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST
"""

import argparse
import subprocess
import json
import os
import sys


def check_credentials():
    missing = [k for k in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST") if not os.environ.get(k)]
    if missing:
        print(f"Missing env vars: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)


def find_traces_in_index(index_path: str, conversation_id: str = None, session_id: str = None) -> list[dict]:
    """Search local index for matching traces."""
    if not os.path.exists(index_path):
        return []

    with open(index_path) as f:
        index = json.load(f)

    matches = []
    for t in index.get("traces", []):
        if conversation_id and conversation_id in (t.get("name") or ""):
            matches.append(t)
        elif session_id and t.get("sessionId") == session_id:
            matches.append(t)

    return sorted(matches, key=lambda t: t.get("timestamp", ""))


def find_traces_via_api(conversation_id: str = None, session_id: str = None) -> list[dict]:
    """Query Langfuse API directly when no local index exists."""
    args = [
        "npx", "langfuse-cli", "api", "traces", "list",
        "--limit", "50",
        "--order-by", "timestamp.asc",
        "--json",
    ]
    if session_id:
        args.extend(["--session-id", session_id])

    result = subprocess.run(args, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        print(f"API error: {result.stderr.strip()}", file=sys.stderr)
        return []

    data = json.loads(result.stdout)
    traces = data.get("body", {}).get("data", [])

    if conversation_id:
        traces = [t for t in traces if conversation_id in (t.get("name") or "")]

    return sorted(traces, key=lambda t: t.get("timestamp", ""))


def fetch_trace_detail(trace_id: str) -> dict:
    """Fetch full trace details including input/output."""
    result = subprocess.run(
        ["npx", "langfuse-cli", "api", "traces", "get", trace_id, "--json"],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to fetch trace {trace_id}: {result.stderr.strip()}")
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description="Fetch all traces for a conversation/case")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--conversation-id", help="Conversation ID (e.g., 10037737676)")
    group.add_argument("--session-id", help="Full Langfuse session ID")
    parser.add_argument("--output-dir", required=True, help="Base data directory")
    args = parser.parse_args()

    check_credentials()

    conv_id = args.conversation_id
    index_path = os.path.join(args.output_dir, "trace-index.json")

    print("Looking up traces...")
    traces = find_traces_in_index(index_path, conversation_id=conv_id, session_id=args.session_id)

    if not traces:
        print("No local index match, querying API directly...")
        traces = find_traces_via_api(conversation_id=conv_id, session_id=args.session_id)

    if not traces:
        print("No traces found.", file=sys.stderr)
        sys.exit(1)

    folder_name = conv_id or args.session_id.replace("/", "_")
    case_dir = os.path.join(args.output_dir, "cases", folder_name)
    os.makedirs(case_dir, exist_ok=True)

    print(f"Found {len(traces)} traces. Fetching details...")

    for i, t in enumerate(traces, 1):
        trace_id = t["id"]
        short_id = trace_id[:8]
        out_path = os.path.join(case_dir, f"trace-{i}-{short_id}.json")

        if os.path.exists(out_path):
            print(f"  [{i}/{len(traces)}] trace-{i}-{short_id}.json (cached)")
            continue

        print(f"  [{i}/{len(traces)}] Fetching {short_id}...")
        try:
            detail = fetch_trace_detail(trace_id)
            body = detail.get("body", detail)
            with open(out_path, "w") as f:
                json.dump(body, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"  ERROR: {e}", file=sys.stderr)

    print(f"\nDone. Traces saved to {case_dir}/")


if __name__ == "__main__":
    main()
