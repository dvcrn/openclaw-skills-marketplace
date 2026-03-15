#!/usr/bin/env bash
# agentline-refresh.sh — Refresh JWT token via nonce signature.
#
# Usage: agentline-refresh.sh [--agent <id>] [--hub <url>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentline-common.sh"

# --- Parse args ---
AGENT_ID="" HUB_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) ag_help ;;
        --agent) AGENT_ID="$2"; shift 2 ;;
        --hub)   HUB_FLAG="$2"; shift 2 ;;
        *)       ag_die "Unknown option: $1" ;;
    esac
done

ag_load_creds "$AGENT_ID"
ag_resolve_hub "$HUB_FLAG"

aid="${AG_CRED_AGENT_ID}"
key_id="${AG_CRED_KEY_ID}"
priv_key="${AG_CRED_PRIVATE_KEY}"

# Generate a random nonce (32 bytes, base64)
nonce="$(node -e "console.log(require('crypto').randomBytes(32).toString('base64'))")"

# Sign the nonce (same as sign-challenge — signs raw decoded bytes)
sig_json="$(ag_crypto sign-challenge "$priv_key" "$nonce")"
sig="$(jq -r '.sig' <<< "$sig_json")"

# POST token refresh
data="$(jq -n --arg kid "$key_id" --arg nonce "$nonce" --arg sig "$sig" \
    '{key_id: $kid, nonce: $nonce, sig: $sig}')"

ag_curl POST "${AG_HUB}/registry/agents/${aid}/token/refresh" "$data"
ag_check_http 2

token="$(jq -r '.agent_token' <<< "$AG_HTTP_BODY")"
expires_at="$(jq -r '.expires_at' <<< "$AG_HTTP_BODY")"

# Update credentials
AG_CRED_TOKEN="$token"
AG_CRED_TOKEN_EXPIRES="$expires_at"
ag_save_creds

jq -n --arg agent_id "$aid" --argjson expires_at "$expires_at" \
    '{agent_id: $agent_id, token_refreshed: true, expires_at: $expires_at}'
