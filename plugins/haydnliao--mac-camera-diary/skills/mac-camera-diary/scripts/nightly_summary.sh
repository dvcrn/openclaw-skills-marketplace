#!/usr/bin/env bash
# nightly_summary.sh - 读取今日日志，生成夜间总结并推送飞书
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

DATE=$(date +%Y-%m-%d)
LOG="${DIARY_DIR}/$DATE/log.md"
SUMMARY_FILE="${DIARY_DIR}/summary.md"

if [ ! -f "$LOG" ]; then
  echo "[INFO] 今日无日志，跳过总结。"
  exit 0
fi

LOG_CONTENT=$(cat "$LOG")

SUMMARY=$(openclaw run --model "$MODEL" \
  --prompt "${SUMMARY_PROMPT}

$LOG_CONTENT" \
  2>/dev/null || echo "（今日总结生成失败，请查看 $LOG）")

# 写入汇总文件
{
  echo ""
  echo "# $DATE 总结"
  echo "$SUMMARY"
} >> "$SUMMARY_FILE"

echo "📋 总结已写入 $SUMMARY_FILE"
echo "$SUMMARY"
