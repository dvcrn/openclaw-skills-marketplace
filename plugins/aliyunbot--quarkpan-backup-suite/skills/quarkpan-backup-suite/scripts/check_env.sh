#!/usr/bin/env bash
set -euo pipefail

need() {
  if command -v "$1" >/dev/null 2>&1; then
    echo "[OK] $1"
  else
    echo "[ERR] missing: $1"
    return 1
  fi
}

need bash
need tar
need sha256sum
need jq

if [[ -x /root/.openclaw/workspace/scripts/backup/.venv-quark/bin/quarkpan ]]; then
  echo "[OK] quarkpan"
else
  echo "[WARN] quarkpan not found at expected path"
fi

if [[ -x /root/.openclaw/workspace/scripts/backup/.venv-tccli/bin/tccli ]]; then
  echo "[OK] tccli"
else
  echo "[WARN] tccli not found at expected path"
fi

echo "[DONE] env check finished"
