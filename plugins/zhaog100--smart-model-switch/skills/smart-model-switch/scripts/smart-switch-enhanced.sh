#!/bin/bash

# 增强版智能切换脚本 - 支持文件类型检测
# 用法: ./smart-switch-enhanced.sh "消息内容" "/path/to/file"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

MESSAGE="${1:-}"
FILE_PATH="${2:-}"

echo "📊 智能模型切换分析"
echo "📝 消息: $MESSAGE"
if [ -n "$FILE_PATH" ]; then
    echo "📁 文件: $FILE_PATH"
fi
echo ""

# 分析消息复杂度
if [ -n "$MESSAGE" ]; then
    MESSAGE_RESULT=$(node "$SCRIPT_DIR/analyze-complexity.js" "$MESSAGE")
    MESSAGE_MODEL=$(echo "$MESSAGE_RESULT" | jq -r '.selectedModel')
    HAS_VISION=$(echo "$MESSAGE_RESULT" | jq -r '.analysis.features.hasVision')
    MESSAGE_SCORE=$(echo "$MESSAGE_RESULT" | jq -r '.analysis.score')
else
    MESSAGE_MODEL=""
    HAS_VISION="false"
    MESSAGE_SCORE=0
fi

# 分析文件类型
if [ -n "$FILE_PATH" ] && [ -f "$FILE_PATH" ]; then
    FILE_RESULT=$(node "$SCRIPT_DIR/analyze-file-type.js" "$FILE_PATH")
    FILE_MODEL=$(echo "$FILE_RESULT" | jq -r '.model')
    FILE_TYPE=$(echo "$FILE_RESULT" | jq -r '.fileType')
    HAS_FILE="true"
else
    FILE_MODEL=""
    FILE_TYPE=""
    HAS_FILE="false"
fi

# 确定最终模型（文件优先级 > 消息优先级）
FINAL_MODEL=""
if [ "$HAS_FILE" = "true" ]; then
    FINAL_MODEL="$FILE_MODEL"
    echo "🎯 文件类型检测: $FILE_TYPE"
    echo "🤖 推荐模型: $FILE_MODEL"
elif [ "$HAS_VISION" = "true" ]; then
    FINAL_MODEL="$MESSAGE_MODEL"
    echo "🎯 视觉任务检测: 是"
    echo "🤖 推荐模型: $MESSAGE_MODEL"
elif [ -n "$MESSAGE_MODEL" ]; then
    FINAL_MODEL="$MESSAGE_MODEL"
    echo "🎯 复杂度评分: $MESSAGE_SCORE"
    echo "🤖 推荐模型: $MESSAGE_MODEL"
else
    FINAL_MODEL="zai/glm-5"
    echo "🤖 默认模型: zai/glm-5"
fi

echo ""
echo "✅ 最终选择模型: $FINAL_MODEL"

# 询问是否切换
read -p "是否切换到推荐模型？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    "$SCRIPT_DIR/switch-model.sh" "$FINAL_MODEL"
fi