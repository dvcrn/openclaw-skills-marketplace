#!/bin/bash

# 终端OCR主脚本

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SKILL_DIR/../venv"

if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "❌ 虚拟环境未安装，请先运行 install.sh"
    exit 1
fi

source "$VENV_DIR/bin/activate"

IMAGE_PATH="$1"

if [ -z "$IMAGE_PATH" ]; then
    echo "用法: ./terminal-ocr.sh <image_path>"
    exit 1
fi

if [ ! -f "$IMAGE_PATH" ]; then
    echo "❌ 文件不存在: $IMAGE_PATH"
    exit 1
fi

echo "🚀 开始终端OCR处理..."
echo "图片: $IMAGE_PATH"

# 预处理图片
echo "🔧 预处理图片..."
python "$SKILL_DIR/preprocess-image.py" "$IMAGE_PATH"

# 尝试OCR识别（如果有tesseract）
if command -v tesseract &> /dev/null; then
    echo "🔍 使用Tesseract OCR识别..."
    # 这里会调用tesseract进行OCR
    echo "✅ Tesseract OCR功能待实现"
else
    echo "⚠️  Tesseract未安装，使用AI视觉分析..."
    python "$SKILL_DIR/fallback-ai-analysis.py" "$IMAGE_PATH"
fi

echo "🎉 处理完成！"