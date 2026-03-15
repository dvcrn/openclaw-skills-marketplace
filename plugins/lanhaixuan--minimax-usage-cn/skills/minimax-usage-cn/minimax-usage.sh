#!/bin/bash
# Minimax Coding Plan Usage Check (国内版)
# Usage: ./minimax-usage.sh
# Requires: MINIMAX_API_KEY in environment

API_KEY="${MINIMAX_API_KEY}"

if [ -z "$API_KEY" ]; then
  echo "❌ Error: MINIMAX_API_KEY required in environment"
  exit 1
fi

echo "🔍 Checking Minimax Coding Plan usage..."

RESPONSE=$(curl -s --location "https://www.minimaxi.com/v1/api/openplatform/coding_plan/remains" \
  --header "Authorization: Bearer $API_KEY" \
  --header "Content-Type: application/json")

# 检查是否返回了有效数据
if echo "$RESPONSE" | grep -q '"status_code":0'; then
  ERROR_MSG="success"
else
  ERROR_MSG=$(echo "$RESPONSE" | grep -o '"status_msg":"[^"]*"' | cut -d'"' -f4)
  echo "❌ API Error: $ERROR_MSG"
  exit 1
fi

# 解析数据 (使用 grep + cut 避免依赖 jq)
TOTAL=$(echo "$RESPONSE" | grep -o '"current_interval_total_count":[0-9]*' | head -1 | cut -d: -f2)
REMAINS=$(echo "$RESPONSE" | grep -o '"current_interval_usage_count":[0-9]*' | head -1 | cut -d: -f2)
MODEL=$(echo "$RESPONSE" | grep -o '"model_name":"[^"]*"' | head -1 | cut -d'"' -f4)
START_TS=$(echo "$RESPONSE" | grep -o '"start_time":[0-9]*' | head -1 | cut -d: -f2)
END_TS=$(echo "$RESPONSE" | grep -o '"end_time":[0-9]*' | head -1 | cut -d: -f2)

if [ -n "$TOTAL" ] && [ -n "$REMAINS" ]; then
  # 注意: current_interval_usage_count 是剩余用量，不是已用量!
  USED=$((TOTAL - REMAINS))
  PERCENT=$((USED * 100 / TOTAL))
  
  # 计算窗口剩余时间 (end_time - now)
  NOW_TS=$(date +%s000)
  if [ -n "$END_TS" ] && [ "$END_TS" -gt "$NOW_TS" ]; then
    REMAIN_MS=$((END_TS - NOW_TS))
    WIN_HOURS=$((REMAIN_MS / 3600000))
    WIN_MINS=$(((REMAIN_MS % 3600000) / 60000))
    WIN_RESET="约 ${WIN_HOURS}h ${WIN_MINS}m"
  else
    WIN_RESET="< 1h"
  fi
  
  # 转换窗口时间为可读格式
  if [ -n "$START_TS" ]; then
    WIN_START=$(date -d @$((START_TS / 1000)) "+%H:%M" 2>/dev/null)
    WIN_END=$(date -d @$((END_TS / 1000)) "+%H:%M" 2>/dev/null)
    WINDOW_INFO="${WIN_START} - ${WIN_END} (UTC+8)"
  else
    WINDOW_INFO="未知"
  fi
  
  echo "✅ Usage retrieved successfully:"
  echo ""
  echo "📊 Coding Plan Status (${MODEL}):"
  echo "   Used:      ${USED} / ${TOTAL} prompts (${PERCENT}%)"
  echo "   Remaining: ${REMAINS} prompts"
  echo "   Window:    ${WINDOW_INFO}"
  echo "   Resets in: ${WIN_RESET}"
  echo ""
  
  if [ "$PERCENT" -gt 90 ]; then
    echo "🚨 CRITICAL: ${PERCENT}% used! Stop all AI work immediately."
  elif [ "$PERCENT" -gt 75 ]; then
    echo "⚠️  WARNING: ${PERCENT}% used. Approaching limit."
  elif [ "$PERCENT" -gt 60 ]; then
    echo "⚠️  CAUTION: ${PERCENT}% used. Target is 60%."
  else
    echo "💚 GREEN: ${PERCENT}% used. Plenty of buffer."
  fi
else
  echo "⚠️  Could not parse usage data"
  echo "$RESPONSE"
fi
