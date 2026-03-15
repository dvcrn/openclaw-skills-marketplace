#!/bin/bash

# 引用检测脚本
# 功能：检测用户消息中的引用标记，提取引用信息

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$SKILL_DIR/config/quote-patterns.json"

USER_MESSAGE="$1"

if [ -z "$USER_MESSAGE" ]; then
    echo "用法: detect-quote.sh <用户消息>"
    exit 1
fi

# 初始化输出
OUTPUT=$(cat <<EOF
{
  "has_quote": false,
  "platform": null,
  "message_id": null,
  "quoted_text": null,
  "quote_position": null
}
EOF
)

# 检测飞书引用
detect_feishu_quote() {
    local message="$1"
    
    # 提取message_id
    local message_id=$(echo "$message" | grep -oP '\[message_id:\s*\K[a-zA-Z0-9_]+(?=\])' | head -1)
    
    if [ -n "$message_id" ]; then
        # 提取引用文本（如果有）
        local quoted_text=$(echo "$message" | grep -oP '(?<=\]).*?(?=\[message_id)' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | head -1)
        
        echo "$(cat <<EOF
{
  "has_quote": true,
  "platform": "feishu",
  "message_id": "$message_id",
  "quoted_text": $([ -n "$quoted_text" ] && echo "\"$quoted_text\"" || echo "null"),
  "quote_position": 0
}
EOF
)"
        return 0
    fi
    
    return 1
}

# 检测QQ引用
detect_qq_quote() {
    local message="$1"
    
    # 提取引用ID
    local quote_id=$(echo "$message" | grep -oP '\[(?:quote|reply):\K[0-9]+(?=\])' | head -1)
    
    if [ -n "$quote_id" ]; then
        echo "$(cat <<EOF
{
  "has_quote": true,
  "platform": "qq",
  "message_id": "$quote_id",
  "quoted_text": null,
  "quote_position": 0
}
EOF
)"
        return 0
    fi
    
    return 1
}

# 检测通用引用标记
detect_generic_quote() {
    local message="$1"
    
    # 检测引用标记
    if echo "$message" | grep -qiE '\[引用\]|\[回复\]|引用[：:]|回复[：:]|前文[：:]|上文[：:]'; then
        # 提取引用文本
        local quoted_text=$(echo "$message" | grep -oP '(?<=(?:引用|回复|前文|上文)[：:])[[:space:]]*\K.+?(?=\n|$)' | head -1)
        
        if [ -z "$quoted_text" ]; then
            quoted_text=$(echo "$message" | grep -oP '(?<=\[引用\])[[:space:]]*\K.+?(?=\[\/引用\]|$)' | head -1)
        fi
        
        echo "$(cat <<EOF
{
  "has_quote": true,
  "platform": "generic",
  "message_id": null,
  "quoted_text": $([ -n "$quoted_text" ] && echo "\"$quoted_text\"" || echo "null"),
  "quote_position": 0
}
EOF
)"
        return 0
    fi
    
    return 1
}

# 主检测逻辑
main() {
    # 1. 尝试检测飞书引用
    local result=$(detect_feishu_quote "$USER_MESSAGE")
    if [ $? -eq 0 ]; then
        echo "$result"
        exit 0
    fi
    
    # 2. 尝试检测QQ引用
    result=$(detect_qq_quote "$USER_MESSAGE")
    if [ $? -eq 0 ]; then
        echo "$result"
        exit 0
    fi
    
    # 3. 尝试检测通用引用
    result=$(detect_generic_quote "$USER_MESSAGE")
    if [ $? -eq 0 ]; then
        echo "$result"
        exit 0
    fi
    
    # 4. 无引用
    echo "$OUTPUT"
}

# 执行主函数
main
