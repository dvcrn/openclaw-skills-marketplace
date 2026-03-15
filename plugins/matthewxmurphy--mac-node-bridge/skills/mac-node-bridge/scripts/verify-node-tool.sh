#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  verify-node-tool.sh --host USER@HOST --bin /abs/path/to/bin

Checks SSH reachability and whether the requested binary exists on the remote Mac node.
EOF
}

HOST=""
REMOTE_BIN=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host) HOST="${2:-}"; shift 2 ;;
    --bin) REMOTE_BIN="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

[[ -n "$HOST" && -n "$REMOTE_BIN" ]] || {
  usage
  exit 1
}

[[ "$REMOTE_BIN" = /* ]] || { echo "bin must be an absolute path" >&2; exit 1; }

ssh -T "$HOST" "test -x '$REMOTE_BIN' && printf 'OK %s\n' '$REMOTE_BIN' || { printf 'MISSING %s\n' '$REMOTE_BIN' >&2; exit 1; }"
