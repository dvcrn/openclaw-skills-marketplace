#!/bin/bash

# 获取当前上下文使用率
# 功能：调用session_status获取上下文信息，提取使用率

# 输出上下文使用率（百分比数字）
# 例如：85

# 方法1：尝试调用openclaw status命令
if command -v openclaw &> /dev/null; then
    # 调用openclaw status，提取上下文信息
    # 格式：Context: 30k/203k (15%)
    usage=$(openclaw status 2>/dev/null | grep -oP 'Context:.*?\(\K[0-9]+' | head -1)
    if [ -n "$usage" ]; then
        echo "$usage"
        exit 0
    fi
fi

# 方法2：读取OpenClaw状态文件（如果存在）
STATUS_FILE="$HOME/.openclaw/status.json"
if [ -f "$STATUS_FILE" ]; then
    usage=$(jq -r '.context.usage // empty' "$STATUS_FILE" 2>/dev/null)
    if [ -n "$usage" ]; then
        echo "$usage"
        exit 0
    fi
fi

# 方法3：模拟值（用于测试）
# 实际部署时应该从OpenClaw API获取
echo "0"
