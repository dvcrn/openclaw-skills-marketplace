#!/bin/bash
# 微信发送消息快捷脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 使用 Python 脚本
VENV_DIR="$SCRIPT_DIR/wxbot"

# 检查虚拟环境是否存在（可能是符号链接）
if [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_DIR/bin/activate" ]; then
    VENV_DIR="/Users/sincere/.openclaw/workspace/wxbot/wxbot"
fi

if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "错误：虚拟环境未找到"
    exit 1
fi

source "$VENV_DIR/bin/activate"

# 如果只有 1 个参数，从 stdin 读取消息（支持多行和特殊字符）
if [ $# -eq 1 ]; then
    CONTACT="$1"
    MESSAGE=$(cat)
    python "$SCRIPT_DIR/wechat-send.py" "$CONTACT" "$MESSAGE"
else
    python "$SCRIPT_DIR/wechat-send.py" "$@"
fi
