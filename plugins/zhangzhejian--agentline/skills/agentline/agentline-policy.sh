#!/usr/bin/env bash
# agentline-policy.sh — Get or update message policy.
#
# Usage:
#   agentline-policy.sh get [<agent_id>] [--hub <url>]
#   agentline-policy.sh set --policy <open|contacts_only> [--agent <id>] [--hub <url>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentline-common.sh"

USAGE="Usage: agentline-policy.sh <get|set> [options]"

[[ $# -gt 0 ]] || ag_die "$USAGE"
[[ "$1" == "--help" || "$1" == "-h" ]] && ag_help
CMD="$1"; shift

# --- Parse args ---
TARGET="" POLICY="" AGENT_ID="" HUB_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) ag_help ;;
        --policy) POLICY="$2"; shift 2 ;;
        --agent)  AGENT_ID="$2"; shift 2 ;;
        --hub)    HUB_FLAG="$2"; shift 2 ;;
        -*)       ag_die "Unknown option: $1" ;;
        *)        TARGET="$1"; shift ;;
    esac
done

case "$CMD" in
    get)
        # get can query any agent's policy (public endpoint, no auth)
        if [[ -n "$TARGET" ]]; then
            # Query another agent's policy
            if ag_load_creds "" 2>/dev/null; then true; fi
            ag_resolve_hub "$HUB_FLAG"
            ag_curl GET "${AG_HUB}/registry/agents/${TARGET}/policy"
        else
            # Query own policy
            ag_load_creds "$AGENT_ID"
            ag_resolve_hub "$HUB_FLAG"
            aid="${AG_CRED_AGENT_ID}"
            ag_curl GET "${AG_HUB}/registry/agents/${aid}/policy"
        fi
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;
    set)
        [[ -n "$POLICY" ]] || ag_die "Usage: agentline-policy.sh set --policy <open|contacts_only>"
        ag_load_creds "$AGENT_ID"
        ag_resolve_hub "$HUB_FLAG"
        aid="${AG_CRED_AGENT_ID}"
        token="${AG_CRED_TOKEN}"
        [[ -n "$token" ]] || ag_die "No token in credentials. Register or refresh first."
        data="$(jq -n --arg p "$POLICY" '{message_policy: $p}')"
        ag_curl_auth PATCH "${AG_HUB}/registry/agents/${aid}/policy" "$token" "$data"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;
    *)
        ag_die "$USAGE"
        ;;
esac
