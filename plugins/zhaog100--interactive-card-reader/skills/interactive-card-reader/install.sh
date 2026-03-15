#!/bin/bash

# Interactive Card Reader 安装脚本

SKILL_NAME="interactive-card-reader"
INSTALL_DIR="$HOME/.openclaw/skills/$SKILL_NAME"

echo "🚀 安装 Interactive Card Reader v1.0.0..."

# 创建目录
mkdir -p "$INSTALL_DIR/config"
mkdir -p "$INSTALL_DIR/scripts"
mkdir -p "$INSTALL_DIR/data"

# 复制文件
cp -r config/* "$INSTALL_DIR/config/" 2>/dev/null || true
cp -r scripts/* "$INSTALL_DIR/scripts/" 2>/dev/null || true
cp SKILL.md "$INSTALL_DIR/" 2>/dev/null || true
cp package.json "$INSTALL_DIR/" 2>/dev/null || true

# 设置权限
chmod +x "$INSTALL_DIR/scripts/"*.sh 2>/dev/null || true

# 验证安装
if [ -f "$INSTALL_DIR/scripts/get-feishu-card.sh" ]; then
    echo "✅ 安装成功"
    echo "📍 安装位置：$INSTALL_DIR"
    echo ""
    echo "📖 使用方式："
    echo "  - AI收到消息时自动检测卡片"
    echo "  - 或手动调用：scripts/get-feishu-card.sh <消息ID>"
    echo ""
    echo "⚙️  配置文件："
    echo "  - $INSTALL_DIR/config/feishu-config.json"
    echo ""
    echo "✨ 功能："
    echo "  - ✅ 飞书交互式卡片获取"
    echo "  - ✅ Token自动管理"
    echo "  - ✅ JSON结构解析"
    echo "  - ⏳ QQ/企业微信（待实现）"
else
    echo "❌ 安装失败"
    exit 1
fi
