#!/bin/bash

echo "📦 安装富途API技能..."

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖包..."
pip install futu-api pandas

echo ""
echo "✅ 安装完成！"
echo ""
echo "使用方法："
echo "1. 激活虚拟环境: source venv/bin/activate"
echo "2. 运行命令: python futu_api.py quote 00700 --market HK"
echo ""
echo "前置要求："
echo "- 安装并运行 FutuOpenD 应用程序"
echo "- 登录富途账户"
echo "- 确保连接地址: 127.0.0.1:11111"