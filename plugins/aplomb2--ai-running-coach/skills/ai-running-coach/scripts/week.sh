#!/bin/bash
# SECURITY MANIFEST:
# Environment variables accessed: ARC_API_TOKEN (only)
# External endpoints called: https://www.airunningcoach.net/api/v1/ (only)
# Local files read: ~/.config/ai-running-coach/config.json
# Local files written: ~/.config/ai-running-coach/config.json (setup only)
# AI Running Coach - Weekly Plan

CONFIG_FILE="$HOME/.config/ai-running-coach/config.json"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "Not set up yet. Run the setup command first."
  exit 1
fi

TOKEN=$(cat "$CONFIG_FILE" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
BASE_URL=$(cat "$CONFIG_FILE" | grep -o '"base_url":"[^"]*"' | cut -d'"' -f4)

RESPONSE=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/week")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
  echo "Error fetching weekly plan. Please check your connection or re-run setup."
  exit 1
fi

WEEK_NUM=$(echo "$BODY" | grep -o '"weekNumber":[0-9]*' | cut -d':' -f2)
PLAN_NAME=$(echo "$BODY" | grep -o '"planName":"[^"]*"' | cut -d'"' -f4)

echo "🗓 Weekly Plan — Week $WEEK_NUM"
[ -n "$PLAN_NAME" ] && echo "$PLAN_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Use jq if available for better parsing, otherwise basic parsing
if command -v jq &> /dev/null; then
  echo "$BODY" | jq -r '.days[] |
    if .isRestDay then
      "\(.dayOfWeek): 😴 Rest Day"
    else
      "\(.dayOfWeek): \(.workoutType // "workout")" +
      (if .distance then " — \(.distance)" else "" end) +
      (if .completed then " ✅" else "" end)
    end'
else
  # Basic parsing without jq - extract day entries
  echo "$BODY" | grep -o '"dayOfWeek":"[^"]*"' | cut -d'"' -f4 | while read -r DAY; do
    echo "  $DAY"
  done
  echo ""
  echo "(Install jq for better formatting)"
fi
