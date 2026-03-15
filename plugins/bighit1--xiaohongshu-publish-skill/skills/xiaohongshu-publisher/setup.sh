#!/usr/bin/env bash
# setup.sh - 跨平台安装脚本（Linux/macOS/Openclaw 环境）
# 用法：bash setup.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔧 创建 Python 虚拟环境..."
python3 -m venv venv

echo "📦 安装依赖..."
venv/bin/pip install --upgrade pip -q
venv/bin/pip install -r requirements.txt

echo "🎭 安装 Playwright Chromium..."
venv/bin/playwright install chromium

echo ""
echo "✅ 安装完成！后续使用："
echo "   发布: ./venv/bin/python scripts/publish_xhs.py --help"
echo "   互动: ./venv/bin/python scripts/interact_xhs.py --help"
echo ""
echo "⚠️  别忘了在根目录创建 .env 文件并填入 XHS_COOKIE"
