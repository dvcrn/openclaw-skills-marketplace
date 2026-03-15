#!/usr/bin/env bash
# Demonstrates am send and receive patterns.
#
# Usage: ./messaging.sh <recipient-npub>
#
# Sends two messages to the recipient, then checks for recent
# incoming messages and prints them.

set -euo pipefail

RECIPIENT="${1:-}"

if [ -z "$RECIPIENT" ]; then
  echo "Usage: $0 <recipient-npub>" >&2
  exit 2
fi

MY_NPUB=$(am identity show | jq -r '.npub')
MY_NAME=$(am identity show | jq -r '.name')

echo "=== Sending messages ===" >&2

# Send a plain text message
am send --to "$RECIPIENT" "Hello from $MY_NAME"
echo "Sent plain text message." >&2

# Send a structured JSON payload via stdin
jq -n \
  --arg from "$MY_NPUB" \
  --arg name "$MY_NAME" \
  --argjson ts "$(date +%s)" \
  '{
    "type": "greeting",
    "from_name": $name,
    "from_npub": $from,
    "timestamp": $ts
  }' | am send --to "$RECIPIENT"
echo "Sent structured JSON message." >&2

echo "" >&2
echo "=== Checking received messages (last hour) ===" >&2

SINCE=$(($(date +%s) - 3600))
count=0

while IFS= read -r msg; do
  FROM=$(echo "$msg" | jq -r '.from')
  CONTENT=$(echo "$msg" | jq -r '.content')
  TS=$(echo "$msg" | jq -r '.created_at')
  echo "[$TS] from $FROM: $CONTENT" >&2
  count=$((count + 1))
done < <(am listen --once --since "$SINCE")

echo "" >&2
if [ "$count" -eq 0 ]; then
  echo "No messages received in the last hour." >&2
else
  echo "Received $count message(s)." >&2
fi

echo "" >&2
echo "=== Streaming (Ctrl+C to stop) ===" >&2
echo "Waiting for incoming messages..." >&2
am listen | while IFS= read -r msg; do
  FROM=$(echo "$msg" | jq -r '.from')
  CONTENT=$(echo "$msg" | jq -r '.content')
  TS=$(echo "$msg" | jq -r '.created_at')
  echo "[$TS] $FROM: $CONTENT"
done
