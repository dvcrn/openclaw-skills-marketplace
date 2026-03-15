#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${SUNO_PYTHON_BIN:-$HOME/.suno/venv/bin/python}"

if [ ! -x "$PYTHON_BIN" ]; then
  echo "Missing Suno runtime: $PYTHON_BIN" >&2
  exit 1
fi

export PYTHONDONTWRITEBYTECODE=1
exec "$PYTHON_BIN" "$(dirname "$0")/receive_cookies.py" "$@"
