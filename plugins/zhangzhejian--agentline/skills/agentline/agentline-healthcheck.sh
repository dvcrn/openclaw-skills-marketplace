#!/usr/bin/env bash
# agentline-healthcheck.sh — Pre-flight health check for OpenClaw + Agentline integration.
#
# Usage:
#   agentline-healthcheck.sh [--agent <id>] [--hub <url>] [--openclaw-home <path>]
#
# Checks:
#   1. OpenClaw hooks configuration (hooks mapping, auth token, bind port)
#   2. Polling cron job (presence and frequency)
#   3. Webhook endpoint consistency (local network vs Hub-registered endpoint)

set -euo pipefail

# Ensure Homebrew and node are on PATH
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentline-common.sh"

# --- Parse args ---
AGENT_ID="" HUB_FLAG="" OC_HOME_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)       ag_help ;;
        --agent)         AGENT_ID="$2"; shift 2 ;;
        --hub)           HUB_FLAG="$2"; shift 2 ;;
        --openclaw-home) OC_HOME_FLAG="$2"; shift 2 ;;
        *)               ag_die "Unknown option: $1" ;;
    esac
done

# --- Output helpers ---
PASS=0
WARN=0
FAIL=0

print_header() {
    echo ""
    echo "========================================"
    echo "  $1"
    echo "========================================"
}

print_ok() {
    echo "  [OK]   $1"
    PASS=$((PASS + 1))
}

print_warn() {
    echo "  [WARN] $1"
    WARN=$((WARN + 1))
}

print_fail() {
    echo "  [FAIL] $1"
    FAIL=$((FAIL + 1))
}

print_info() {
    echo "  [INFO] $1"
}

# =============================================
# Version
# =============================================
AG_VERSION_FILE="${HOME}/.agentline/version"
if [[ -f "$AG_VERSION_FILE" ]]; then
    AG_VERSION="$(cat "$AG_VERSION_FILE")"
else
    AG_VERSION="unknown"
fi
echo ""
echo "  Agentline CLI v${AG_VERSION}"

# =============================================
# 0. Agentline Credentials
# =============================================
print_header "Agentline Credentials"

CREDS_LOADED=false
if ag_load_creds "$AGENT_ID" 2>/dev/null; then
    CREDS_LOADED=true
    ag_resolve_hub "$HUB_FLAG"
    print_ok "Credentials loaded for agent: ${AG_CRED_AGENT_ID}"
    print_info "Display name: ${AG_CRED_DISPLAY_NAME:-<not set>}"
    print_info "Hub URL: ${AG_HUB}"
    print_info "Key ID: ${AG_CRED_KEY_ID}"

    # Check token presence and expiry
    if [[ -n "${AG_CRED_TOKEN:-}" ]]; then
        if [[ -n "${AG_CRED_TOKEN_EXPIRES:-}" && "${AG_CRED_TOKEN_EXPIRES}" != "null" ]]; then
            NOW="$(date +%s)"
            if (( AG_CRED_TOKEN_EXPIRES > NOW )); then
                REMAINING=$(( AG_CRED_TOKEN_EXPIRES - NOW ))
                HOURS=$(( REMAINING / 3600 ))
                MINS=$(( (REMAINING % 3600) / 60 ))
                print_ok "JWT token valid (expires in ${HOURS}h ${MINS}m)"
            else
                print_fail "JWT token expired. Run: agentline-refresh.sh"
            fi
        else
            print_warn "JWT token present but no expiry recorded"
        fi
    else
        print_fail "No JWT token found. Run: agentline-register.sh or agentline-refresh.sh"
    fi
else
    print_fail "Cannot load agentline credentials. Run: agentline-register.sh --name <name> --set-default"
fi

# =============================================
# 1. OpenClaw Hooks Configuration
# =============================================
print_header "OpenClaw Hooks Configuration"

# --- Locate OpenClaw ---
# Priority: --openclaw-home flag > OPENCLAW_HOME env > `openclaw` CLI > default path
OC_HOME=""
if [[ -n "$OC_HOME_FLAG" ]]; then
    OC_HOME="$OC_HOME_FLAG"
    print_info "OpenClaw home (from --openclaw-home): ${OC_HOME}"
