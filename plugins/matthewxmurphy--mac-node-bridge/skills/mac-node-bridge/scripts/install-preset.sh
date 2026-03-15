#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
INSTALL_WRAPPER="$SCRIPT_DIR/install-wrapper.sh"

usage() {
  cat <<'EOF'
Usage:
  install-preset.sh --tool TOOL --host USER@HOST --target-dir DIR
                    [--name WRAPPER_NAME] [--ssh-key KEY] [--known-hosts FILE]

Supported tools:
  imsg remindctl memo things peekaboo brew gh
EOF
}

TOOL=""
HOST=""
TARGET_DIR=""
NAME=""
SSH_KEY=""
KNOWN_HOSTS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tool) TOOL="${2:-}"; shift 2 ;;
    --host) HOST="${2:-}"; shift 2 ;;
    --target-dir) TARGET_DIR="${2:-}"; shift 2 ;;
    --name) NAME="${2:-}"; shift 2 ;;
    --ssh-key) SSH_KEY="${2:-}"; shift 2 ;;
    --known-hosts) KNOWN_HOSTS="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

[[ -n "$TOOL" && -n "$HOST" && -n "$TARGET_DIR" ]] || {
  usage
  exit 1
}

case "$TOOL" in
  imsg|remindctl|memo|things|peekaboo|brew|gh)
    remote_bin="/opt/homebrew/bin/$TOOL"
    ;;
  *)
    echo "Unsupported tool preset: $TOOL" >&2
    usage
    exit 1
    ;;
esac

wrapper_name="${NAME:-$TOOL}"

cmd=(
  "$INSTALL_WRAPPER"
  --name "$wrapper_name"
  --host "$HOST"
  --remote-bin "$remote_bin"
  --target-dir "$TARGET_DIR"
)

[[ -n "$SSH_KEY" ]] && cmd+=(--ssh-key "$SSH_KEY")
[[ -n "$KNOWN_HOSTS" ]] && cmd+=(--known-hosts "$KNOWN_HOSTS")

"${cmd[@]}"
