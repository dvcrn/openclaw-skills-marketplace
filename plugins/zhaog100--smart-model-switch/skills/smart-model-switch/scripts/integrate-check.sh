#!/bin/bash

# AI主动检测集成脚本（无输出版）
# 功能：静默检查上下文，仅在需要时输出提醒

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 调用主动检测脚本，静默输出
RESULT=$("$SCRIPT_DIR/ai-proactive-check.sh" 2>/dev/null)

# 只有在有输出时才显示（表示需要提醒）
if [ -n "$RESULT" ]; then
    echo "$RESULT"
fi
