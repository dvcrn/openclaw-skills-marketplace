#!/bin/bash

# AI集成脚本（静默版）
# 功能：完整引用处理流程，仅在需要时输出

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

USER_MESSAGE="$1"

if [ -z "$USER_MESSAGE" ]; then
    exit 0
fi

# 1. 检测引用
QUOTE_INFO=$("$SCRIPT_DIR/detect-quote.sh" "$USER_MESSAGE" 2>/dev/null)

# 2. 判断是否有引用
HAS_QUOTE=$(echo "$QUOTE_INFO" | jq -r '.has_quote' 2>/dev/null)

if [ "$HAS_QUOTE" != "true" ]; then
    # 无引用，静默退出
    exit 0
fi

# 3. 提取引用内容
QUOTE_CONTENT=$("$SCRIPT_DIR/extract-quote.sh" "$QUOTE_INFO" 2>/dev/null)

if [ -z "$QUOTE_CONTENT" ]; then
    exit 0
fi

# 4. 输出引用信息（供AI使用）
cat <<EOF
📋 【引用检测】

引用消息：
$(echo "$QUOTE_CONTENT" | jq -r '.quoted_message.content' 2>/dev/null)

引用意图：$(echo "$QUOTE_CONTENT" | jq -r '.intent' 2>/dev/null)
建议回复：$(echo "$QUOTE_CONTENT" | jq -r '.suggested_response' 2>/dev/null)

上下文：
$(echo "$QUOTE_CONTENT" | jq '.context.before[] | "  \(.role): \(.content)"' 2>/dev/null | head -2)

---
EOF
