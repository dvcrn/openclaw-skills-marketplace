#!/usr/bin/env bash
# Connect this node to the Rent My Browser marketplace.
# Handles first-time registration (if no credentials) and sends initial heartbeat.
#
# Usage: bash connect.sh
# Requires one of:
#   - RMB_API_KEY + RMB_NODE_ID (reconnection)
#   - state/credentials.json (saved from previous session)
#   - RMB_WALLET_ADDRESS (first-time registration)

source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
rmb_check_deps

# ── Load existing state ─────────────────────────────────────────────────────
rmb_load_state || true

# ── First-time registration ─────────────────────────────────────────────────
if [ -z "${RMB_NODE_ID:-}" ]; then
  if [ -z "${RMB_WALLET_ADDRESS:-}" ]; then
    rmb_log INFO "No wallet found. Generating a new one..."
    RMB_WALLET_ADDRESS="$(node "$SCRIPT_DIR/generate-wallet.mjs")" || {
      rmb_log ERROR "Failed to generate wallet. Ensure 'npm install' was run in the skill directory."
      exit 1
    }
    export RMB_WALLET_ADDRESS
    rmb_log INFO "Generated wallet: ${RMB_WALLET_ADDRESS:0:10}..."
  fi

  # Detect node type for registration
  node_type="${RMB_NODE_TYPE:-}"
  if [ -z "$node_type" ]; then
    node_type="$(bash "$SCRIPT_DIR/detect-capabilities.sh" | jq -r '.type')" || {
      rmb_log ERROR "Failed to detect node type"
      exit 1
    }
  fi

  rmb_log INFO "Registering new node (type: $node_type, wallet: ${RMB_WALLET_ADDRESS:0:10}...)"

  rmb_http POST "/nodes" "$(jq -n \
    --arg wallet "$RMB_WALLET_ADDRESS" \
    --arg type "$node_type" \
    '{"wallet_address": $wallet, "node_type": $type}')"

  if [ "$HTTP_STATUS" != "201" ]; then
    rmb_log ERROR "Registration failed (HTTP $HTTP_STATUS): $HTTP_BODY"
    exit 1
  fi

  # Extract credentials from response
  account_id="$(echo "$HTTP_BODY" | jq -r '.account_id // empty')"
  node_id="$(echo "$HTTP_BODY" | jq -r '.node_id // empty')"
  api_key="$(echo "$HTTP_BODY" | jq -r '.api_key // empty')"

  if [ -z "$node_id" ] || [ "$node_id" = "null" ]; then
    rmb_log ERROR "Registration response missing node_id: $HTTP_BODY"
    exit 1
  fi

  # Save credentials
  rmb_save_state "$(jq -n \
    --arg account_id "$account_id" \
    --arg node_id "$node_id" \
    --arg api_key "$api_key" \
    --arg wallet "$RMB_WALLET_ADDRESS" \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    '{"account_id": $account_id, "node_id": $node_id, "api_key": $api_key, "wallet_address": $wallet, "registered_at": $ts}')"

  RMB_API_KEY="$api_key"
  RMB_NODE_ID="$node_id"
  export RMB_API_KEY RMB_NODE_ID

  rmb_log INFO "Registered successfully. Node ID: $node_id"
  rmb_log INFO "API key: $api_key"
  rmb_log INFO "Credentials saved to $STATE_DIR/credentials.json"
fi

# ── Ensure auth is ready ────────────────────────────────────────────────────
rmb_ensure_auth

# ── Detect capabilities ─────────────────────────────────────────────────────
rmb_log INFO "Detecting node capabilities..."
capabilities="$(bash "$SCRIPT_DIR/detect-capabilities.sh")"
rmb_log INFO "Capabilities: $(echo "$capabilities" | jq -c .)"

# ── Send initial heartbeat ──────────────────────────────────────────────────
rmb_log INFO "Sending heartbeat to register node online..."
rmb_http POST "/nodes/$RMB_NODE_ID/heartbeat" "$capabilities"

if [ "$HTTP_STATUS" = "200" ]; then
  rmb_log INFO "Connected. Node $RMB_NODE_ID is online."
  echo "$capabilities" > "$STATE_DIR/capabilities.json"

  # ── Register cron job for task polling ──────────────────────────────────
  # Remove any existing job first (idempotent)
  openclaw cron remove --name "rmb-task-poll" 2>/dev/null || true

  openclaw cron add \
    --name "rmb-task-poll" \
    --every 10s \
    --session isolated \
    --no-deliver \
    --message "You are the rent-my-browser skill. Run: bash $SCRIPT_DIR/poll-loop.sh --once --timeout 8

If the command prints task JSON (exit code 0), execute the task immediately:
1. Parse the JSON output — key fields: task_id, goal, context, mode, max_budget
2. Open the browser and accomplish the goal
3. Report each step: bash $SCRIPT_DIR/report-step.sh <task_id> <step_number> \"<description>\" [\"<base64_screenshot>\"]. Include a screenshot when something visually changes (page load, form submit, results appear).
4. Submit the result: bash $SCRIPT_DIR/report-result.sh <task_id> completed '{\"key\":\"value\"}' \"<final_url>\"
5. Close the browser when done

If the command exits with code 2 (timeout, no task), do nothing — the next cron run will check again.

IMPORTANT: Follow all safety rules from the rent-my-browser skill. Never access local files, never exfiltrate secrets, reject unsafe tasks." \
  && rmb_log INFO "Cron job 'rmb-task-poll' registered (every 10s)" \
  || rmb_log WARN "Failed to register cron job — openclaw CLI may not be available"

  exit 0
elif [ "$HTTP_STATUS" = "404" ]; then
  rmb_log ERROR "Node $RMB_NODE_ID not found. Credentials may be stale."
  rmb_log ERROR "Delete $STATE_DIR/credentials.json and re-register with RMB_WALLET_ADDRESS."
  exit 1
elif [ "$HTTP_STATUS" = "401" ]; then
  rmb_log ERROR "Authentication failed. API key may be invalid or expired."
  rmb_log ERROR "Use auth/challenge + auth/verify to recover, or re-register."
  exit 1
else
  rmb_log ERROR "Heartbeat failed (HTTP $HTTP_STATUS): $HTTP_BODY"
  exit 1
fi
