#!/bin/bash

# 获取飞书卡片内容
# 功能：根据消息ID获取交互式卡片内容

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

MESSAGE_ID="$1"

if [ -z "$MESSAGE_ID" ]; then
    echo '{"error": "缺少消息ID"}'
    echo "用法: get-feishu-card.sh <消息ID>"
    exit 1
fi

# 获取Token
TOKEN_INFO=$("$SCRIPT_DIR/get-feishu-token.sh")
TOKEN=$(echo "$TOKEN_INFO" | jq -r '.token // empty')

if [ -z "$TOKEN" ]; then
    echo '{"error": "获取Token失败"}'
    exit 1
fi

# 调用飞书API
RESPONSE=$(curl -s -X GET \
  "https://open.feishu.cn/open-apis/im/v1/messages/$MESSAGE_ID" \
  -H "Authorization: Bearer $TOKEN")

# 检查响应
CODE=$(echo "$RESPONSE" | jq -r '.code // -1')
if [ "$CODE" != "0" ]; then
    echo "{\"error\": \"获取消息失败\", \"code\": $CODE, \"message_id\": \"$MESSAGE_ID\"}"
    exit 1
fi

# 提取消息内容
MSG_TYPE=$(echo "$RESPONSE" | jq -r '.data.items[0].msg_type // empty')
CONTENT=$(echo "$RESPONSE" | jq -r '.data.items[0].body.content // empty')
SENDER_ID=$(echo "$RESPONSE" | jq -r '.data.items[0].sender.id // empty')
CREATE_TIME=$(echo "$RESPONSE" | jq -r '.data.items[0].create_time // empty')

# 如果是交互式卡片，解析content字段
if [ "$MSG_TYPE" = "interactive" ]; then
    # content是JSON字符串，需要解析
    PARSED_CONTENT=$(echo "$CONTENT" | jq . 2>/dev/null || echo "$CONTENT")

    cat <<EOF
{
  "success": true,
  "message_id": "$MESSAGE_ID",
  "msg_type": "$MSG_TYPE",
  "sender_id": "$SENDER_ID",
  "create_time": "$CREATE_TIME",
  "content": $PARSED_CONTENT,
  "raw_response": $RESPONSE
}
EOF
else
    # 非卡片消息
    cat <<EOF
{
  "success": true,
  "message_id": "$MESSAGE_ID",
  "msg_type": "$MSG_TYPE",
  "is_card": false,
  "content": "$CONTENT",
  "sender_id": "$SENDER_ID",
  "create_time": "$CREATE_TIME"
}
EOF
fi
