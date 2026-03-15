#!/bin/bash
# Smart Memory Sync 安装脚本

echo "🚀 安装 Smart Memory Sync..."

# 创建必要的目录
mkdir -p logs
mkdir -p data

# 设置权限
chmod +x scripts/smart-sync.py
chmod +x triggers/auto-check.py
chmod +x syncers/sync-all.py

# 检查Python版本
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python版本: $PYTHON_VERSION"

# 检查openclaw命令
if command -v openclaw &> /dev/null; then
    OPENCLAW_VERSION=$(openclaw --version 2>&1 | head -1)
    echo "✅ OpenClaw: $OPENCLAW_VERSION"
else
    echo "⚠️ OpenClaw未安装"
fi

# 检查Git
if command -v git &> /dev/null; then
    echo "✅ Git已安装"
else
    echo "⚠️ Git未安装"
fi

# 检查QMD
if command -v qmd &> /dev/null; then
    echo "✅ QMD已安装"
else
    echo "⚠️ QMD未安装（可选）"
fi

echo ""
echo "✅ 安装完成！"
echo ""
echo "使用方法："
echo "  python3 scripts/smart-sync.py --status    # 查看状态"
echo "  python3 scripts/smart-sync.py --check     # 单次检查"
echo "  python3 scripts/smart-sync.py --sync      # 手动同步"
echo "  python3 scripts/smart-sync.py --daemon    # 守护进程"
