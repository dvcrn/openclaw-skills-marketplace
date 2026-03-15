#!/usr/bin/env bash
# agentline-resolve.sh — Resolve agent info + active endpoints.
#
# Usage: agentline-resolve.sh <agent_id> [--hub <url>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentline-common.sh"

# --- Parse args ---
TARGET="" HUB_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) ag_help ;;
        --hub) HUB_FLAG="$2"; shift 2 ;;
        -*)    ag_die "Unknown option: $1" ;;
        *)     TARGET="$1"; shift ;;
    esac
done

[[ -n "$TARGET" ]] || ag_die "Usage: agentline-resolve.sh <agent_id> [--hub <url>]"

# Try loading creds for hub URL fallback (non-fatal)
if ag_load_creds "" 2>/dev/null; then true; fi
ag_resolve_hub "$HUB_FLAG"

ag_curl GET "${AG_HUB}/registry/resolve/${TARGET}"
ag_check_http 2

echo "$AG_HTTP_BODY"
