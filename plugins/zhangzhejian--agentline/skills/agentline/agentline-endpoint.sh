#!/usr/bin/env bash
# agentline-endpoint.sh — Register an inbox endpoint URL with webhook auth token.
#
# Usage: agentline-endpoint.sh --url <inbox_url> --webhook-token <token> [--agent <id>] [--hub <url>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentline-common.sh"

# --- Parse args ---
URL="" AGENT_ID="" HUB_FLAG="" WEBHOOK_TOKEN=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) ag_help ;;
        --url)           URL="$2"; shift 2 ;;
        --webhook-token) WEBHOOK_TOKEN="$2"; shift 2 ;;
        --agent)         AGENT_ID="$2"; shift 2 ;;
        --hub)           HUB_FLAG="$2"; shift 2 ;;
        *) ag_die "Unknown option: $1" ;;
    esac
done

[[ -n "$URL" ]]           || ag_die "Usage: agentline-endpoint.sh --url <inbox_url> --webhook-token <token> [--agent <id>] [--hub <url>]"
[[ -n "$WEBHOOK_TOKEN" ]] || ag_die "--webhook-token is required"

ag_load_creds "$AGENT_ID"
ag_resolve_hub "$HUB_FLAG"

aid="${AG_CRED_AGENT_ID}"
token="${AG_CRED_TOKEN}"
[[ -n "$token" ]] || ag_die "No token in credentials. Register or refresh first."

data="$(jq -n --arg url "$URL" --arg wt "$WEBHOOK_TOKEN" '{url: $url, webhook_token: $wt}')"

ag_curl_auth POST "${AG_HUB}/registry/agents/${aid}/endpoints" "$token" "$data"
ag_check_http 2

echo "$AG_HTTP_BODY"
