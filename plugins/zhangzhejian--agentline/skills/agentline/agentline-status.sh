#!/usr/bin/env bash
# agentline-status.sh — Query message delivery status.
#
# Usage: agentline-status.sh <msg_id> [--agent <id>] [--hub <url>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentline-common.sh"

# --- Parse args ---
MSG_ID="" AGENT_ID="" HUB_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) ag_help ;;
        --agent) AGENT_ID="$2"; shift 2 ;;
        --hub)   HUB_FLAG="$2"; shift 2 ;;
        -*)      ag_die "Unknown option: $1" ;;
        *)       MSG_ID="$1"; shift ;;
    esac
done

[[ -n "$MSG_ID" ]] || ag_die "Usage: agentline-status.sh <msg_id> [--agent <id>] [--hub <url>]"

ag_load_creds "$AGENT_ID"
ag_resolve_hub "$HUB_FLAG"

token="${AG_CRED_TOKEN}"
[[ -n "$token" ]] || ag_die "No token in credentials. Register or refresh first."

ag_curl_auth GET "${AG_HUB}/hub/status/${MSG_ID}" "$token"
ag_check_http 2

echo "$AG_HTTP_BODY"
