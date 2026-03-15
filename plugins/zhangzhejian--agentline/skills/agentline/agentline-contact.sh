#!/usr/bin/env bash
# agentline-contact.sh — Manage contacts (list, get, remove).
# Adding contacts is done via the contact request flow (agentline-contact-request.sh).
#
# Usage:
#   agentline-contact.sh list  [--agent <id>] [--hub <url>]
#   agentline-contact.sh get   --id <agent_id> [--agent <id>] [--hub <url>]
#   agentline-contact.sh remove --id <agent_id> [--agent <id>] [--hub <url>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentline-common.sh"

USAGE="Usage: agentline-contact.sh <list|get|remove> [options]"

[[ $# -gt 0 ]] || ag_die "$USAGE"
[[ "$1" == "--help" || "$1" == "-h" ]] && ag_help
CMD="$1"; shift

# --- Parse args ---
CONTACT_ID="" AGENT_ID="" HUB_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) ag_help ;;
        --id)    CONTACT_ID="$2"; shift 2 ;;
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
    list)
        ag_curl_auth GET "${AG_HUB}/registry/agents/${aid}/contacts" "$token"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;
    get)
        [[ -n "$CONTACT_ID" ]] || ag_die "Usage: agentline-contact.sh get --id <agent_id>"
        ag_curl_auth GET "${AG_HUB}/registry/agents/${aid}/contacts/${CONTACT_ID}" "$token"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;
    remove)
        [[ -n "$CONTACT_ID" ]] || ag_die "Usage: agentline-contact.sh remove --id <agent_id>"
        ag_curl_auth DELETE "${AG_HUB}/registry/agents/${aid}/contacts/${CONTACT_ID}" "$token"
        ag_check_http 2
        jq -n --arg id "$CONTACT_ID" '{removed: $id}'
        ;;
    *)
        ag_die "$USAGE"
        ;;
esac
