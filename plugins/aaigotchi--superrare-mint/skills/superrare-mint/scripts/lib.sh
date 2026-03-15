#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_FILE="${SUPER_RARE_CONFIG_FILE:-$SKILL_DIR/config.json}"
TRANSFER_TOPIC="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

err() {
  echo "Error: $*" >&2
  exit 1
}

require_bin() {
  command -v "$1" >/dev/null 2>&1 || err "Required binary not found: $1"
}

trim_hex_64_to_dec() {
  local hex_value="$1"
  local clean="${hex_value#0x}"
  clean="${clean#${clean%%[!0]*}}"
  if [ -z "$clean" ]; then
    echo "0"
    return
  fi
  cast --to-dec "0x$clean"
}

load_config() {
  [ -f "$CONFIG_FILE" ] || err "Missing config file: $CONFIG_FILE (copy config.example.json to config.json)"

  CONFIG_CHAIN="$(jq -r '.chain // "mainnet"' "$CONFIG_FILE")"
  CONFIG_COLLECTION="$(jq -r '.collectionContract // empty' "$CONFIG_FILE")"
  CONFIG_RECEIVER="$(jq -r '.receiver // empty' "$CONFIG_FILE")"
  CONFIG_ROYALTY_RECEIVER="$(jq -r '.royaltyReceiver // empty' "$CONFIG_FILE")"
  CONFIG_RPC_URL="$(jq -r '.rpcUrl // empty' "$CONFIG_FILE")"
  CONFIG_API_BASE_URL="$(jq -r '.apiBaseUrl // "https://api.superrare.org"' "$CONFIG_FILE")"
  CONFIG_DESCRIPTION_PREFIX="$(jq -r '.descriptionPrefix // "SuperRare mint via aaigotchi"' "$CONFIG_FILE")"
}

apply_chain_defaults() {
  case "${1:-$CONFIG_CHAIN}" in
    mainnet)
      CHAIN="mainnet"
      CHAIN_ID=1
      RPC_URL="${ETH_MAINNET_RPC:-${CONFIG_RPC_URL:-https://ethereum-rpc.publicnode.com}}"
      EXPLORER_TX_BASE="https://etherscan.io/tx/"
      ;;
    sepolia)
      CHAIN="sepolia"
      CHAIN_ID=11155111
      RPC_URL="${ETH_SEPOLIA_RPC:-${CONFIG_RPC_URL:-https://ethereum-sepolia-rpc.publicnode.com}}"
      EXPLORER_TX_BASE="https://sepolia.etherscan.io/tx/"
      ;;
    *)
      err "Unsupported chain: ${1:-$CONFIG_CHAIN}. Use mainnet or sepolia."
      ;;
  esac
}

resolve_bankr_api_key() {
  if [ -n "${BANKR_API_KEY:-}" ]; then
    echo "$BANKR_API_KEY"
    return
  fi

  if command -v systemctl >/dev/null 2>&1; then
    local env_key
    env_key="$(systemctl --user show-environment 2>/dev/null | awk -F= '$1=="BANKR_API_KEY"{print $2; exit}')"
    if [ -n "$env_key" ]; then
      echo "$env_key"
      return
    fi
  fi

  local config_path
  for config_path in \
    "$HOME/.openclaw/skills/bankr/config.json" \
    "$HOME/.openclaw/workspace/skills/bankr/config.json"
  do
    if [ -f "$config_path" ]; then
      local value
      value="$(jq -r '.apiKey // empty' "$config_path")"
      if [ -n "$value" ]; then
        echo "$value"
        return
      fi
    fi
  done

  err "BANKR_API_KEY not found in env or Bankr config"
}

resolve_bankr_api_url() {
  local config_path
  for config_path in \
    "$HOME/.openclaw/skills/bankr/config.json" \
    "$HOME/.openclaw/workspace/skills/bankr/config.json"
  do
    if [ -f "$config_path" ]; then
      local value
      value="$(jq -r '.apiUrl // empty' "$config_path")"
      if [ -n "$value" ]; then
        echo "$value"
        return
      fi
    fi
  done

  echo "https://api.bankr.bot"
}

extract_token_id_from_receipt() {
  local receipt_json="$1"
  local contract_address="$2"

  echo "$receipt_json" | jq -r --arg topic "$TRANSFER_TOPIC" --arg contract "$contract_address" '
    .logs[]? |
    select((.topics[0] // "" | ascii_downcase) == ($topic | ascii_downcase)) |
    select((.address // "" | ascii_downcase) == ($contract | ascii_downcase)) |
    (.topics[3] // empty)
  ' | head -n1
}

write_receipt_file() {
  local file_path="$1"
  local payload="$2"

  mkdir -p "$(dirname "$file_path")"
  printf '%s\n' "$payload" > "$file_path"
}


wait_for_receipt_json() {
  local tx_hash="$1"
  local rpc_url="$2"
  local timeout_seconds="${3:-300}"
  local poll_seconds="${4:-5}"
  local start_ts now_ts receipt_json status

  start_ts="$(date +%s)"
  while true; do
    if receipt_json="$(cast receipt "$tx_hash" --rpc-url "$rpc_url" --json 2>/dev/null)"; then
      status="$(echo "$receipt_json" | jq -r '.status // empty')"
      if [ -n "$status" ] && [ "$status" != "null" ]; then
        echo "$receipt_json"
        return 0
      fi
    fi

    now_ts="$(date +%s)"
    if [ $((now_ts - start_ts)) -ge "$timeout_seconds" ]; then
      err "Timed out waiting for receipt for $tx_hash after ${timeout_seconds}s"
    fi
    sleep "$poll_seconds"
  done
}
