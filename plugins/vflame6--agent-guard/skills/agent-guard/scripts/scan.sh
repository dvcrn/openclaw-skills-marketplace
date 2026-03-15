#!/usr/bin/env bash
# AgentGuard scanner wrapper
# Usage: bash scripts/scan.sh analyze "some text" --json
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/agent_guard.py" "$@"
