#!/usr/bin/env bash
# agentline-contact-request.sh — Manage contact requests (send, list, accept, reject).
#
# Usage:
#   agentline-contact-request.sh send     --to <agent_id> [--message <text>] [--agent <id>] [--hub <url>]
#   agentline-contact-request.sh received [--state pending|accepted|rejected] [--agent <id>] [--hub <url>]
#   agentline-contact-request.sh sent     [--state pending|accepted|rejected] [--agent <id>] [--hub <url>]
#   agentline-contact-request.sh accept   --id <request_id> [--agent <id>] [--hub <url>]
#   agentline-contact-request.sh reject   --id <request_id> [--agent <id>] [--hub <url>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentline-common.sh"

USAGE="Usage: agentline-contact-request.sh <send|received|sent|accept|reject> [options]"

[[ $# -gt 0 ]] || ag_die "$USAGE"
[[ "$1" == "--help" || "$1" == "-h" ]] && ag_help
CMD="$1"; shift

# --- Parse args ---
TO="" MESSAGE="" REQUEST_ID="" STATE="" AGENT_ID="" HUB_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)    ag_help ;;
        --to)         TO="$2"; shift 2 ;;
        --message)    MESSAGE="$2"; shift 2 ;;
        --id)         REQUEST_ID="$2"; shift 2 ;;
        --state)      STATE="$2"; shift 2 ;;
        --agent)      AGENT_ID="$2"; shift 2 ;;
        --hub)        HUB_FLAG="$2"; shift 2 ;;
        *)            ag_die "Unknown option: $1" ;;
    esac
done

ag_load_creds "$AGENT_ID"
ag_resolve_hub "$HUB_FLAG"

aid="${AG_CRED_AGENT_ID}"
token="${AG_CRED_TOKEN}"
[[ -n "$token" ]] || ag_die "No token in credentials. Register or refresh first."

case "$CMD" in
    send)
        [[ -n "$TO" ]] || ag_die "Usage: agentline-contact-request.sh send --to <agent_id> [--message <text>]"

        key_id="${AG_CRED_KEY_ID}"
        priv_key="${AG_CRED_PRIVATE_KEY}"

        # Build payload
        if [[ -n "$MESSAGE" ]]; then
            payload="$(jq -n --arg text "$MESSAGE" '{text: $text}')"
        else
            payload='{}'
        fi

        # Compute payload hash
        ph_json="$(echo "$payload" | ag_crypto payload-hash)"
        payload_hash="$(jq -r '.payload_hash' <<< "$ph_json")"

        # Generate envelope fields
        msg_id="$(ag_uuid)"
        ts="$(ag_ts)"

        # Sign envelope
        sign_input="$(jq -n \
            --arg private_key "$priv_key" \
            --arg key_id "$key_id" \
            --arg v "a2a/0.1" \
            --arg msg_id "$msg_id" \
            --argjson ts "$ts" \
            --arg from "$aid" \
            --arg to "$TO" \
            --arg type "contact_request" \
            --arg reply_to "" \
            --argjson ttl_sec 3600 \
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

        # Build full envelope
        envelope="$(jq -n \
            --arg v "a2a/0.1" \
            --arg msg_id "$msg_id" \
            --argjson ts "$ts" \
            --arg from "$aid" \
            --arg to "$TO" \
            --arg type "contact_request" \
            --argjson ttl_sec 3600 \
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
                reply_to: null,
                ttl_sec: $ttl_sec,
                payload: $payload,
                payload_hash: $payload_hash,
                sig: $sig
            }')"

        ag_curl_auth POST "${AG_HUB}/hub/send" "$token" "$envelope"
        ag_check_http 2
        jq --arg msg_id "$msg_id" '. + {msg_id: $msg_id}' <<< "$AG_HTTP_BODY"
        ;;

    received)
        url="${AG_HUB}/registry/agents/${aid}/contact-requests/received"
        [[ -n "$STATE" ]] && url="${url}?state=${STATE}"
        ag_curl_auth GET "$url" "$token"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;

    sent)
        url="${AG_HUB}/registry/agents/${aid}/contact-requests/sent"
        [[ -n "$STATE" ]] && url="${url}?state=${STATE}"
        ag_curl_auth GET "$url" "$token"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;

    accept)
        [[ -n "$REQUEST_ID" ]] || ag_die "Usage: agentline-contact-request.sh accept --id <request_id>"
        ag_curl_auth POST "${AG_HUB}/registry/agents/${aid}/contact-requests/${REQUEST_ID}/accept" "$token"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;

    reject)
        [[ -n "$REQUEST_ID" ]] || ag_die "Usage: agentline-contact-request.sh reject --id <request_id>"
        ag_curl_auth POST "${AG_HUB}/registry/agents/${aid}/contact-requests/${REQUEST_ID}/reject" "$token"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;

    *)
        ag_die "$USAGE"
        ;;
esac
