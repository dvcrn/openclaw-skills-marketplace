#!/usr/bin/env bash
set -euo pipefail

KEYWORD=""
MAX_ITEMS="10"
ENSURE_BRIDGE="false"
BRIDGE_CMD=""

LOCAL_WORKDIR="${WEB_COLLECTION_LOCAL_WORKDIR:-/Users/zhym/coding/web_pluging/web_collection}"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

usage() {
  cat <<'EOF'
Usage:
  run.sh --keyword "<关键词>" [--max-items 10] [--ensure-bridge] [--bridge-cmd '<cmd>']

Defaults:
  platform=douyin
  method=videoKeyword
  feature=video
  mode=search
  interval=300
  fetch-detail=true
  detail-speed=fast
  auto-export=true
  export-mode=personal
  force-stop-before-start=true
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --keyword)
      KEYWORD="${2:-}"
      shift 2
      ;;
    --max-items)
      MAX_ITEMS="${2:-10}"
      shift 2
      ;;
    --ensure-bridge)
      ENSURE_BRIDGE="true"
      shift 1
      ;;
    --bridge-cmd)
      BRIDGE_CMD="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$KEYWORD" ]]; then
  echo "--keyword is required" >&2
  exit 1
fi

CMD=(
  bash "$SKILL_DIR/scripts/collect_and_export_loop.sh"
  --platform douyin
  --method videoKeyword
  --keyword "$KEYWORD"
  --max-items "$MAX_ITEMS"
  --feature video
  --mode search
  --interval 300
  --fetch-detail true
  --detail-speed fast
  --auto-export true
  --export-mode personal
  --force-stop-before-start
)

if [[ "$ENSURE_BRIDGE" == "true" ]]; then
  CMD+=(--ensure-bridge)
  if [[ -n "$BRIDGE_CMD" ]]; then
    CMD+=(--bridge-cmd "$BRIDGE_CMD")
  fi
fi

"${CMD[@]}"
