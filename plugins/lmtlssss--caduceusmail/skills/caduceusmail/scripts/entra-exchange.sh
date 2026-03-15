#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'USAGE'
Usage:
  bash ./scripts/entra-exchange.sh send --from <alias@domain> --mailbox <mailbox@domain> --to <recipient@domain> --subject <text> --body <text> [--dry-run]
USAGE
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

command="$1"
shift || true

case "${command}" in
  send)
    exec python3 "${SCRIPT_DIR}/send_mail_graph.py" send "$@"
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    echo "Unknown subcommand: ${command}" >&2
    usage
    exit 1
    ;;
esac
