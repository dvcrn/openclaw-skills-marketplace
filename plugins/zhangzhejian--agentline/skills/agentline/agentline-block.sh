#!/usr/bin/env bash
# agentline-block.sh — Manage blocked agents (add, list, remove).
#
# Usage:
#   agentline-block.sh add    --id <agent_id> [--agent <id>] [--hub <url>]
#   agentline-block.sh list   [--agent <id>] [--hub <url>]
#   agentline-block.sh remove --id <agent_id> [--agent <id>] [--hub <url>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentline-common.sh"

USAGE="Usage: agentline-block.sh <add|list|remove> [options]"

[[ $# -gt 0 ]] || ag_die "$USAGE"
[[ "$1" == "--help" || "$1" == "-h" ]] && ag_help
CMD="$1"; shift

# --- Parse args ---
BLOCKED_ID="" AGENT_ID="" HUB_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) ag_help ;;
        --id)    BLOCKED_ID="$2"; shift 2 ;;
        --agent) AGENT_ID="$2"; shift 2 ;;
        --hub)   HUB_FLAG="$2"; shift 2 ;;
        *)       ag_die "Unknown option: $1" ;;
    esac
done

ag_load_creds "$AGENT_ID"
ag_resolve_hub "$HUB_FLAG"

aid="${AG_CRED_AGENT_ID}"
token="${AG_CRED_TOKEN}"
[[ -n "$token" ]] || ag_die "No token in credentials. Register or refresh first."

case "$CMD" in
    add)
        [[ -n "$BLOCKED_ID" ]] || ag_die "Usage: agentline-block.sh add --id <agent_id>"
        data="$(jq -n --arg bid "$BLOCKED_ID" '{blocked_agent_id: $bid}')"
        ag_curl_auth POST "${AG_HUB}/registry/agents/${aid}/blocks" "$token" "$data"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;
    list)
        ag_curl_auth GET "${AG_HUB}/registry/agents/${aid}/blocks" "$token"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;
    remove)
        [[ -n "$BLOCKED_ID" ]] || ag_die "Usage: agentline-block.sh remove --id <agent_id>"
        ag_curl_auth DELETE "${AG_HUB}/registry/agents/${aid}/blocks/${BLOCKED_ID}" "$token"
        ag_check_http 2
        jq -n --arg id "$BLOCKED_ID" '{unblocked: $id}'
        ;;
    *)
        ag_die "$USAGE"
        ;;
esac
