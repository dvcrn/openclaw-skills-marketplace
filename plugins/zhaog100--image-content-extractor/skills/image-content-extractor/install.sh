#!/bin/bash

# 图片内容提取技能安装脚本
# 版本：1.0.0

set -e

echo "🎨 图片内容提取技能 - 安装"
echo "================================"

# 检测系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "❌ 无法检测操作系统"
    exit 1
fi

echo "📋 系统: $OS"

# 安装系统依赖
install_system_deps() {
    echo ""
    echo "📦 安装系统依赖..."

    if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        sudo apt-get update
        sudo apt-get install -y \
            tesseract-ocr \
            tesseract-ocr-chi-sim \
            tesseract-ocr-eng \
            python3-pip \
            python3-venv
    elif [ "$OS" = "darwin" ]; then
        brew install tesseract tesseract-lang
    else
        echo "⚠️  请手动安装: tesseract-ocr, python3"
    fi

    echo "✅ 系统依赖安装完成"
}

# 安装Python依赖
install_python_deps() {
    echo ""
    echo "📦 安装Python依赖..."

    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi

    source venv/bin/activate

    pip install --upgrade pip
    pip install \
        opencv-python \
        pillow \
        pytesseract \
        numpy

    echo "✅ Python依赖安装完成"
}

# 验证安装
verify() {
    echo ""
    echo "🔍 验证安装..."

    if command -v tesseract &> /dev/null; then
        echo "✅ Tesseract: $(tesseract --version | head -1)"
    else
        echo "❌ Tesseract未安装"
        exit 1
    fi

    if python3 -c "import cv2, PIL, pytesseract" 2>/dev/null; then
        echo "✅ Python包: OK"
    else
        echo "❌ Python包缺失"
        exit 1
    fi

    echo "✅ 安装验证通过"
}

# 显示使用指南
show_usage() {
    echo ""
    echo "================================"
    echo "✨ 安装完成！"
    echo ""
    echo "📖 使用方法："
    echo "  python3 scripts/extract-content.py /path/to/image.png"
    echo ""
    echo "📚 详细文档："
    echo "  cat SKILL.md"
    echo ""
}

# 主流程
main() {
    install_system_deps
    install_python_deps
    verify
    show_usage
}

main
