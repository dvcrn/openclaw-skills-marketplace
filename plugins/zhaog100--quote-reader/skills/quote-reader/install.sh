#!/bin/bash

# 引用前文内容读取技能 - 安装脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 安装引用前文内容读取技能..."
echo ""

# 1. 检查依赖
echo "1️⃣ 检查依赖..."
if ! command -v jq &> /dev/null; then
    echo "❌ 需要jq，请先安装"
    echo "   Ubuntu/Debian: sudo apt-get install jq"
    echo "   macOS: brew install jq"
    exit 1
fi

echo "✅ 依赖检查通过"
echo ""

# 2. 设置权限
echo "2️⃣ 设置脚本权限..."
chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null || true
echo "✅ 权限设置完成"
echo ""

# 3. 创建必要目录
echo "3️⃣ 创建必要目录..."
mkdir -p "$SKILL_DIR/data"
echo "✅ 目录创建完成"
echo ""

# 4. 测试安装
echo "4️⃣ 测试安装..."
TEST_MESSAGE="[message_id: om_x100b55b] 这个是指什么？"
RESULT=$("$SCRIPT_DIR/scripts/detect-quote.sh" "$TEST_MESSAGE" 2>&1)

if [ $? -eq 0 ]; then
    echo "✅ 测试通过"
    echo ""
    echo "测试消息：$TEST_MESSAGE"
    echo "$RESULT" | jq -r '"检测到\(.platform)引用，消息ID：\(.message_id)"'
else
    echo "❌ 测试失败：$RESULT"
    exit 1
fi
echo ""

# 5. 完成
echo "✅ 安装完成！"
echo ""
echo "📝 使用方法："
echo ""
echo "1. 检测引用："
echo "   scripts/detect-quote.sh \"用户消息\""
echo ""
echo "2. 提取引用："
echo "   scripts/extract-quote.sh \"引用信息JSON\""
echo ""
echo "3. AI集成（静默）："
echo "   scripts/integrate-quote.sh \"用户消息\""
echo ""
echo "4. 完整测试："
echo "   bash scripts/test-quote.sh"
echo ""
