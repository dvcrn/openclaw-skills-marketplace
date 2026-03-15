#!/bin/bash
# AI Agent Security Scanner - 安装脚本
# 用法: ./scripts/install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

echo "🛡️ AI Agent Security Scanner 安装"
echo "================================="
echo ""

# 检查 Python 版本
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ 需要 Python 3.10+，当前版本: $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python 版本: $PYTHON_VERSION"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install --upgrade pip
pip install -e .

# 验证安装
echo ""
echo "🔍 验证安装..."
if python -c "from scanner.cli import app" 2>/dev/null; then
    echo "✅ 安装成功！"
    echo ""
    echo "使用方法:"
    echo "  source venv/bin/activate"
    echo "  aascan scan          # 执行安全扫描"
    echo "  aascan discover      # 资产发现"
    echo "  aascan check-apikey  # 检测 API Key"
    echo ""
    echo "  aascan scan --help   # 查看更多选项"
else
    echo "⚠️ 模块导入测试失败，尝试直接运行..."
    if ./venv/bin/aascan --help > /dev/null 2>&1; then
        echo "✅ 安装成功！"
    else
        echo "❌ 安装失败，请检查错误信息"
        exit 1
    fi
fi
