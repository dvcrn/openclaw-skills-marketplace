#!/usr/bin/env bash
# agentline-send.sh — Construct a signed message envelope and send it.
#
# Usage: agentline-send.sh --to <agent_id> [--text <msg>] [--payload '{...}']
#        [--payload-file path] [--reply-to <msg_id>] [--ttl <sec>]
#        [--topic <topic>] [--agent <id>] [--hub <url>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentline-common.sh"

# --- Parse args ---
TO="" TEXT="" PAYLOAD="" PAYLOAD_FILE=""
REPLY_TO="" TTL="3600" TOPIC="" AGENT_ID="" HUB_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)      ag_help ;;
        --to)           TO="$2"; shift 2 ;;
        --text)         TEXT="$2"; shift 2 ;;
        --payload)      PAYLOAD="$2"; shift 2 ;;
        --payload-file) PAYLOAD_FILE="$2"; shift 2 ;;
        --reply-to)     REPLY_TO="$2"; shift 2 ;;
        --ttl)          TTL="$2"; shift 2 ;;
        --topic)        TOPIC="$2"; shift 2 ;;
        --agent)        AGENT_ID="$2"; shift 2 ;;
        --hub)          HUB_FLAG="$2"; shift 2 ;;
        *) ag_die "Unknown option: $1" ;;
    esac
done

[[ -n "$TO" ]] || ag_die "Usage: agentline-send.sh --to <agent_id> [--text <msg>|--payload '{...}'|--payload-file path] [--topic <topic>]"

ag_load_creds "$AGENT_ID"
ag_resolve_hub "$HUB_FLAG"

aid="${AG_CRED_AGENT_ID}"
token="${AG_CRED_TOKEN}"
key_id="${AG_CRED_KEY_ID}"
priv_key="${AG_CRED_PRIVATE_KEY}"
[[ -n "$token" ]] || ag_die "No token in credentials. Register or refresh first."

# --- Build payload ---
if [[ -n "$TEXT" ]]; then
    payload="$(jq -n --arg text "$TEXT" '{text: $text}')"
elif [[ -n "$PAYLOAD" ]]; then
    payload="$PAYLOAD"
elif [[ -n "$PAYLOAD_FILE" ]]; then
    payload="$(cat "$PAYLOAD_FILE")"
else
    ag_die "Must provide --text, --payload, or --payload-file"
fi

# Validate payload is JSON
jq empty <<< "$payload" 2>/dev/null || ag_die "Payload is not valid JSON"

# --- Compute payload hash ---
ph_json="$(echo "$payload" | ag_crypto payload-hash)"
payload_hash="$(jq -r '.payload_hash' <<< "$ph_json")"

# --- Generate envelope fields ---
msg_id="$(ag_uuid)"
ts="$(ag_ts)"

# --- Sign envelope ---
sign_input="$(jq -n \
    --arg private_key "$priv_key" \
    --arg key_id "$key_id" \
    --arg v "a2a/0.1" \
    --arg msg_id "$msg_id" \
    --argjson ts "$ts" \
    --arg from "$aid" \
    --arg to "$TO" \
    --arg type "message" \
    --arg reply_to "$REPLY_TO" \
    --argjson ttl_sec "$TTL" \
    --arg payload_hash "$payload_hash" \
    '{
        private_key: $private_key,
        key_id: $key_id,
        v: $v,
        msg_id: $msg_id,
        ts: $ts,
        from: $from,
        to: $to,
        type: $type,
        reply_to: $reply_to,
        ttl_sec: $ttl_sec,
        payload_hash: $payload_hash
    }')"

sig_json="$(echo "$sign_input" | ag_crypto sign-envelope)"

# --- Build full envelope ---
envelope="$(jq -n \
    --arg v "a2a/0.1" \
    --arg msg_id "$msg_id" \
    --argjson ts "$ts" \
    --arg from "$aid" \
    --arg to "$TO" \
    --arg type "message" \
    --arg reply_to "$REPLY_TO" \
    --argjson ttl_sec "$TTL" \
    --argjson payload "$payload" \
    --arg payload_hash "$payload_hash" \
    --argjson sig "$sig_json" \
    '{
        v: $v,
        msg_id: $msg_id,
        ts: $ts,
        from: $from,
        to: $to,
        type: $type,
        reply_to: (if $reply_to == "" then null else $reply_to end),
        ttl_sec: $ttl_sec,
        payload: $payload,
        payload_hash: $payload_hash,
        sig: $sig
    }')"

# --- Send ---
send_url="${AG_HUB}/hub/send"
if [[ -n "$TOPIC" ]]; then
    encoded_topic="$(node -e "console.log(encodeURIComponent(process.argv[1]))" "$TOPIC")"
    send_url="${send_url}?topic=${encoded_topic}"
fi
ag_curl_auth POST "$send_url" "$token" "$envelope"
ag_check_http 2

# Include msg_id in output for status tracking
jq --arg msg_id "$msg_id" '. + {msg_id: $msg_id}' <<< "$AG_HTTP_BODY"