elif [[ -n "${OPENCLAW_HOME:-}" ]]; then
    OC_HOME="$OPENCLAW_HOME"
    print_info "OpenClaw home (from \$OPENCLAW_HOME): ${OC_HOME}"
elif command -v openclaw >/dev/null 2>&1; then
    # Try to get home dir from `openclaw config path` or infer from binary location
    OC_BIN="$(command -v openclaw)"
    print_ok "openclaw CLI found: ${OC_BIN}"
    # OpenClaw typically stores config in ~/.openclaw
    if OC_CFG_DIR="$(openclaw config path 2>/dev/null)"; then
        OC_HOME="$(dirname "$OC_CFG_DIR")"
    else
        OC_HOME="$HOME/.openclaw"
    fi
    print_info "OpenClaw home (from CLI): ${OC_HOME}"
else
    OC_HOME="$HOME/.openclaw"
    print_warn "openclaw CLI not found on PATH; using default: ${OC_HOME}"
fi

OC_CONFIG="${OC_HOME}/openclaw.json"

if [[ -f "$OC_CONFIG" ]]; then
    print_ok "OpenClaw config found: $OC_CONFIG"

    # --- Hooks enabled ---
    HOOKS_ENABLED="$(jq -r '.hooks.enabled // empty' "$OC_CONFIG" 2>/dev/null)" || true
    if [[ "$HOOKS_ENABLED" == "false" ]]; then
        print_fail "Hooks are disabled (.hooks.enabled = false)"
        print_info "Webhook delivery will not work until hooks are enabled"
    elif [[ "$HOOKS_ENABLED" == "true" ]]; then
        print_ok "Hooks are enabled"
    else
        print_info "Hooks enabled flag not set (defaults depend on OpenClaw version)"
    fi

    # --- Hooks base path ---
    HOOKS_PATH="$(jq -r '.hooks.path // empty' "$OC_CONFIG" 2>/dev/null)" || true
    if [[ -z "$HOOKS_PATH" ]]; then
        print_fail "Hooks base path not set (.hooks.path is missing)"
        print_info "Fix: set \"hooks.path\": \"/hooks\" in ${OC_CONFIG}"
    elif [[ "$HOOKS_PATH" == "/hooks" ]]; then
        print_ok "Hooks base path: ${HOOKS_PATH}"
    else
        print_fail "Hooks base path is '${HOOKS_PATH}' — must be '/hooks'"
        print_info "Fix: set \"hooks.path\": \"/hooks\" in ${OC_CONFIG}"
    fi

    # --- Hooks token ---
    HOOKS_TOKEN="$(jq -r '.hooks.token // empty' "$OC_CONFIG" 2>/dev/null)" || true
    if [[ -n "$HOOKS_TOKEN" ]]; then
        # Mask token for display (show first 8 chars)
        MASKED="${HOOKS_TOKEN:0:8}..."
        print_ok "Hooks auth token configured: ${MASKED}"
    else
        print_fail "Hooks auth token not set (.hooks.token is missing)"
        print_info "Webhook delivery will fail without a matching token"
    fi

    # --- allowRequestSessionKey ---
    ALLOW_REQ_SK="$(jq -r '.hooks.allowRequestSessionKey // empty' "$OC_CONFIG" 2>/dev/null)" || true
    if [[ "$ALLOW_REQ_SK" == "true" ]]; then
        print_ok "allowRequestSessionKey = true (Hub can specify session per message)"
    elif [[ "$ALLOW_REQ_SK" == "false" ]]; then
        print_fail "allowRequestSessionKey = false — Hub payload 包含 sessionKey，OpenClaw 将返回 400 拒绝投递"
        print_info "Fix: set \"hooks.allowRequestSessionKey\": true in ${OC_CONFIG}"
    else
        print_fail "allowRequestSessionKey 未设置（默认为 false）— Hub payload 包含 sessionKey，OpenClaw 将返回 400 拒绝投递"
        print_info "Fix: add \"hooks.allowRequestSessionKey\": true to .hooks in ${OC_CONFIG}"
    fi

    # --- allowedSessionKeyPrefixes ---
    SK_PREFIXES="$(jq -r '.hooks.allowedSessionKeyPrefixes // empty' "$OC_CONFIG" 2>/dev/null)" || true
    if [[ -n "$SK_PREFIXES" && "$SK_PREFIXES" != "null" ]]; then
        HAS_HOOK_PREFIX=false
        HAS_AG_PREFIX=false
        if jq -e '.hooks.allowedSessionKeyPrefixes | index("hook:")' "$OC_CONFIG" >/dev/null 2>&1; then
            HAS_HOOK_PREFIX=true
        fi
        if jq -e '.hooks.allowedSessionKeyPrefixes | index("agentline:")' "$OC_CONFIG" >/dev/null 2>&1; then
            HAS_AG_PREFIX=true
        fi

        # "hook:" is required by OpenClaw when defaultSessionKey is unset (gateway won't start without it)
        DEFAULT_SK_SET="$(jq -r '.hooks.defaultSessionKey // empty' "$OC_CONFIG" 2>/dev/null)" || true
        if [[ "$HAS_HOOK_PREFIX" != "true" && -z "$DEFAULT_SK_SET" ]]; then
            print_fail "allowedSessionKeyPrefixes 缺少 \"hook:\" — defaultSessionKey 未设置时 OpenClaw 要求必须包含 \"hook:\"，否则 gateway 无法启动"
            print_info "Fix: add \"hook:\" to .hooks.allowedSessionKeyPrefixes in ${OC_CONFIG}"
        elif [[ "$HAS_HOOK_PREFIX" == "true" ]]; then
            print_ok "allowedSessionKeyPrefixes 包含 \"hook:\""
        fi

        if [[ "$HAS_AG_PREFIX" == "true" ]]; then
            print_ok "allowedSessionKeyPrefixes 包含 \"agentline:\""
        else
            print_fail "allowedSessionKeyPrefixes 不包含 \"agentline:\" — Hub 生成的 session key 将被拒绝"
            print_info "Fix: add \"agentline:\" to .hooks.allowedSessionKeyPrefixes in ${OC_CONFIG}"
        fi
    else
        print_warn "allowedSessionKeyPrefixes 未设置（无前缀限制，任意来源均可指定 session key）"
        print_info "建议设置 \"hooks.allowedSessionKeyPrefixes\": [\"hook:\", \"agentline:\"] 以限制来源"
    fi

    # --- defaultSessionKey ---
    DEFAULT_SK="$(jq -r '.hooks.defaultSessionKey // empty' "$OC_CONFIG" 2>/dev/null)" || true
    if [[ -n "$DEFAULT_SK" ]]; then
        print_ok "defaultSessionKey: ${DEFAULT_SK}"
    else
        print_info "defaultSessionKey 未设置（可选，建议设为 \"agentline:default\" 作为回退会话）"
    fi

    # --- session.reset.mode ---
    SESSION_RESET_MODE="$(jq -r '.session.reset.mode // empty' "$OC_CONFIG" 2>/dev/null)" || true
    if [[ "$SESSION_RESET_MODE" == "never" ]]; then
        print_ok "session.reset.mode = never（会话不会自动重置）"
    elif [[ -n "$SESSION_RESET_MODE" ]]; then
        print_fail "session.reset.mode = \"${SESSION_RESET_MODE}\" — OpenClaw 会定期重置会话（生成新 sessionId），导致 Agentline 聊天上下文断开"
        print_info "Fix: set \"session\": {\"reset\": {\"mode\": \"never\"}} in ${OC_CONFIG}"
    else
        print_fail "session.reset.mode 未设置（默认每天凌晨 4 点重置会话，生成新 sessionId，导致 Agentline 聊天上下文断开）"
        print_info "Fix: add \"session\": {\"reset\": {\"mode\": \"never\"}} to ${OC_CONFIG}"
    fi

    # --- Gateway port (where OpenClaw HTTP server listens) ---
    HOOKS_PORT="$(jq -r '.gateway.port // empty' "$OC_CONFIG" 2>/dev/null)" || true
    if [[ -n "$HOOKS_PORT" ]]; then
        print_ok "Gateway port: ${HOOKS_PORT}"

        # Check if the port is actually listening
        if command -v lsof >/dev/null 2>&1; then
            if lsof -iTCP:"$HOOKS_PORT" -sTCP:LISTEN -P -n >/dev/null 2>&1; then
                print_ok "Port ${HOOKS_PORT} is actively listening"
            else
                print_warn "Port ${HOOKS_PORT} is configured but nothing is listening"
                print_info "Is OpenClaw running? Start it to accept webhook deliveries"
            fi
        fi

        # Check bind address — does it allow external access?
        BIND_HOST="$(jq -r '.gateway.customBindHost // .gateway.bind // empty' "$OC_CONFIG" 2>/dev/null)" || true
        if [[ -n "$BIND_HOST" ]]; then
            case "$BIND_HOST" in
                localhost|127.0.0.1|::1)
                    print_warn "Bind address: ${BIND_HOST} (localhost only — external services cannot reach hooks)"
                    print_info "The Agentline Hub needs to deliver webhooks to this gateway."
                    print_info "Fix: set \"gateway.bind\" to \"lan\" or \"0.0.0.0\" in ${OC_CONFIG}"
                    ;;
                lan|0.0.0.0|::)
                    print_ok "Bind address: ${BIND_HOST} (allows external access)"
                    ;;
                *)
                    # Specific IP — could be external or internal, just info
                    print_ok "Bind address: ${BIND_HOST}"
                    ;;
            esac
        else
            print_warn "Bind address not set (.gateway.bind is missing)"
            print_info "If using default (localhost), external webhook delivery will not work"
            print_info "Fix: set \"gateway.bind\" to \"lan\" or \"0.0.0.0\" in ${OC_CONFIG}"
        fi
    else
        print_warn "Gateway port not set (.gateway.port)"
        print_info "OpenClaw may use a default port; check OpenClaw docs"
    fi

    # --- Hooks mappings ---
    HOOKS_MAPPINGS="$(jq -r '.hooks.mappings // empty' "$OC_CONFIG" 2>/dev/null)" || true
    if [[ -n "$HOOKS_MAPPINGS" && "$HOOKS_MAPPINGS" != "null" ]]; then
        MAPPING_COUNT="$(jq '.hooks.mappings | length' "$OC_CONFIG" 2>/dev/null)" || MAPPING_COUNT=0
        if [[ "$MAPPING_COUNT" -eq 0 ]]; then
            print_fail "Hooks mappings array is empty (.hooks.mappings = [])"
            print_info "Fix: add the required mappings to ${OC_CONFIG}:"
            cat <<'SNIPPET'
         "mappings": [
           {"id":"agentline-agent","match":{"path":"/agentgram_inbox/agent"},"action":"agent","messageTemplate":"[Agentline] {{message}}"},
           {"id":"agentline-wake","match":{"path":"/agentgram_inbox/wake"},"action":"wake","wakeMode":"now","textTemplate":"{{body}}"},
           {"id":"agentline-default","match":{"path":"/agentline_inbox"},"action":"agent","messageTemplate":"[Agentline] {{message}}"}
         ]
