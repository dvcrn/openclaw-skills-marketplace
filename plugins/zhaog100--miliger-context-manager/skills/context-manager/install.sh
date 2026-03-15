#!/bin/bash
# Context Manager v2.0 安装脚本

SKILL_NAME="context-manager"
INSTALL_DIR="$HOME/.openclaw/skills/$SKILL_NAME"

echo "🚀 安装 Context Manager v2.0..."

# 创建目录
mkdir -p "$INSTALL_DIR/scripts"
mkdir -p "$INSTALL_DIR/logs"

# 复制文件
cp scripts/seamless-switch.sh "$INSTALL_DIR/scripts/"
cp SKILL.md "$INSTALL_DIR/"
cp README.md "$INSTALL_DIR/" 2>/dev/null || true
cp install.sh "$INSTALL_DIR/" 2>/dev/null || true

# 设置权限
chmod +x "$INSTALL_DIR/scripts/seamless-switch.sh"

# 配置定时任务
echo "⏰ 配置定时任务（每10分钟）..."
(crontab -l 2>/dev/null | grep -v "seamless-switch.sh"; echo "*/10 * * * * $INSTALL_DIR/scripts/seamless-switch.sh >> $HOME/.openclaw/workspace/logs/seamless-switch-cron.log 2>&1") | crontab -

# 验证安装
if [ -f "$INSTALL_DIR/scripts/seamless-switch.sh" ]; then
    echo "✅ 安装成功"
    echo "📍 安装位置：$INSTALL_DIR"
    echo "⏰ 定时任务：每10分钟检查上下文"
    echo "🎯 阈值：85%（可自定义）"
    echo ""
    echo "📖 使用方式："
    echo "  - 正常对话即可，一切自动完成"
    echo "  - 查看日志：tail -50 ~/.openclaw/workspace/logs/seamless-switch.log"
    echo "  - 查看定时任务：crontab -l | grep seamless"
else
    echo "❌ 安装失败"
    exit 1
fi
