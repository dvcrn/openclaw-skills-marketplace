#!/bin/bash

# 引用内容提取脚本（增强版）
# 功能：根据消息ID检索真实消息内容，支持飞书/QQ/企业微信

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
INTENT_FILE="$SKILL_DIR/config/intent-rules.json"
FEISHU_CONFIG="$SKILL_DIR/config/feishu-config.json"

QUOTE_INFO="$1"

if [ -z "$QUOTE_INFO" ]; then
    echo "用法: extract-quote.sh <引用信息JSON>"
    exit 1
fi

# 解析引用信息
HAS_QUOTE=$(echo "$QUOTE_INFO" | jq -r '.has_quote')
PLATFORM=$(echo "$QUOTE_INFO" | jq -r '.platform')
MESSAGE_ID=$(echo "$QUOTE_INFO" | jq -r '.message_id')
QUOTED_TEXT=$(echo "$QUOTE_INFO" | jq -r '.quoted_text // empty')

# 如果没有引用，直接返回
if [ "$HAS_QUOTE" != "true" ]; then
    echo '{"error": "无引用信息"}'
    exit 0
fi

# 识别引用意图
detect_intent() {
    local user_message="$1"

    # 读取意图规则
    local intents=$(jq -r '.intents | keys[]' "$INTENT_FILE" 2>/dev/null)

    for intent in $intents; do
        local keywords=$(jq -r ".intents.\"$intent\".keywords[]" "$INTENT_FILE" 2>/dev/null)

        for keyword in $keywords; do
            if echo "$user_message" | grep -qi "$keyword"; then
                echo "$intent"
                return 0
            fi
        done
    done

    echo "unknown"
}

# 检索飞书消息（真实API调用）⭐
retrieve_feishu_message() {
    local message_id="$1"

    # 获取Token
    TOKEN_INFO=$("$SCRIPT_DIR/get-feishu-token.sh" 2>/dev/null)
    TOKEN=$(echo "$TOKEN_INFO" | jq -r '.token // empty')

    if [ -z "$TOKEN" ]; then
        echo '{"error": "获取飞书Token失败"}'
        return 1
    fi

    # 调用飞书API获取消息详情
    RESPONSE=$(curl -s -X GET \
      "https://open.feishu.cn/open-apis/im/v1/messages/$message_id" \
      -H "Authorization: Bearer $TOKEN")

    # 检查响应
    CODE=$(echo "$RESPONSE" | jq -r '.code // -1')
    if [ "$CODE" != "0" ]; then
        echo "{\"error\": \"获取消息失败\", \"code\": $CODE}"
        return 1
    fi

    # 提取消息内容
    MSG_TYPE=$(echo "$RESPONSE" | jq -r '.data.items[0].msg_type // empty')
    CONTENT=$(echo "$RESPONSE" | jq -r '.data.items[0].body.content // empty')
    SENDER_ID=$(echo "$RESPONSE" | jq -r '.data.items[0].sender.id // empty')
    CREATE_TIME=$(echo "$RESPONSE" | jq -r '.data.items[0].create_time // empty')

    # 如果是交互式卡片，解析content字段
    if [ "$MSG_TYPE" = "interactive" ]; then
        # content是JSON字符串，需要解析
        PARSED_CONTENT=$(echo "$CONTENT" | jq . 2>/dev/null || echo "\"$CONTENT\"")

        cat <<EOF
{
  "id": "$message_id",
  "msg_type": "$MSG_TYPE",
  "content": $PARSED_CONTENT,
  "sender_id": "$SENDER_ID",
  "timestamp": "$CREATE_TIME",
  "is_interactive_card": true
}
EOF
    else
        # 普通消息
        cat <<EOF
{
  "id": "$message_id",
  "msg_type": "$MSG_TYPE",
  "content": $CONTENT,
  "sender_id": "$SENDER_ID",
  "timestamp": "$CREATE_TIME",
  "is_interactive_card": false
}
EOF
    fi
}

# 检索QQ消息（待实现）
retrieve_qq_message() {
    local message_id="$1"
    # TODO: 实现QQ消息获取
    echo "{\"error\": \"QQ平台暂未实现\", \"message_id\": \"$message_id\"}"
}

# 检索企业微信消息（待实现）
retrieve_wechat_message() {
    local message_id="$1"
    # TODO: 实现企业微信消息获取
    echo "{\"error\": \"企业微信平台暂未实现\", \"message_id\": \"$message_id\"}"
}

# 根据平台检索消息
retrieve_message() {
    local message_id="$1"
    local platform="$2"

    case "$platform" in
        "feishu")
            retrieve_feishu_message "$message_id"
            ;;
        "qq")
            retrieve_qq_message "$message_id"
            ;;
        "wechat")
            retrieve_wechat_message "$message_id"
            ;;
        *)
            echo "{\"error\": \"未知平台: $platform\"}"
            ;;
    esac
}

# 提取上下文
extract_context() {
    local message_id="$1"

    # 这里应调用sessions_history获取上下文
    # 目前返回空上下文（已获取到真实消息内容）

    cat <<EOF
{
  "before": [],
  "after": []
}
EOF
}

# 主提取逻辑
main() {
    # 1. 检索引用消息（真实API调用）⭐
    local quoted_message
    if [ -n "$MESSAGE_ID" ] && [ "$MESSAGE_ID" != "null" ]; then
        quoted_message=$(retrieve_message "$MESSAGE_ID" "$PLATFORM")
    else
        # 使用提供的引用文本
        quoted_message=$(cat <<EOF
{
  "id": "unknown",
  "content": "$QUOTED_TEXT",
  "timestamp": "$(date -Iseconds)",
  "role": "unknown"
}
EOF
)
    fi

    # 2. 提取上下文
    local context
    if [ -n "$MESSAGE_ID" ] && [ "$MESSAGE_ID" != "null" ]; then
        context=$(extract_context "$MESSAGE_ID")
    else
        context='{"before": [], "after": []}'
    fi

    # 3. 识别意图
    local intent=$(detect_intent "$QUOTED_TEXT")

    # 4. 生成输出
    cat <<EOF
{
  "quoted_message": $(echo "$quoted_message" | jq .),
  "context": $(echo "$context" | jq .),
  "intent": "$intent",
  "platform": "$PLATFORM",
  "suggested_response": "$(get_suggested_response "$intent")"
}
EOF
}

# 获取建议的回复方式
get_suggested_response() {
    local intent="$1"

    case "$intent" in
        "clarify")
            echo "解释引用内容的具体含义"
            ;;
        "supplement")
            echo "基于引用内容补充相关信息"
            ;;
        "refute")
            echo "修正或反驳引用中的观点"
            ;;
        "deepen")
            echo "深入分析引用内容"
            ;;
        "relate")
            echo "关联引用内容和其他对话"
            ;;
        "example")
            echo "为引用内容举例说明"
            ;;
        *)
            echo "基于引用内容回答问题"
            ;;
    esac
}

# 执行主函数
main