SNIPPET
        else
            print_ok "Hooks mappings configured: ${MAPPING_COUNT} route(s)"

            # Check for agentline-related mappings (agentgram_inbox/agent and agentgram_inbox/wake)
            HAS_AGENT_ROUTE=false
            HAS_WAKE_ROUTE=false
            AGENT_ACTION=""
            WAKE_ACTION=""

            MAPPING_TYPE="$(jq -r '.hooks.mappings | type' "$OC_CONFIG" 2>/dev/null)" || MAPPING_TYPE=""

            if [[ "$MAPPING_TYPE" == "array" ]]; then
                if jq -e '.hooks.mappings[] | select((.match.path // .path // .route // .url // "") | test("agentgram_inbox/agent"; "i"))' "$OC_CONFIG" >/dev/null 2>&1; then
                    HAS_AGENT_ROUTE=true
                    AGENT_ACTION="$(jq -r '[.hooks.mappings[] | select((.match.path // .path // .route // .url // "") | test("agentgram_inbox/agent"; "i"))][0].action // empty' "$OC_CONFIG" 2>/dev/null)" || true
                fi
                if jq -e '.hooks.mappings[] | select((.match.path // .path // .route // .url // "") | test("agentgram_inbox/wake"; "i"))' "$OC_CONFIG" >/dev/null 2>&1; then
                    HAS_WAKE_ROUTE=true
                    WAKE_ACTION="$(jq -r '[.hooks.mappings[] | select((.match.path // .path // .route // .url // "") | test("agentgram_inbox/wake"; "i"))][0].action // empty' "$OC_CONFIG" 2>/dev/null)" || true
                fi
            elif [[ "$MAPPING_TYPE" == "object" ]]; then
                if jq -e '.hooks.mappings | to_entries[] | select(.key | test("agentgram_inbox/agent"; "i"))' "$OC_CONFIG" >/dev/null 2>&1; then
                    HAS_AGENT_ROUTE=true
                fi
                if jq -e '.hooks.mappings | to_entries[] | select(.key | test("agentgram_inbox/wake"; "i"))' "$OC_CONFIG" >/dev/null 2>&1; then
                    HAS_WAKE_ROUTE=true
                fi
            fi

            if [[ "$HAS_AGENT_ROUTE" == "true" ]]; then
                print_ok "Route /agentgram_inbox/agent found (messages & receipts)"
                if [[ -n "$AGENT_ACTION" && "$AGENT_ACTION" != "agent" ]]; then
                    print_warn "/agentgram_inbox/agent mapping has action '${AGENT_ACTION}' — expected 'agent'"
                    print_info "Fix: set \"action\": \"agent\" on the /agentgram_inbox/agent mapping"
                fi
            else
                print_fail "No /agentgram_inbox/agent route found in hooks mappings"
                print_info "Fix: add this mapping to .hooks.mappings in ${OC_CONFIG}:"
                echo '         {"id":"agentline-agent","match":{"path":"/agentgram_inbox/agent"},"action":"agent","messageTemplate":"[Agentline] {{message}}"}'
            fi

            if [[ "$HAS_WAKE_ROUTE" == "true" ]]; then
                print_ok "Route /agentgram_inbox/wake found (notifications)"
                if [[ -n "$WAKE_ACTION" && "$WAKE_ACTION" != "wake" ]]; then
                    print_warn "/agentgram_inbox/wake mapping has action '${WAKE_ACTION}' — expected 'wake'"
                    print_info "Fix: set \"action\": \"wake\" on the /agentgram_inbox/wake mapping"
                fi
            else
                print_fail "No /agentgram_inbox/wake route found in hooks mappings"
                print_info "Fix: add this mapping to .hooks.mappings in ${OC_CONFIG}:"
                echo '         {"id":"agentline-wake","match":{"path":"/agentgram_inbox/wake"},"action":"wake","wakeMode":"now","textTemplate":"{{body}}"}'
            fi

            # Print all mappings for reference
            print_info "Mappings detail:"
            if [[ "$MAPPING_TYPE" == "array" ]]; then
                jq -r '.hooks.mappings[] | "         [\(.id // "?")] \(.match.path // "*") -> \(.action // "?")"' "$OC_CONFIG" 2>/dev/null || true
            elif [[ "$MAPPING_TYPE" == "object" ]]; then
                jq -r '.hooks.mappings | to_entries[] | "         \(.key) -> \(.value)"' "$OC_CONFIG" 2>/dev/null || true
            fi
        fi
    else
        print_fail "No hooks mappings configured (.hooks.mappings is missing or empty)"
        print_info "Without mappings, webhook messages won't route to agents"
        print_info "Fix: add a \"mappings\" array to .hooks in ${OC_CONFIG}:"
        cat <<'SNIPPET'
         "mappings": [
           {"id":"agentline-agent","match":{"path":"/agentgram_inbox/agent"},"action":"agent","messageTemplate":"[Agentline] {{message}}"},
           {"id":"agentline-wake","match":{"path":"/agentgram_inbox/wake"},"action":"wake","wakeMode":"now","textTemplate":"{{body}}"},
           {"id":"agentline-default","match":{"path":"/agentline_inbox"},"action":"agent","messageTemplate":"[Agentline] {{message}}"}
         ]
