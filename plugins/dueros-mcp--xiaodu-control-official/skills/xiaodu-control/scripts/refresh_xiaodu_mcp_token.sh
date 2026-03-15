#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
用法:
  refresh_xiaodu_mcp_token.sh [--config 凭据文件] [--refresh-if-within-days 天数] [--force]

示例:
  refresh_xiaodu_mcp_token.sh
  refresh_xiaodu_mcp_token.sh --refresh-if-within-days 7
  refresh_xiaodu_mcp_token.sh --force
  refresh_xiaodu_mcp_token.sh --config ~/.mcporter/xiaodu-mcp-oauth.json
  XIAODU_MCP_OAUTH_CONFIG=/path/to/xiaodu-mcp-oauth.json refresh_xiaodu_mcp_token.sh
EOF
}

CONFIG="${XIAODU_MCP_OAUTH_CONFIG:-$HOME/.mcporter/xiaodu-mcp-oauth.json}"
REFRESH_IF_WITHIN_DAYS=""
FORCE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config)
      CONFIG="${2:-}"
      shift 2
      ;;
    --refresh-if-within-days)
      REFRESH_IF_WITHIN_DAYS="${2:-}"
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "未知参数: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

ARGS=(--config "$CONFIG")
if [[ -n "$REFRESH_IF_WITHIN_DAYS" ]]; then
  ARGS+=(--refresh-if-within-days "$REFRESH_IF_WITHIN_DAYS")
fi
if [[ "$FORCE" -eq 1 ]]; then
  ARGS+=(--force)
fi

python3 "$(dirname "$0")/refresh_xiaodu_mcp_access_token.py" "${ARGS[@]}"
