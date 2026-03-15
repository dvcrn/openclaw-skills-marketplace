#!/bin/bash

# 终端OCR技能安装脚本

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SKILL_DIR/venv"

echo "🚀 安装终端OCR技能..."

# 创建虚拟环境
echo "📦 创建Python虚拟环境..."
python3 -m venv "$VENV_DIR"

# 激活虚拟环境并安装依赖
echo "📥 安装依赖包..."
source "$VENV_DIR/bin/activate"
pip install opencv-python pillow numpy

# 创建必要的目录
mkdir -p "$SKILL_DIR/data/processed"
mkdir -p "$SKILL_DIR/scripts"

echo "✅ 终端OCR技能安装完成！"
echo ""
echo "使用方法："
echo "1. 激活虚拟环境: source $VENV_DIR/bin/activate"
echo "2. 运行OCR脚本: python scripts/terminal-ocr.py /path/to/image.png"
echo ""
echo "注意：如需完整OCR功能，请在宿主机安装tesseract-ocr"