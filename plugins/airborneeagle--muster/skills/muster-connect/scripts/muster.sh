#!/usr/bin/env bash
# muster.sh — Quick Muster MCP helper for agents
# Usage: bash muster.sh <command> [args]
#
# Environment variables:
#   MUSTER_URL        — Muster base URL (default: http://localhost:3000)
#   MUSTER_API_KEY    — Your agent API key (or set via MUSTER_KEYCHAIN_* below)
#   MUSTER_STATE_FILE — Path to agent state JSON (default: ~/.muster/state.json)
#
# macOS Keychain (optional): set MUSTER_KEYCHAIN_ACCOUNT and MUSTER_KEYCHAIN_SERVICE
#   to load the API key from Keychain automatically.
#
# Commands:
#   heartbeat [status]    — Check in (status: idle|working|reflecting|error)
#   tasks                 — List open tasks from REST API
#   status                — Show agent record from Muster
#   register              — Register this agent (first-time only, prompts for details)

set -euo pipefail

MUSTER_URL="${MUSTER_URL:-http://localhost:3000}"
STATE_FILE="${MUSTER_STATE_FILE:-$HOME/.muster/state.json}"

# Load API key — env var takes precedence, then macOS Keychain if configured
if [[ -z "${MUSTER_API_KEY:-}" ]]; then
  KEYCHAIN_ACCOUNT="${MUSTER_KEYCHAIN_ACCOUNT:-}"
  KEYCHAIN_SERVICE="${MUSTER_KEYCHAIN_SERVICE:-}"
  if [[ -n "$KEYCHAIN_ACCOUNT" && -n "$KEYCHAIN_SERVICE" ]]; then
    MUSTER_API_KEY=$(security find-generic-password -a "$KEYCHAIN_ACCOUNT" -s "$KEYCHAIN_SERVICE" -w 2>/dev/null || echo "")
  else
    MUSTER_API_KEY=""
  fi
fi

if [[ -z "$MUSTER_API_KEY" ]]; then
  echo '{"error": "Muster API key not found in Keychain. Run registration first."}'
  exit 1
fi

# Load agent ID from state file
if [[ -f "$STATE_FILE" ]]; then
  AGENT_ID=$(python3 -c "import json; print(json.load(open('$STATE_FILE'))['agent_id'])" 2>/dev/null || echo "")
else
  AGENT_ID=""
fi

mcp_call() {
  local tool="$1"
  local args="$2"
  curl -s -X POST "$MUSTER_URL/muster/mcp" \
    -H "Authorization: Bearer $MUSTER_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"jsonrpc\": \"2.0\",
      \"id\": 1,
      \"method\": \"tools/call\",
      \"params\": {
        \"name\": \"$tool\",
        \"arguments\": $args
      }
    }" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    # Unwrap MCP result content
    if 'result' in data and 'content' in data['result']:
        for item in data['result']['content']:
            if item.get('type') == 'text':
                try:
                    print(json.dumps(json.loads(item['text']), indent=2))
                except Exception:
                    print(item['text'])
    else:
        print(json.dumps(data, indent=2))
except Exception as e:
    print(sys.stdin.read())
"
}

CMD="${1:-heartbeat}"

case "$CMD" in
  heartbeat)
    STATUS="${2:-idle}"
    if [[ -z "$AGENT_ID" ]]; then
      echo '{"error": "No agent_id found. Run: bash muster.sh register"}'
      exit 1
    fi
    mcp_call "heartbeat" "{\"agent_id\": \"$AGENT_ID\", \"status\": \"$STATUS\"}"
    ;;

  tasks)
    curl -s "$MUSTER_URL/api/tasks" \
      -H "Authorization: Bearer $MUSTER_API_KEY" | python3 -m json.tool
    ;;

  status)
    if [[ -z "$AGENT_ID" ]]; then
      echo '{"error": "No agent_id found."}'
      exit 1
    fi
    curl -s "$MUSTER_URL/api/agents/$AGENT_ID" | python3 -m json.tool
    ;;

  register)
    echo "Registering agent with Muster at $MUSTER_URL"
    echo ""
    read -rp "Agent name (e.g. Silas): " REG_NAME
    read -rp "Agent title (e.g. Chief Operating Officer): " REG_TITLE
    read -rp "Slug (e.g. coo) [optional]: " REG_SLUG
    read -rp "Webhook URL [optional]: " REG_WEBHOOK
    read -rp "Runtime (e.g. openclaw, claude-code) [optional]: " REG_RUNTIME

    PAYLOAD=$(python3 -c "
import json, sys
d = {'name': '$REG_NAME', 'title': '$REG_TITLE'}
if '$REG_SLUG': d['slug'] = '$REG_SLUG'
if '$REG_WEBHOOK': d['webhookUrl'] = '$REG_WEBHOOK'
if '$REG_RUNTIME': d['runtime'] = '$REG_RUNTIME'
print(json.dumps(d))
")

    RESULT=$(curl -s -X POST "$MUSTER_URL/api/agents/register" \
      -H "Content-Type: application/json" \
      -d "$PAYLOAD")
    echo "$RESULT" | python3 -m json.tool

    API_KEY=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('apiKey',''))" 2>/dev/null || echo "")
    UUID=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('agent',{}).get('id',''))" 2>/dev/null || echo "")

    if [[ -n "$API_KEY" && -n "$UUID" ]]; then
      mkdir -p "$(dirname "$STATE_FILE")"
      echo "{\"agent_id\":\"$UUID\",\"slug\":\"$REG_SLUG\",\"registered_at\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" > "$STATE_FILE"
      echo ""
      echo "✅ Registered. agent_id=$UUID"
      echo "✅ State saved to $STATE_FILE"
      echo ""
      echo "⚠️  Store your API key securely — it will not be shown again:"
      echo "   $API_KEY"
      echo ""
      echo "   Set it for future use:"
      echo "   export MUSTER_API_KEY=\"$API_KEY\""
    else
      echo ""
      echo "⚠️  Could not parse response. Copy the apiKey and agent.id manually."
    fi
    ;;

  *)
    echo "Unknown command: $CMD"
    echo "Usage: bash muster.sh [heartbeat|tasks|status|register]"
    exit 1
    ;;
esac
