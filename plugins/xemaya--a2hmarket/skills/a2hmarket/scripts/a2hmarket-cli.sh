#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NODE_BIN="${NODE_BIN:-node}"
export NODE_NO_WARNINGS="${NODE_NO_WARNINGS:-1}"

CMD="${1:-}"
if [[ -z "$CMD" ]]; then
  cat <<'USAGE'
Usage: ./scripts/a2hmarket-cli.sh <command> [options]

Commands:
  a2a-send     发送 A2A 消息
  inbox-pull   拉取 inbox 消息
  inbox-ack    确认 inbox 消息
  inbox-peek   预览未读消息数
USAGE
  exit 1
fi

shift

case "$CMD" in
  a2a-send)
    exec "$NODE_BIN" "$ROOT_DIR/bin/a2hmarket.js" a2a send "$@"
    ;;
  inbox-pull)
    exec "$NODE_BIN" "$ROOT_DIR/bin/a2hmarket.js" inbox pull "$@"
    ;;
  inbox-ack)
    exec "$NODE_BIN" "$ROOT_DIR/bin/a2hmarket.js" inbox ack "$@"
    ;;
  inbox-peek)
    exec "$NODE_BIN" "$ROOT_DIR/bin/a2hmarket.js" inbox peek "$@"
    ;;
  *)
    echo "unknown command: $CMD" >&2
    echo "run './scripts/a2hmarket-cli.sh' without arguments to see usage" >&2
    exit 1
    ;;
esac
