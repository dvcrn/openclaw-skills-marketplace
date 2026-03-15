#!/bin/bash
# SECURITY MANIFEST:
# Environment variables accessed: ARC_API_TOKEN (only)
# External endpoints called: https://www.airunningcoach.net/api/v1/ (only)
# Local files read: ~/.config/ai-running-coach/config.json
# Local files written: ~/.config/ai-running-coach/config.json (setup only)
# AI Running Coach - Training Statistics

CONFIG_FILE="$HOME/.config/ai-running-coach/config.json"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "Not set up yet. Run the setup command first."
  exit 1
fi

TOKEN=$(cat "$CONFIG_FILE" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
BASE_URL=$(cat "$CONFIG_FILE" | grep -o '"base_url":"[^"]*"' | cut -d'"' -f4)

RESPONSE=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/stats")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
  echo "Error fetching stats. Please check your connection or re-run setup."
  exit 1
fi

TOTAL_WORKOUTS=$(echo "$BODY" | grep -o '"totalWorkouts":[0-9]*' | cut -d':' -f2)
TOTAL_DISTANCE=$(echo "$BODY" | grep -o '"totalDistance":[0-9.]*' | cut -d':' -f2)
TOTAL_DURATION=$(echo "$BODY" | grep -o '"totalDuration":[0-9.]*' | cut -d':' -f2)
STREAK=$(echo "$BODY" | grep -o '"currentStreak":[0-9]*' | cut -d':' -f2)
COMPLETION=$(echo "$BODY" | grep -o '"completionRate":[0-9.]*' | cut -d':' -f2)

echo "📊 Training Statistics"
echo "━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Total Workouts: ${TOTAL_WORKOUTS:-0}"
echo "Total Distance: ${TOTAL_DISTANCE:-0} km"
echo "Total Duration: ${TOTAL_DURATION:-0} min"
echo "Current Streak: ${STREAK:-0} days 🔥"
echo "Completion Rate: ${COMPLETION:-0}%"