SNIPPET
    fi
else
    print_fail "OpenClaw config not found: $OC_CONFIG"
    print_info "Install and configure OpenClaw first"
fi

# =============================================
# 2. Polling Cron Job
# =============================================
print_header "Polling Cron Job"

CRON_LINES=""
if CRON_LINES="$(crontab -l 2>/dev/null)"; then
    POLL_ENTRIES="$(grep -i 'agentline-poll' <<< "$CRON_LINES" 2>/dev/null)" || true

    if [[ -n "$POLL_ENTRIES" ]]; then
        ENTRY_COUNT="$(echo "$POLL_ENTRIES" | wc -l | tr -d ' ')"
        print_ok "Found ${ENTRY_COUNT} polling cron entry(ies)"

        while IFS= read -r entry; do
            # Skip comments
            [[ "$entry" =~ ^[[:space:]]*# ]] && continue

            print_info "Entry: $entry"

            # Extract schedule (first 5 fields)
            SCHED="$(awk '{print $1, $2, $3, $4, $5}' <<< "$entry")"

            case "$SCHED" in
                "* * * * *")
                    print_ok "Polling frequency: every 1 minute"
                    ;;
                "*/2 * * * *")
                    print_ok "Polling frequency: every 2 minutes"
                    ;;
                "*/5 * * * *")
                    print_warn "Polling frequency: every 5 minutes (messages may be delayed)"
                    ;;
                *)
                    print_info "Polling schedule: ${SCHED}"
                    ;;
            esac

            # Check if --openclaw-agent is specified
            if [[ "$entry" == *"--openclaw-agent"* ]]; then
                OC_AGENT="$(echo "$entry" | grep -oP '(?<=--openclaw-agent\s)\S+' 2>/dev/null || echo "$entry" | sed -n 's/.*--openclaw-agent[[:space:]]\+\([^[:space:]]*\).*/\1/p')"
                print_ok "OpenClaw agent specified: ${OC_AGENT:-<parsed value>}"
            else
                print_warn "No --openclaw-agent specified (will use default OpenClaw agent)"
            fi
        done <<< "$POLL_ENTRIES"
    else
        print_warn "No agentline-poll cron job found"
        print_info "Set up polling with:"
        print_info '  (crontab -l 2>/dev/null; echo "* * * * * $HOME/.agentline/bin/agentline-poll.sh 2>&1") | crontab -'
    fi
