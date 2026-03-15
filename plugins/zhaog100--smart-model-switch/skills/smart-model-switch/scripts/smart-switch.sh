#!/bin/bash

# 智能模型切换主脚本
# 功能：分析消息复杂度，自动选择最优模型

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

MESSAGE="$1"

if [ -z "$MESSAGE" ]; then
    echo "用法: smart-switch.sh <消息内容>"
    exit 1
fi

# 调用复杂度分析
ANALYSIS=$(node "$SCRIPT_DIR/analyze-complexity.js" "$MESSAGE" 2>/dev/null)

if [ $? -ne 0 ]; then
    echo "❌ 复杂度分析失败"
    exit 1
fi

# 提取选择的模型
SELECTED_MODEL=$(echo "$ANALYSIS" | jq -r '.selectedModel')
SCORE=$(echo "$ANALYSIS" | jq -r '.analysis.score')

echo "📊 复杂度评分：$SCORE"
echo "🎯 推荐模型：$SELECTED_MODEL"
echo ""
echo "$ANALYSIS" | jq '.'

# 询问是否切换
read -p "是否切换到推荐模型？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    "$SCRIPT_DIR/switch-model.sh" "$SELECTED_MODEL"
fi
