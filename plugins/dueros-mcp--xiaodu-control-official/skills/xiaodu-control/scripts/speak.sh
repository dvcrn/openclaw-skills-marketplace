#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
用法:
  speak.sh --text 文本 [--device-name 设备名 | --cuid ID --client-id ID] [--server 服务名]

示例:
  speak.sh --text "晚饭好了" --device-name "小度智能屏2"
  speak.sh --server xiaodu --text "请到楼下来" --cuid abc --client-id xyz
EOF
}

SERVER="xiaodu"
TEXT=""
DEVICE_NAME=""
CUID=""
CLIENT_ID=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --server)
      SERVER="${2:-}"
      shift 2
      ;;
    --text)
      TEXT="${2:-}"
      shift 2
      ;;
    --device-name)
      DEVICE_NAME="${2:-}"
      shift 2
      ;;
    --cuid)
      CUID="${2:-}"
      shift 2
      ;;
    --client-id)
      CLIENT_ID="${2:-}"
      shift 2
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

if [[ -z "$TEXT" ]]; then
  echo "必须提供 --text" >&2
  usage >&2
  exit 1
fi

if [[ -z "$DEVICE_NAME" && ( -z "$CUID" || -z "$CLIENT_ID" ) ]]; then
  echo "必须提供 --device-name，或者同时提供 --cuid 和 --client-id" >&2
  usage >&2
  exit 1
fi

if ! command -v mcporter >/dev/null 2>&1; then
  echo "PATH 中未找到 mcporter" >&2
  exit 1
fi

if [[ -n "$DEVICE_NAME" ]]; then
  eval "$(
    python3 "$(dirname "$0")/device_resolver.py" \
      --server "$SERVER" \
      --device-name "$DEVICE_NAME" \
      --format shell
  )"
fi

ARGS=("text=$TEXT")
ARGS+=("cuid=$CUID")
ARGS+=("client_id=$CLIENT_ID")

mcporter call "${SERVER}.xiaodu_speak" "${ARGS[@]}"
