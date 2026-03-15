#!/bin/bash
# SECURITY MANIFEST:
# Environment variables accessed: ARC_API_TOKEN (only)
# External endpoints called: https://www.airunningcoach.net/api/v1/ (only)
# Local files read: ~/.config/ai-running-coach/config.json
# Local files written: ~/.config/ai-running-coach/config.json (setup only)
# AI Running Coach - Today's Workout

CONFIG_FILE="$HOME/.config/ai-running-coach/config.json"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "Not set up yet. Run the setup command first."
  exit 1
fi

TOKEN=$(cat "$CONFIG_FILE" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
BASE_URL=$(cat "$CONFIG_FILE" | grep -o '"base_url":"[^"]*"' | cut -d'"' -f4)

RESPONSE=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/today")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
  echo "Error fetching today's workout. Please check your connection or re-run setup."
  exit 1
fi

# Parse JSON response
DATE=$(echo "$BODY" | grep -o '"date":"[^"]*"' | cut -d'"' -f4)
DAY=$(echo "$BODY" | grep -o '"dayOfWeek":"[^"]*"' | cut -d'"' -f4)
TYPE=$(echo "$BODY" | grep -o '"workoutType":"[^"]*"' | cut -d'"' -f4)
DISTANCE=$(echo "$BODY" | grep -o '"distance":"[^"]*"' | cut -d'"' -f4)
DURATION=$(echo "$BODY" | grep -o '"duration":"[^"]*"' | cut -d'"' -f4)
PACE=$(echo "$BODY" | grep -o '"pace":"[^"]*"' | cut -d'"' -f4)
INTENSITY=$(echo "$BODY" | grep -o '"intensity":"[^"]*"' | cut -d'"' -f4)
DESCRIPTION=$(echo "$BODY" | grep -o '"description":"[^"]*"' | cut -d'"' -f4)
REST=$(echo "$BODY" | grep -o '"isRestDay":true')
COMPLETED=$(echo "$BODY" | grep -o '"completed":true')

echo "🏃 Today's Workout — $DAY, $DATE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -n "$REST" ]; then
  echo "😴 Rest Day"
  echo "Take it easy and recover!"
else
  echo "Type: $TYPE"
  [ -n "$DISTANCE" ] && echo "Distance: $DISTANCE"
  [ -n "$DURATION" ] && echo "Duration: $DURATION"
  [ -n "$PACE" ] && echo "Pace: $PACE"
  [ -n "$INTENSITY" ] && echo "Intensity: $INTENSITY"
  [ -n "$DESCRIPTION" ] && echo ""
  [ -n "$DESCRIPTION" ] && echo "$DESCRIPTION"

  if [ -n "$COMPLETED" ]; then
    echo ""
    echo "✅ Already completed!"
  fi
fi