else
    print_warn "No crontab configured for current user"
    print_info "Set up polling with:"
    print_info '  (crontab -l 2>/dev/null; echo "* * * * * $HOME/.agentline/bin/agentline-poll.sh 2>&1") | crontab -'
fi

# Check auth lockfile (indicates recent auth failure)
AUTH_LOCK="${AG_DIR}/.poll-auth-lock"
if [[ -f "$AUTH_LOCK" ]]; then
    LOCK_TS="$(cat "$AUTH_LOCK")"
    NOW="$(date +%s)"
    if (( NOW - LOCK_TS < 3600 )); then
        REMAINING=$(( 3600 - (NOW - LOCK_TS) ))
        print_fail "Polling is paused due to auth failure (lockout expires in $((REMAINING / 60))m)"
        print_info "Fix: run agentline-refresh.sh, then delete ${AUTH_LOCK}"
    else
        print_warn "Stale auth lockfile found (expired). It will be cleared on next poll."
    fi
fi

# =============================================
# 3. Webhook Endpoint Consistency
# =============================================
print_header "Webhook Endpoint"

HAS_WEBHOOK=false

if [[ "$CREDS_LOADED" == "true" ]]; then
    # Fetch registered endpoint from Hub (also verifies Hub connectivity)
    ag_curl GET "${AG_HUB}/registry/resolve/${AG_CRED_AGENT_ID}"

    if [[ "$AG_HTTP_CODE" =~ ^2 ]]; then
        print_ok "Hub is reachable at ${AG_HUB}"

        # resolve API returns { agent_id, display_name, has_endpoint, endpoints }
        HAS_EP="$(jq -r '.has_endpoint // false' <<< "$AG_HTTP_BODY" 2>/dev/null)" || HAS_EP="false"

        if [[ "$HAS_EP" == "true" ]]; then
            HAS_WEBHOOK=true
            EP_URL="$(jq -r '.endpoints[]?.url // empty' <<< "$AG_HTTP_BODY" 2>/dev/null)" || EP_URL=""
            EP_STATE="$(jq -r '.endpoints[]?.state // empty' <<< "$AG_HTTP_BODY" 2>/dev/null)" || EP_STATE=""
            if [[ -n "$EP_URL" ]]; then
                print_ok "Webhook endpoint registered: ${EP_URL}"
            else
                print_ok "Webhook endpoint registered on Hub (has_endpoint: true)"
            fi
            if [[ -n "$EP_STATE" ]]; then
                case "$EP_STATE" in
                    active)
                        print_ok "Endpoint state: active"
                        ;;
                    unverified)
                        print_warn "Endpoint state: unverified (probe failed during registration)"
                        print_info "Re-register endpoint after fixing connectivity: POST /registry/agents/{agent_id}/endpoints"
                        print_info "Use POST /registry/agents/{agent_id}/endpoints/test to diagnose"
                        ;;
                    unreachable)
                        print_fail "Endpoint state: unreachable (delivery failures exceeded TTL)"
                        print_info "Re-register endpoint: POST /registry/agents/{agent_id}/endpoints"
                        ;;
                    *)
                        print_info "Endpoint state: ${EP_STATE}"
                        ;;
                esac
            fi
        else
            print_info "No webhook endpoint registered (using polling mode only)"
            print_info "This is fine if you have a polling cron job set up"
        fi

        # --- Endpoint status dashboard (requires JWT) ---
        if [[ -n "${AG_CRED_TOKEN:-}" ]]; then
            ag_curl GET "${AG_HUB}/registry/agents/${AG_CRED_AGENT_ID}/endpoints/status" \
                "Authorization: Bearer ${AG_CRED_TOKEN}"

            if [[ "$AG_HTTP_CODE" =~ ^2 ]]; then
                STATUS_STATE="$(jq -r '.state // empty' <<< "$AG_HTTP_BODY" 2>/dev/null)" || STATUS_STATE=""
                QUEUED="$(jq -r '.queued_message_count // 0' <<< "$AG_HTTP_BODY" 2>/dev/null)" || QUEUED=0
                FAILED="$(jq -r '.failed_message_count // 0' <<< "$AG_HTTP_BODY" 2>/dev/null)" || FAILED=0
                LAST_ERR="$(jq -r '.last_delivery_error // empty' <<< "$AG_HTTP_BODY" 2>/dev/null)" || LAST_ERR=""

                print_info "Queued messages: ${QUEUED}"
                if [[ "$FAILED" -gt 0 ]]; then
                    print_warn "Failed messages (24h): ${FAILED}"
                else
                    print_ok "Failed messages (24h): 0"
                fi
                if [[ -n "$LAST_ERR" && "$LAST_ERR" != "null" ]]; then
                    print_warn "Last delivery error: ${LAST_ERR}"
                fi
            elif [[ "$AG_HTTP_CODE" == "404" ]]; then
                print_info "No endpoint registered (status endpoint returned 404)"
            fi
        fi
    else
        print_fail "Cannot resolve agent from Hub (HTTP ${AG_HTTP_CODE})"
        print_info "Hub may be unreachable or agent not registered"
    fi
else
    print_warn "Skipped — credentials not loaded"
fi

# --- Cross-check: neither webhook nor polling ---
HAS_POLLING=false
if [[ -n "${POLL_ENTRIES:-}" ]]; then
    HAS_POLLING=true
fi

if [[ "$HAS_WEBHOOK" == "false" && "$HAS_POLLING" == "false" ]]; then
    echo ""
    print_fail "Neither webhook nor polling is configured — agent CANNOT receive messages"
    print_info "Set up at least one: cron polling (step 4) or webhook endpoint (step 6)"
fi

# =============================================
# Summary
# =============================================
print_header "Summary"
TOTAL=$((PASS + WARN + FAIL))
echo "  Passed: ${PASS}  |  Warnings: ${WARN}  |  Failed: ${FAIL}  |  Total: ${TOTAL}"
echo ""

if [[ "$FAIL" -gt 0 ]]; then
    echo "  Some checks FAILED. Please fix the issues above before using Agentline."
    exit 1
elif [[ "$WARN" -gt 0 ]]; then
    echo "  All critical checks passed, but there are warnings to review."
    exit 0
else
    echo "  All checks passed. Agentline is ready to use!"
    exit 0
fi
