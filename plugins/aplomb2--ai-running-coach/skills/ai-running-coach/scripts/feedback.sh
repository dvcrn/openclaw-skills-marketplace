#!/bin/bash
# SECURITY MANIFEST:
# Environment variables accessed: ARC_API_TOKEN (only)
# External endpoints called: https://www.airunningcoach.net/api/v1/ (only)
# Local files read: ~/.config/ai-running-coach/config.json
# Local files written: ~/.config/ai-running-coach/config.json (setup only)
# AI Running Coach - Submit Body Feedback

CONFIG_FILE="$HOME/.config/ai-running-coach/config.json"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "Not set up yet. Run the setup command first."
  exit 1
fi

TYPE="$1"
shift
DESCRIPTION="$*"

if [ -z "$TYPE" ]; then
  echo "Usage: feedback <type> <description>"
  echo ""
  echo "Types: injury, fatigue, soreness, other"
  echo "Example: feedback soreness My calves are tight after yesterday's run"
  exit 1
fi

# Validate type
case "$TYPE" in
  injury|fatigue|soreness|other) ;;
  *)
    echo "Invalid type: $TYPE"
    echo "Valid types: injury, fatigue, soreness, other"
    exit 1
    ;;
esac

TOKEN=$(cat "$CONFIG_FILE" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
BASE_URL=$(cat "$CONFIG_FILE" | grep -o '"base_url":"[^"]*"' | cut -d'"' -f4)

RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"type\":\"$TYPE\",\"description\":\"$DESCRIPTION\"}" \
  "$BASE_URL/api/v1/feedback")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)

if [ "$HTTP_CODE" = "200" ]; then
  echo "✅ Feedback recorded!"
  echo "Your coach will take this into account for future recommendations."
else
  echo "Error submitting feedback. Please try again."
  exit 1
fi
