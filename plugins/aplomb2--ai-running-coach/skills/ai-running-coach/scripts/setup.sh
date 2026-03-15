#!/bin/bash
# SECURITY MANIFEST:
# Environment variables accessed: ARC_API_TOKEN (only)
# External endpoints called: https://www.airunningcoach.net/api/v1/ (only)
# Local files read: ~/.config/ai-running-coach/config.json
# Local files written: ~/.config/ai-running-coach/config.json (setup only)
# AI Running Coach - Setup Script
# Connects your account by validating and storing your API token

CONFIG_DIR="$HOME/.config/ai-running-coach"
CONFIG_FILE="$CONFIG_DIR/config.json"
BASE_URL="https://www.airunningcoach.net"

echo "🏃 AI Running Coach - Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To get your API token:"
echo "1. Go to $BASE_URL"
echo "2. Log in and visit Profile → API Access"
echo "3. Generate a new token"
echo ""

read -p "Enter your API token: " TOKEN

if [ -z "$TOKEN" ]; then
  echo "Error: No token provided."
  exit 1
fi

# Validate token by calling the today endpoint
echo ""
echo "Validating token..."

RESPONSE=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/v1/today")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
  # Create config directory
  mkdir -p "$CONFIG_DIR"

  # Store config
  cat > "$CONFIG_FILE" << EOF
{
  "token": "$TOKEN",
  "base_url": "$BASE_URL"
}
EOF

  chmod 600 "$CONFIG_FILE"

  echo "✅ Token validated successfully!"
  echo "Config saved to $CONFIG_FILE"
  echo ""
  echo "You're all set! Try these commands:"
  echo "  today   - See today's workout"
  echo "  week    - View weekly plan"
  echo "  coach   - Ask your AI coach"
elif [ "$HTTP_CODE" = "401" ]; then
  echo "❌ Invalid token. Please check your token and try again."
  exit 1
else
  echo "❌ Connection error (HTTP $HTTP_CODE). Please try again later."
  exit 1
fi
