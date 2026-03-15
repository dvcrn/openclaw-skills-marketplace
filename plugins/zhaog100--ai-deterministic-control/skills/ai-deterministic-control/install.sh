#!/bin/bash
# AI 确定性控制工具 - 安装脚本
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技

set -e

echo "📦 安装 AI 确定性控制工具"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 3"
    echo "请安装 Python 3.8+ 后重试"
    exit 1
fi

echo "✅ Python 版本: $(python3 --version)"

# 创建配置目录
CONFIG_DIR="$HOME/.ai-deterministic"
mkdir -p "$CONFIG_DIR"

# 创建默认配置
if [ ! -f "$CONFIG_DIR/config.json" ]; then
    cat > "$CONFIG_DIR/config.json" << 'CONFIG'
{
  "temperature": 0.7,
  "seed": null
}
CONFIG
    echo "✅ 配置文件已创建: $CONFIG_DIR/config.json"
else
    echo "ℹ️  配置文件已存在，跳过"
fi

# 添加到 PATH（可选）
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo ""
echo "📋 安装完成！"
echo ""
echo "使用方法:"
echo "  cd $SKILL_DIR"
echo "  ./deterministic.sh <command>"
echo ""
echo "或添加到 PATH:"
echo "  export PATH=\"\$PATH:$SKILL_DIR\""
echo "  deterministic <command>"
echo ""
echo "命令列表:"
echo "  temperature <value>  设置温度（0.0-2.0）"
echo "  check <outputs...>   检查输出一致性"
echo "  seed <value>         设置随机种子"
echo "  config               查看配置"
echo "  help                 显示帮助"
