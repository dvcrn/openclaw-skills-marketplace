#!/usr/bin/env bash
# agentline-register.sh — Register a new agent, verify challenge, save credentials.
#
# Usage: agentline-register.sh --name <display_name> [--hub <url>] [--set-default]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentline-common.sh"

# --- Parse args ---
NAME="" HUB_FLAG="" SET_DEFAULT=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) ag_help ;;
        --name)    NAME="$2"; shift 2 ;;
        --hub)     HUB_FLAG="$2"; shift 2 ;;
        --set-default) SET_DEFAULT=true; shift ;;
        *) ag_die "Unknown option: $1" ;;
    esac
done

[[ -n "$NAME" ]] || ag_die "Usage: agentline-register.sh --name <display_name> [--hub <url>] [--set-default]"
ag_resolve_hub "$HUB_FLAG"

# --- 1. Generate keypair ---
keys="$(ag_crypto keygen)"
priv_key="$(jq -r '.private_key' <<< "$keys")"
pub_key="$(jq -r '.public_key' <<< "$keys")"
pubkey_fmt="$(jq -r '.pubkey_formatted' <<< "$keys")"

# --- 2. Register agent ---
reg_data="$(jq -n --arg name "$NAME" --arg pk "$pubkey_fmt" \
    '{display_name: $name, pubkey: $pk}')"

ag_curl POST "${AG_HUB}/registry/agents" "$reg_data"
ag_check_http 2

agent_id="$(jq -r '.agent_id' <<< "$AG_HTTP_BODY")"
key_id="$(jq -r '.key_id' <<< "$AG_HTTP_BODY")"
challenge="$(jq -r '.challenge' <<< "$AG_HTTP_BODY")"

# --- 3. Sign challenge ---
sig_json="$(ag_crypto sign-challenge "$priv_key" "$challenge")"
sig="$(jq -r '.sig' <<< "$sig_json")"

# --- 4. Verify (challenge-response) ---
verify_data="$(jq -n --arg kid "$key_id" --arg ch "$challenge" --arg s "$sig" \
    '{key_id: $kid, challenge: $ch, sig: $s}')"

ag_curl POST "${AG_HUB}/registry/agents/${agent_id}/verify" "$verify_data"
ag_check_http 2

token="$(jq -r '.agent_token' <<< "$AG_HTTP_BODY")"
expires_at="$(jq -r '.expires_at' <<< "$AG_HTTP_BODY")"

# --- 5. Save credentials ---
AG_CRED_HUB_URL="$AG_HUB"
AG_CRED_AGENT_ID="$agent_id"
AG_CRED_DISPLAY_NAME="$NAME"
AG_CRED_KEY_ID="$key_id"
AG_CRED_PRIVATE_KEY="$priv_key"
AG_CRED_PUBLIC_KEY="$pub_key"
AG_CRED_TOKEN="$token"
AG_CRED_TOKEN_EXPIRES="$expires_at"
ag_save_creds

if [[ "$SET_DEFAULT" == true ]]; then
    ag_set_default "$agent_id"
fi

# --- Output result ---
jq -n \
    --arg agent_id "$agent_id" \
    --arg key_id "$key_id" \
    --arg name "$NAME" \
    --arg hub "$AG_HUB" \
    --argjson set_default "$SET_DEFAULT" \
    '{agent_id: $agent_id, key_id: $key_id, display_name: $name, hub: $hub, set_default: $set_default}'
