#!/usr/bin/env bash
# dql.sh — 执行 Dynatrace DQL 查询
#
# 用法：
#   echo "fetch events..." | ./dql.sh
#   cat query.dql       | ./dql.sh
#
# 配置优先级（从高到低）：
#   1. 环境变量 DT_ENV_URL / DT_TOKEN（显式传入，优先级最高）
#   2. 同目录下的 config.json（首次运行时交互式写入）
#
# config.json 格式：
#   { "DT_ENV_URL": "https://xxx.apps.dynatrace.com", "DT_TOKEN": "dt0s16.xxx" }

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.json"

# ── 读取配置（环境变量 > config.json）──────────────────────
load_config() {
  local key="$1"
  # 环境变量优先
  local env_val="${!key:-}"
  if [[ -n "$env_val" ]]; then
    echo "$env_val"
    return
  fi
  # 从 config.json 读取
  if [[ -f "$CONFIG_FILE" ]]; then
    local val
    val=$(jq -r --arg k "$key" '.[$k] // empty' "$CONFIG_FILE" 2>/dev/null || true)
    if [[ -n "$val" ]]; then
      echo "$val"
      return
    fi
  fi
  echo ""
}

# ── 首次配置：交互式询问并保存 ─────────────────────────────
ensure_config() {
  local url token existing_url existing_token

  existing_url=$(load_config "DT_ENV_URL")
  existing_token=$(load_config "DT_TOKEN")

  if [[ -n "$existing_url" && -n "$existing_token" ]]; then
    return  # 已有配置，跳过
  fi

  echo "[dql.sh] 首次使用，需要配置 Dynatrace 连接信息（将保存到 config.json）" >&2
  echo "" >&2

  if [[ -z "$existing_url" ]]; then
    read -rp "  DT_ENV_URL（如 https://xxxxxx.apps.dynatrace.com）: " url </dev/tty
  else
    url="$existing_url"
  fi

  if [[ -z "$existing_token" ]]; then
    read -rsp "  DT_TOKEN（Platform Token，dt0s16.xxx，输入不显示）: " token </dev/tty
    echo "" >&2
  else
    token="$existing_token"
  fi

  # 写入 config.json
  jq -n \
    --arg url "$url" \
    --arg token "$token" \
    '{"DT_ENV_URL": $url, "DT_TOKEN": $token}' \
    > "$CONFIG_FILE"

  chmod 600 "$CONFIG_FILE"  # 仅当前用户可读
  echo "[dql.sh] 配置已保存到 $CONFIG_FILE" >&2
}

# ── 主流程 ──────────────────────────────────────────────────
ensure_config

DT_ENV_URL=$(load_config "DT_ENV_URL")
DT_TOKEN=$(load_config "DT_TOKEN")
DT_TIMEOUT_MS="${DT_TIMEOUT_MS:-60000}"
DT_MAX_RECORDS="${DT_MAX_RECORDS:-1000}"
DQL_API="${DT_ENV_URL}/platform/storage/query/v1/query:execute"

# ── 读取 DQL（从 stdin）──────────────────────────────────────
DQL_CONTENT=$(cat)

if [[ -z "$DQL_CONTENT" ]]; then
  echo "[dql.sh] 错误：stdin 为空，请通过管道传入 DQL 语句" >&2
  exit 1
fi

# ── 构造 JSON payload 并执行查询 ─────────────────────────────
PAYLOAD=$(jq -n \
  --arg query "$DQL_CONTENT" \
  --argjson timeout "$DT_TIMEOUT_MS" \
  --argjson maxRecords "$DT_MAX_RECORDS" \
  '{query: $query, requestTimeoutMilliseconds: $timeout, maxResultRecords: $maxRecords}')

curl -s -X POST "$DQL_API" \
  -H "Authorization: Bearer $DT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD"
