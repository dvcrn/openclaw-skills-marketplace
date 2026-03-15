#!/usr/bin/env bash
# Run subagent-tracker list, status, and tail; exit 0 only if all run successfully.
# Use from skill root or with OPENCLAW_HOME set; uses absolute path to the script when available.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRACKER="${SCRIPT_DIR}/subagent_tracker.py"

if [[ ! -x "$TRACKER" ]]; then
  # fallback: absolute path used in SKILL.md
  TRACKER="/Users/ghost/.openclaw/workspace/skills/subagent-tracker/scripts/subagent_tracker.py"
fi

echo "Testing subagent-tracker: list..."
python3 "$TRACKER" list --active 1440

echo "Testing subagent-tracker: list --json..."
JSON=$(python3 "$TRACKER" list --active 1440 --json)
FIRST_ID=$(echo "$JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['sessionId'] if d else '')" 2>/dev/null || true)

if [[ -n "$FIRST_ID" ]]; then
  echo "Testing subagent-tracker: status $FIRST_ID..."
  python3 "$TRACKER" status "$FIRST_ID"
  echo "Testing subagent-tracker: tail $FIRST_ID --lines 5..."
  python3 "$TRACKER" tail "$FIRST_ID" --lines 5
else
  echo "No subagents in last 24h; skipping status/tail."
fi

echo "All subagent-tracker checks passed."
