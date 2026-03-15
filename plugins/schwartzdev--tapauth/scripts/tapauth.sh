#!/usr/bin/env bash
set -euo pipefail

TAPAUTH_BASE="${TAPAUTH_BASE_URL:-https://tapauth.ai}"
TAPAUTH_DIR="${TAPAUTH_HOME:-./.tapauth}"
mkdir -p "$TAPAUTH_DIR" && chmod 700 "$TAPAUTH_DIR"

provider="${1:-}"
scopes="${2:-}"

if [ -z "${provider:-}" ] || [ -z "${scopes:-}" ]; then
  echo "usage: tapauth <provider> <scopes>" >&2
  exit 1
fi

# Sort scopes for deterministic file naming
sorted_scopes=$(echo "$scopes" | tr "," "\n" | sort | tr "\n" "," | sed "s/,$//")
env_file="${TAPAUTH_DIR}/${provider}-${sorted_scopes}.env"

save_and_emit() {
  install -m 600 /dev/null "$env_file"
  if ! curl -sf -o "$env_file" "$1" -H "Authorization: Bearer $2"; then
    echo "tapauth: failed to fetch token" >&2
    exit 1
  fi
  source "$env_file"
  echo "${TAPAUTH_TOKEN:?tapauth: no token in response}"
}

# --- Cached/Refresh Flow ---
if [ -f "$env_file" ]; then
  source "$env_file"
  if [ -n "${TAPAUTH_EXPIRES:-}" ] && [ "$(date +%s)" -lt "${TAPAUTH_EXPIRES:-0}" ]; then
    echo "${TAPAUTH_TOKEN:-}"
    exit 0
  fi
  save_and_emit "${TAPAUTH_BASE}/api/v1/token/${TAPAUTH_GRANT_ID}.env" "${TAPAUTH_GRANT_SECRET}"
  exit 0
fi

# --- First-Run Flow ---
echo "Creating grant for ${provider} (${sorted_scopes})..." >&2
grant_response=$(curl -sf "${TAPAUTH_BASE}/api/v1/grants" \
  -X POST -H "Accept: text/plain" \
  --data-urlencode "provider=${provider}" \
  --data-urlencode "scopes=${sorted_scopes}" 2>/dev/null) || true
if [ -z "${grant_response:-}" ]; then
  echo "tapauth: failed to create grant (API request failed)" >&2
  exit 1
fi
eval "$(echo "$grant_response" | grep '^TAPAUTH_')"
if [ -z "${TAPAUTH_GRANT_ID:-}" ] || [ -z "${TAPAUTH_GRANT_SECRET:-}" ] || [ -z "${TAPAUTH_APPROVE_URL:-}" ]; then
  echo "tapauth: failed to create grant" >&2
  exit 1
fi
echo "Approve access: ${TAPAUTH_APPROVE_URL}" >&2
while true; do
  sleep 2
  response=$(curl -s -w "\n%{http_code}" "${TAPAUTH_BASE}/api/v1/token/${TAPAUTH_GRANT_ID}" \
    -H "Authorization: Bearer ${TAPAUTH_GRANT_SECRET}")
  http_code="${response##*$'\n'}"
  case "$http_code" in
    200) break ;;
    202) ;;
    *) echo "tapauth: error ${http_code}" >&2; exit 1 ;;
  esac
done
save_and_emit "${TAPAUTH_BASE}/api/v1/token/${TAPAUTH_GRANT_ID}.env" "${TAPAUTH_GRANT_SECRET}"
