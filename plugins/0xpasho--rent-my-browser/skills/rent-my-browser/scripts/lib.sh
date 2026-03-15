#!/usr/bin/env bash
# Shared functions for Rent My Browser skill scripts.
# Source this file at the top of every script:
#   source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

set -euo pipefail

# ── Base directory ──────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
STATE_DIR="$SKILL_DIR/state"

# Persistent dir survives skill updates (stored outside the skill directory)
PERSIST_DIR="${RMB_PERSIST_DIR:-$HOME/.rent-my-browser}"

mkdir -p "$STATE_DIR"
mkdir -p "$PERSIST_DIR"

# ── Logging ─────────────────────────────────────────────────────────────────
rmb_log() {
  local level="$1"
  shift
  echo "[RMB] [$(date -u +%H:%M:%S)] [$level] $*" >&2
}

# ── Dependency check ────────────────────────────────────────────────────────
rmb_check_deps() {
  local missing=()
  for cmd in curl jq node; do
    if ! command -v "$cmd" &>/dev/null; then
      missing+=("$cmd")
    fi
  done
  if [ ${#missing[@]} -gt 0 ]; then
    rmb_log ERROR "Missing required tools: ${missing[*]}"
    exit 1
  fi
}

# ── Server URL ─────────────────────────────────────────────────────────────
RMB_SERVER_URL="https://api.rentmybrowser.dev"

# ── Auth check ─────────────────────────────────────────────────────────────
rmb_ensure_auth() {
  if [ -z "${RMB_API_KEY:-}" ]; then
    rmb_log ERROR "RMB_API_KEY is not set"
    exit 1
  fi
}

# ── State management ────────────────────────────────────────────────────────
# Credentials are saved to both state/ (local) and ~/.rent-my-browser/ (persistent).
# On load, we check local first, then fall back to persistent (survives skill updates).

rmb_load_state() {
  local state_file="$STATE_DIR/credentials.json"
  local persist_file="$PERSIST_DIR/credentials.json"

  # Try local first, fall back to persistent backup
  local source_file=""
  if [ -f "$state_file" ]; then
    source_file="$state_file"
  elif [ -f "$persist_file" ]; then
    rmb_log INFO "Restoring credentials from $persist_file"
    cp "$persist_file" "$state_file"
    source_file="$state_file"
  fi

  if [ -z "$source_file" ]; then
    return 1
  fi

  # Export state values if not already set via env
  if [ -z "${RMB_NODE_ID:-}" ]; then
    RMB_NODE_ID="$(jq -r '.node_id // empty' "$source_file" 2>/dev/null || true)"
    export RMB_NODE_ID
  fi
  if [ -z "${RMB_API_KEY:-}" ]; then
    RMB_API_KEY="$(jq -r '.api_key // empty' "$source_file" 2>/dev/null || true)"
    export RMB_API_KEY
  fi
  if [ -z "${RMB_WALLET_ADDRESS:-}" ]; then
    RMB_WALLET_ADDRESS="$(jq -r '.wallet_address // empty' "$source_file" 2>/dev/null || true)"
    export RMB_WALLET_ADDRESS
  fi
  return 0
}

rmb_save_state() {
  local json="$1"

  # Save to local state dir
  local state_file="$STATE_DIR/credentials.json"
  local tmp_file="$state_file.tmp"
  echo "$json" > "$tmp_file"
  mv "$tmp_file" "$state_file"

  # Also save to persistent dir (survives skill updates)
  local persist_file="$PERSIST_DIR/credentials.json"
  local persist_tmp="$persist_file.tmp"
  echo "$json" > "$persist_tmp"
  mv "$persist_tmp" "$persist_file"
}

# ── HTTP client ─────────────────────────────────────────────────────────────
# Usage: rmb_http METHOD /path [body]
# Sets global: HTTP_STATUS, HTTP_BODY
HTTP_STATUS=""
HTTP_BODY=""

rmb_http() {
  local method="$1"
  local path="$2"
  local body="${3:-}"
  local url="${RMB_SERVER_URL}${path}"
  local max_retries=3
  local attempt=0
  local backoff=1

  local curl_args=(
    -s
    -w "\n%{http_code}"
    -X "$method"
    -H "Content-Type: application/json"
  )

  if [ -n "${RMB_API_KEY:-}" ]; then
    curl_args+=(-H "Authorization: Bearer $RMB_API_KEY")
  fi

  if [ -n "$body" ]; then
    curl_args+=(-d "$body")
  fi

  while [ $attempt -lt $max_retries ]; do
    local response
    response="$(curl "${curl_args[@]}" "$url" 2>/dev/null)" || {
      attempt=$((attempt + 1))
      if [ $attempt -lt $max_retries ]; then
        rmb_log WARN "Network error (attempt $attempt/$max_retries), retrying in ${backoff}s..."
        sleep "$backoff"
        backoff=$((backoff * 2))
        continue
      fi
      rmb_log ERROR "Network error after $max_retries attempts: $method $path"
      HTTP_STATUS="000"
      HTTP_BODY='{"error":"network_error"}'
      return 1
    }

    HTTP_BODY="$(echo "$response" | sed '$d')"
    HTTP_STATUS="$(echo "$response" | tail -1)"

    # Retry on 5xx server errors
    if [ "${HTTP_STATUS:0:1}" = "5" ]; then
      attempt=$((attempt + 1))
      if [ $attempt -lt $max_retries ]; then
        rmb_log WARN "Server error $HTTP_STATUS (attempt $attempt/$max_retries), retrying in ${backoff}s..."
        sleep "$backoff"
        backoff=$((backoff * 2))
        continue
      fi
    fi

    return 0
  done

  return 1
}

# ── Session stats ───────────────────────────────────────────────────────────
rmb_update_stats() {
  local key="$1"
  local value="$2"
  local stats_file="$STATE_DIR/session-stats.json"

  if [ ! -f "$stats_file" ]; then
    echo '{"session_started":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'","tasks_completed":0,"tasks_failed":0,"total_steps":0,"total_earnings":0,"last_task_at":null}' > "$stats_file"
  fi

  local tmp_file="$stats_file.tmp"
  jq --arg k "$key" --argjson v "$value" '.[$k] = (.[$k] + $v)' "$stats_file" > "$tmp_file"
  mv "$tmp_file" "$stats_file"
}

rmb_set_stat() {
  local key="$1"
  local value="$2"
  local stats_file="$STATE_DIR/session-stats.json"

  if [ ! -f "$stats_file" ]; then
    echo '{"session_started":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'","tasks_completed":0,"tasks_failed":0,"total_steps":0,"total_earnings":0,"last_task_at":null}' > "$stats_file"
  fi

  local tmp_file="$stats_file.tmp"
  jq --arg k "$key" --arg v "$value" '.[$k] = $v' "$stats_file" > "$tmp_file"
  mv "$tmp_file" "$stats_file"
}
