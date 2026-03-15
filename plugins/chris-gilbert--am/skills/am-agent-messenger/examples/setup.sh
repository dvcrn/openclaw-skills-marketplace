#!/usr/bin/env bash
# Idempotent first-time setup for a new am agent identity.
#
# Usage: ./setup.sh [identity-name]
#   identity-name defaults to "default"
#
# Outputs the npub to stdout on success (for capture by callers).
# All status messages go to stderr.

set -euo pipefail

IDENTITY="${1:-default}"

echo "=== am setup: identity '$IDENTITY' ===" >&2

# Generate identity if it doesn't already exist
if am identity show --name "$IDENTITY" >/dev/null 2>&1; then
  echo "Identity '$IDENTITY' already exists." >&2
  NPUB=$(am identity show --name "$IDENTITY" | jq -r '.npub')
else
  echo "Generating identity '$IDENTITY'..." >&2
  NPUB=$(am identity generate --name "$IDENTITY" | jq -r '.npub')
  echo "Generated." >&2
fi

# Add default relays if not already configured
add_relay_if_missing() {
  local url="$1"
  if am relay list | jq -e --arg u "$url" '.[] | select(.url == $u)' >/dev/null 2>&1; then
    echo "Relay already configured: $url" >&2
  else
    am relay add "$url"
    echo "Added relay: $url" >&2
  fi
}

add_relay_if_missing "wss://relay.damus.io"
add_relay_if_missing "wss://nos.lol"

echo "" >&2
echo "=== Setup complete ===" >&2
echo "Identity: $IDENTITY" >&2
echo "npub:     $NPUB" >&2
echo "" >&2
echo "Share this npub with agents or humans who need to reach you." >&2

# Output npub to stdout for capture
echo "$NPUB"
