#!/bin/bash
# Session Memory Enhanced - Installation Script
# Version: 2.0.0

set -e

WORKSPACE="/root/.openclaw/workspace"
SCRIPT_NAME="session-memory-enhanced.sh"
LOG_FILE="$WORKSPACE/logs/session-memory-enhanced.log"

echo "🚀 安装 Session Memory Enhanced v2.0.0"
echo "================================"

# 1. 复制脚本
echo "📦 复制脚本文件..."
mkdir -p "$WORKSPACE/scripts"
cp "$(dirname "$0")/../scripts/$SCRIPT_NAME" "$WORKSPACE/scripts/"
chmod +x "$WORKSPACE/scripts/$SCRIPT_NAME"
echo "✅ 脚本已复制到: $WORKSPACE/scripts/$SCRIPT_NAME"

# 2. 创建日志目录
echo "📝 创建日志目录..."
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"
echo "✅ 日志目录已创建: $(dirname "$LOG_FILE")"

# 3. 检查crontab
echo "⏰ 检查crontab配置..."
if crontab -l 2>/dev/null | grep -q "$SCRIPT_NAME"; then
    echo "ℹ️  Crontab已配置"
else
    echo "ℹ️  Crontab未配置"
    echo ""
    echo "要配置定时任务吗？(建议每小时运行)"
    echo "请手动执行:"
    echo ""
    echo "  crontab -e"
    echo "  # 添加以下行:"
    echo "  0 * * * * $WORKSPACE/scripts/$SCRIPT_NAME >> $LOG_FILE 2>&1"
    echo ""
fi

# 4. 测试运行
echo "🧪 测试运行..."
if bash "$WORKSPACE/scripts/$SCRIPT_NAME" 2>&1 | tail -5; then
    echo "✅ 测试成功"
else
    echo "⚠️  测试失败（可能是正常现象，如果没有变更）"
fi

# 5. 显示日志
echo ""
echo "📊 最近日志:"
tail -20 "$LOG_FILE" 2>/dev/null || echo "ℹ️  暂无日志"

echo ""
echo "✅ 安装完成！"
echo ""
echo "🎯 使用方式:"
echo "  1. 自动模式: 每小时自动运行（需配置crontab）"
echo "  2. 手动模式: bash $WORKSPACE/scripts/$SCRIPT_NAME"
echo "  3. 查看日志: tail -f $LOG_FILE"
echo ""
echo "📚 文档: $WORKSPACE/skills/session-memory-enhanced/README.md"
echo "================================"
