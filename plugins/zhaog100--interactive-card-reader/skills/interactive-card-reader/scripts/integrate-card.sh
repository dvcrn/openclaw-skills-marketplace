#!/bin/bash

# AI集成脚本
# 功能：检测用户消息中的消息ID，自动获取卡片内容

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

USER_MESSAGE="$1"

if [ -z "$USER_MESSAGE" ]; then
    exit 0
fi

# 检测飞书消息ID（om_开头）
MESSAGE_ID=$(echo "$USER_MESSAGE" | grep -oP 'om_[a-f0-9]{32}' | head -1)

if [ -z "$MESSAGE_ID" ]; then
    # 没有检测到消息ID，静默退出
    exit 0
fi

# 获取卡片内容
CARD_CONTENT=$("$SCRIPT_DIR/get-feishu-card.sh" "$MESSAGE_ID" 2>&1)

# 检查是否成功
SUCCESS=$(echo "$CARD_CONTENT" | jq -r '.success // false' 2>/dev/null)
IS_CARD=$(echo "$CARD_CONTENT" | jq -r '.is_card // true' 2>/dev/null)

if [ "$SUCCESS" != "true" ]; then
    # 获取失败，静默退出
    exit 0
fi

if [ "$IS_CARD" = "false" ]; then
    # 不是卡片消息，静默退出
    exit 0
fi

# 输出卡片内容（供AI使用）
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 检测到交互式卡片（ID: $MESSAGE_ID）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "$CARD_CONTENT" | jq -r '.content' | jq .
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
