#!/bin/bash
# SECURITY MANIFEST:
# Environment variables accessed: ARC_API_TOKEN (only)
# External endpoints called: https://www.airunningcoach.net/api/v1/ (only)
# Local files read: ~/.config/ai-running-coach/config.json
# Local files written: ~/.config/ai-running-coach/config.json (setup only)
# AI Running Coach - Ask Your Coach

CONFIG_FILE="$HOME/.config/ai-running-coach/config.json"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "Not set up yet. Run the setup command first."
  exit 1
fi

MESSAGE="$*"
if [ -z "$MESSAGE" ]; then
  echo "Usage: coach <your question>"
  echo "Example: coach Should I run today if my legs are sore?"
  exit 1
fi

TOKEN=$(cat "$CONFIG_FILE" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
BASE_URL=$(cat "$CONFIG_FILE" | grep -o '"base_url":"[^"]*"' | cut -d'"' -f4)

echo "🤔 Thinking..."
echo ""

RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"$MESSAGE\"}" \
  "$BASE_URL/api/v1/coach")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
  echo "Error contacting coach. Please try again."
  exit 1
fi

if command -v jq &> /dev/null; then
  REPLY=$(echo "$BODY" | jq -r '.response')
  SUGGESTIONS=$(echo "$BODY" | jq -r '.suggestions // [] | .[]' 2>/dev/null)
else
  REPLY=$(echo "$BODY" | grep -o '"response":"[^"]*"' | cut -d'"' -f4)
  SUGGESTIONS=""
fi

echo "🏃 Coach says:"
echo "$REPLY"

if [ -n "$SUGGESTIONS" ]; then
  echo ""
  echo "💡 Suggestions:"
  echo "$SUGGESTIONS" | while read -r line; do
    echo "  • $line"
  done
fi
