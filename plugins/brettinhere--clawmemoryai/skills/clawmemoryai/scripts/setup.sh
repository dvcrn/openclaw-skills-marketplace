#!/usr/bin/env bash
# ClawMemory Hub — First-time setup
# Usage: bash setup.sh

set -e

CONFIG_DIR="${HOME}/.clawmemoryai"
CONFIG_FILE="$CONFIG_DIR/config.json"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   ClawMemory Hub — Setup             ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Get your API key at: https://clawmemory.ai/settings/api-keys"
echo ""

read -p "API Key (sk_...): " API_KEY
read -p "Your username: " USERNAME
read -p "Base URL [https://clawmemory.ai]: " BASE_URL
BASE_URL="${BASE_URL:-https://clawmemory.ai}"

mkdir -p "$CONFIG_DIR"
cat > "$CONFIG_FILE" << EOF
{
  "baseUrl": "$BASE_URL",
  "apiKey": "$API_KEY",
  "defaultUser": "$USERNAME"
}
EOF

chmod 600 "$CONFIG_FILE"
echo ""
echo "✅ Config saved to $CONFIG_FILE"

# Verify connection
echo "🔄 Verifying connection..."
RESULT=$(curl -s -H "Authorization: Bearer $API_KEY" "$BASE_URL/api/v1/user")
if echo "$RESULT" | grep -q '"username"'; then
  USER=$(echo "$RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['data']['username'])")
  echo "✅ Connected as: $USER"
else
  echo "⚠️  Could not verify — check your API key"
  echo "   Response: $RESULT"
fi
echo ""
echo "Done! Use: bash $(dirname "$0")/cm.sh help"
