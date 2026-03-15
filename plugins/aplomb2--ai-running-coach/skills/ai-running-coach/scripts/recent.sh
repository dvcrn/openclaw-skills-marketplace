#!/bin/bash
# SECURITY MANIFEST:
# Environment variables accessed: ARC_API_TOKEN (only)
# External endpoints called: https://www.airunningcoach.net/api/v1/ (only)
# Local files read: ~/.config/ai-running-coach/config.json
# Local files written: ~/.config/ai-running-coach/config.json (setup only)
# AI Running Coach - Recent Strava Activities

CONFIG_FILE="$HOME/.config/ai-running-coach/config.json"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "Not set up yet. Run the setup command first."
  exit 1
fi

TOKEN=$(cat "$CONFIG_FILE" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
BASE_URL=$(cat "$CONFIG_FILE" | grep -o '"base_url":"[^"]*"' | cut -d'"' -f4)

RESPONSE=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/strava/recent")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
  ERROR=$(echo "$BODY" | grep -o '"error":"[^"]*"' | cut -d'"' -f4)
  if [ -n "$ERROR" ]; then
    echo "$ERROR"
  else
    echo "Error fetching Strava activities. Is your Strava account connected?"
  fi
  exit 1
fi

echo "🏃 Recent Strava Activities"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if command -v jq &> /dev/null; then
  echo "$BODY" | jq -r '.activities[] |
    "📅 \(.date) — \(.workoutType // "run")\n   Distance: \(.distance) | Duration: \(.duration) | Pace: \(.pace)\n   \(.analysis // "")\n"'
else
  echo "$BODY" | grep -o '"date":"[^"]*"' | cut -d'"' -f4 | while read -r DATE; do
    echo "📅 $DATE"
  done
  echo ""
  echo "(Install jq for better formatting)"
fi
