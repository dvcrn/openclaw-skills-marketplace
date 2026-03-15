#!/bin/bash
# WebSocket Receiver Skill - 安装脚本

echo "🚀 安装 WebSocket Receiver Skill..."

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要 Python 3"
    exit 1
fi

# 安装依赖
echo "📦 安装依赖..."
python3 -m pip install --user websockets 2>/dev/null || python3 -m pip install websockets

# 创建数据目录
mkdir -p ~/clawd/data/websocket

# 添加到 PATH
SKILL_BIN="$HOME/clawd/skills/websocket-receiver/scripts"
SHELL_RC=""

if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [ -n "$SHELL_RC" ]; then
    if ! grep -q "websocket-receiver" "$SHELL_RC"; then
        echo "export PATH=\"$SKILL_BIN:\$PATH\"" >> "$SHELL_RC"
        echo "✅ 已添加到 PATH ($SHELL_RC)"
    fi
fi

# 创建示例配置
CONFIG_FILE="$HOME/.openclaw/websocket-config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" << 'EOF'
{
  "ws_url": "ws://59.110.46.1:6680/ws",
  "batch_size": 10,
  "auto_analyze": true,
  "data_dir": "~/clawd/data/websocket"
}
EOF
    echo "✅ 创建配置: $CONFIG_FILE"
fi

echo ""
echo "✅ 安装完成!"
echo ""
echo "使用方法:"
echo "  websocket-receiver start    # 启动"
echo "  websocket-receiver stop     # 停止"
echo "  websocket-receiver status   # 状态"
echo "  websocket-receiver logs     # 日志"
echo ""
echo "或者使用环境变量:"
echo "  WEBSOCKET_URL=ws://example.com:8765 websocket-receiver start"
echo ""
