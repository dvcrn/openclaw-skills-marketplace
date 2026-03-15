#!/usr/bin/env bash
# agentline-poll.sh — Poll inbox, trigger OpenClaw, and send reply back.
#
# Usage:
#   agentline-poll.sh [--agent <id>] [--hub <url>] [--openclaw-agent <agent>]
#
# Options:
#   --agent <id>            Agentline agent credentials to use
#   --hub <url>             Agentline Hub URL override
#   --openclaw-agent <agent> OpenClaw agent id to handle incoming messages
#                           NOTE: This is the agent *id* (e.g. "main"), not the
#                           identity name (e.g. "Jarvis"). Run `openclaw agents list`
#                           to see available ids.
#
# Designed to run as a cron job:
#   * * * * * ~/.agentline/bin/agentline-poll.sh 2>&1

set -euo pipefail

# Ensure Homebrew and node are on PATH (cron has a minimal PATH)
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentline-common.sh"

# --- Parse args ---
AGENT_ID="" HUB_FLAG="" OPENCLAW_AGENT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)        ag_help ;;
        --agent)          AGENT_ID="$2"; shift 2 ;;
        --hub)            HUB_FLAG="$2"; shift 2 ;;
        --openclaw-agent) OPENCLAW_AGENT="$2"; shift 2 ;;
        *)                ag_die "Unknown option: $1" ;;
    esac
done

ag_load_creds "$AGENT_ID"
ag_resolve_hub "$HUB_FLAG"

token="${AG_CRED_TOKEN}"
[[ -n "$token" ]] || ag_die "No token in credentials. Register or refresh first."

LOG="${AG_DIR}/inbox.log"
ERR_LOG="${AG_DIR}/poll-errors.log"

# --- Auth failure lockfile: skip polling if token is unrecoverable ---
AUTH_LOCK="${AG_DIR}/.poll-auth-lock"
if [[ -f "$AUTH_LOCK" ]]; then
    lock_ts="$(cat "$AUTH_LOCK")"
    now="$(date +%s)"
    # Lock expires after 1 hour — allow retry then
    if (( now - lock_ts < 3600 )); then
        exit 0
    fi
    rm -f "$AUTH_LOCK"
fi

# --- Poll inbox (ack=true so messages won't repeat) ---
ag_curl_auth GET "${AG_HUB}/hub/inbox?limit=10&ack=true" "$token"

# On 401, try auto-refresh before giving up
if [[ "$AG_HTTP_CODE" == "401" ]]; then
    if "${SCRIPT_DIR}/agentline-refresh.sh" 2>/dev/null; then
        # Reload refreshed token
        ag_load_creds "$AGENT_ID"
        token="${AG_CRED_TOKEN}"
        ag_curl_auth GET "${AG_HUB}/hub/inbox?limit=10&ack=true" "$token"
    fi
    # If still 401 after refresh, lock out further polls
    if [[ "$AG_HTTP_CODE" == "401" ]]; then
        date +%s > "$AUTH_LOCK"
        ag_die "Auth failed after refresh attempt. Polling paused for 1 hour. Run agentline-refresh.sh manually."
    fi
fi

ag_check_http 2

RESP="$AG_HTTP_BODY"
COUNT="$(jq -r '.count' <<< "$RESP")"

# Silent exit if no new messages
[[ "$COUNT" -gt 0 ]] || exit 0

# Log poll summary
echo "[$(date -Iseconds)] POLL_RECEIVED count=${COUNT}" >> "$LOG"

# --- Process each message ---
# This script is a thin transport bridge — zero business logic.
# Message content comes from the server's build_flat_text() via the `text` field,
# identical to what webhook delivers.  The script only decides:
#   1. action: agent (message) vs wake (contact_request/response/removed)
#   2. session: --group-id (room) vs --session-id (DM)
jq -c '.messages[]' <<< "$RESP" | while read -r MSG_OBJ; do
    FLAT_TEXT="$(jq -r '.text // empty' <<< "$MSG_OBJ")"
    ROOM_ID="$(jq -r '.room_id // empty' <<< "$MSG_OBJ")"

    ENV="$(jq -c '.envelope' <<< "$MSG_OBJ")"
    FROM="$(jq -r '.from' <<< "$ENV")"
    MSG_ID="$(jq -r '.msg_id' <<< "$ENV")"
    TYPE="$(jq -r '.type' <<< "$ENV")"

    [[ -z "$FLAT_TEXT" ]] && continue

    echo "[$(date -Iseconds)] MSG_IN type=${TYPE} from=${FROM} msg_id=${MSG_ID}" >> "$LOG"

    case "$TYPE" in
        contact_request|contact_request_response|contact_removed)
            # Wake path — mirrors /agentgram_inbox/wake webhook mapping
            OC_ARGS=(system event --text "[Agentline] ${FLAT_TEXT}" --mode now)
            [[ -n "$OPENCLAW_AGENT" ]] && OC_ARGS+=(--agent "$OPENCLAW_AGENT")
            if openclaw "${OC_ARGS[@]}" 2>/dev/null; then
                echo "[$(date -Iseconds)] WAKE_SENT type=${TYPE} from=${FROM}" >> "$LOG"
            else
                echo "[$(date -Iseconds)] WAKE_FAILED type=${TYPE} from=${FROM}" >> "$ERR_LOG"
            fi
            ;;
        message)
            # Agent path — mirrors /agentgram_inbox/agent webhook mapping
            OC_ARGS=(agent --message "[Agentline] ${FLAT_TEXT}" --thinking low --json)
            [[ -n "$OPENCLAW_AGENT" ]] && OC_ARGS+=(--agent "$OPENCLAW_AGENT")

            # Forward agent reply back to sender
            AGENT_OUT=""
            if AGENT_OUT="$(openclaw "${OC_ARGS[@]}" 2>/dev/null)"; then
                REPLY_TEXT="$(jq -r '.text // .message // .response // .content // empty' <<< "$AGENT_OUT" 2>/dev/null)" || true
                [[ -z "$REPLY_TEXT" && -n "$AGENT_OUT" ]] && ! jq empty <<< "$AGENT_OUT" 2>/dev/null && REPLY_TEXT="$AGENT_OUT"
                if [[ -n "$REPLY_TEXT" ]]; then
                    if "${SCRIPT_DIR}/agentline-send.sh" --to "$FROM" --text "$REPLY_TEXT" --reply-to "$MSG_ID" 2>/dev/null; then
                        echo "[$(date -Iseconds)] REPLY_SENT to=${FROM} reply_to=${MSG_ID}" >> "$LOG"
                    else
                        echo "[$(date -Iseconds)] REPLY_FAILED to=${FROM}" >> "$ERR_LOG"
                    fi
                fi
            else
                echo "[$(date -Iseconds)] AGENT_FAILED from=${FROM} msg_id=${MSG_ID}" >> "$ERR_LOG"
            fi
            ;;
        *)
            continue
            ;;
    esac
done
