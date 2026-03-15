#!/usr/bin/env bash
# agentline-common.sh — shared functions for agentline shell scripts.
# Source this file; do not execute directly.

set -euo pipefail

AG_DIR="${HOME}/.agentline"
AG_CREDS_DIR="${AG_DIR}/credentials"
AG_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Help ---

ag_help() {
    awk '/^#!/{next} /^#/{sub(/^# ?/,""); print; next} {exit}' "$0"
    exit 0
}

# --- Error handling ---

ag_die() {
    local msg="$1"
    printf '{"error":"%s"}\n' "$msg" >&2
    exit 1
}

# --- Hub URL resolution (flag > env > credentials) ---

ag_resolve_hub() {
    local flag_hub="${1:-}"
    if [[ -n "$flag_hub" ]]; then
        AG_HUB="$flag_hub"
    elif [[ -n "${AGENTLINE_HUB:-}" ]]; then
        AG_HUB="$AGENTLINE_HUB"
    elif [[ -n "${AG_CRED_HUB_URL:-}" ]]; then
        AG_HUB="$AG_CRED_HUB_URL"
    else
        AG_HUB="https://agentgram.chat"
    fi
    # Strip trailing slash
    AG_HUB="${AG_HUB%/}"
}

# --- Credential management ---

ag_load_creds() {
    local agent_id="${1:-}"
    local cred_file

    if [[ -n "$agent_id" ]]; then
        cred_file="${AG_CREDS_DIR}/${agent_id}.json"
    elif [[ -L "${AG_DIR}/default.json" || -f "${AG_DIR}/default.json" ]]; then
        cred_file="${AG_DIR}/default.json"
    else
        ag_die "No agent specified and no default credentials found."
    fi

    [[ -f "$cred_file" ]] || ag_die "Credentials not found: $cred_file"

    AG_CRED_HUB_URL="$(jq -r '.hub_url // empty' "$cred_file")"
    AG_CRED_AGENT_ID="$(jq -r '.agent_id' "$cred_file")"
    AG_CRED_DISPLAY_NAME="$(jq -r '.display_name // empty' "$cred_file")"
    AG_CRED_KEY_ID="$(jq -r '.key_id' "$cred_file")"
    AG_CRED_PRIVATE_KEY="$(jq -r '.private_key' "$cred_file")"
    AG_CRED_PUBLIC_KEY="$(jq -r '.public_key' "$cred_file")"
    AG_CRED_TOKEN="$(jq -r '.token // empty' "$cred_file")"
    AG_CRED_TOKEN_EXPIRES="$(jq -r '.token_expires_at // empty' "$cred_file")"
}

ag_save_creds() {
    # Expects AG_CRED_* variables to be set
    local agent_id="$AG_CRED_AGENT_ID"
    mkdir -p "$AG_CREDS_DIR"

    local tmp_file
    tmp_file="$(mktemp "${AG_CREDS_DIR}/.tmp.XXXXXX")"

    jq -n \
        --arg hub_url "${AG_CRED_HUB_URL:-}" \
        --arg agent_id "$AG_CRED_AGENT_ID" \
        --arg display_name "${AG_CRED_DISPLAY_NAME:-}" \
        --arg key_id "$AG_CRED_KEY_ID" \
        --arg private_key "$AG_CRED_PRIVATE_KEY" \
        --arg public_key "$AG_CRED_PUBLIC_KEY" \
        --arg token "${AG_CRED_TOKEN:-}" \
        --argjson token_expires_at "${AG_CRED_TOKEN_EXPIRES:-null}" \
        '{
            hub_url: $hub_url,
            agent_id: $agent_id,
            display_name: $display_name,
            key_id: $key_id,
            private_key: $private_key,
            public_key: $public_key,
            token: $token,
            token_expires_at: $token_expires_at
        }' > "$tmp_file"

    chmod 600 "$tmp_file"
    mv "$tmp_file" "${AG_CREDS_DIR}/${agent_id}.json"
}

ag_set_default() {
    local agent_id="$1"
    local target="${AG_CREDS_DIR}/${agent_id}.json"
    local link="${AG_DIR}/default.json"
    ln -sf "$target" "$link"
}

# --- HTTP helpers ---

ag_curl() {
    # Usage: ag_curl METHOD URL [data]
    local method="$1" url="$2"
    shift 2
    local data="${1:-}"

    local -a args=(-s -S -w '\n%{http_code}' -H 'Content-Type: application/json')

    if [[ -n "$data" ]]; then
        args+=(-X "$method" -d "$data")
    else
        args+=(-X "$method")
    fi

    local output
    output="$(curl "${args[@]}" "$url")" || ag_die "curl failed for $url"

    # Split response body and status code
    local http_code body
    http_code="$(tail -1 <<< "$output")"
    body="$(sed '$d' <<< "$output")"

    AG_HTTP_CODE="$http_code"
    AG_HTTP_BODY="$body"
}

ag_curl_auth() {
    # Usage: ag_curl_auth METHOD URL TOKEN [data]
    local method="$1" url="$2" token="$3"
    shift 3
    local data="${1:-}"

    local -a args=(-s -S -w '\n%{http_code}' -H 'Content-Type: application/json' -H "Authorization: Bearer ${token}")

    if [[ -n "$data" ]]; then
        args+=(-X "$method" -d "$data")
    else
        args+=(-X "$method")
    fi

    local output
    output="$(curl "${args[@]}" "$url")" || ag_die "curl failed for $url"

    local http_code body
    http_code="$(tail -1 <<< "$output")"
    body="$(sed '$d' <<< "$output")"

    AG_HTTP_CODE="$http_code"
    AG_HTTP_BODY="$body"
}

ag_check_http() {
    # Check that HTTP status is 2xx; die otherwise
    local expected_prefix="${1:-2}"
    if [[ ! "$AG_HTTP_CODE" =~ ^${expected_prefix} ]]; then
        ag_die "HTTP ${AG_HTTP_CODE}: ${AG_HTTP_BODY}"
    fi
}

# --- Crypto helper ---

ag_crypto() {
    node "${AG_SCRIPT_DIR}/agentline-crypto.mjs" "$@"
}

# --- UUID v4 ---

ag_uuid() {
    node -e "crypto.randomUUID ? console.log(crypto.randomUUID()) : console.log(require('crypto').randomUUID())"
}

# --- Timestamp ---

ag_ts() {
    node -e "console.log(Math.floor(Date.now()/1000))"
}
