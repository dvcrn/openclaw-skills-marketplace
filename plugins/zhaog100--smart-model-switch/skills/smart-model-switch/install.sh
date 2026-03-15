#!/bin/bash

# 智能模型切换技能 - 安装脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
OPENCLAW_SKILLS="$HOME/.openclaw/skills"
OPENCLAW_WORKSPACE_SKILLS="$HOME/.openclaw/workspace/skills"

echo "🚀 安装智能模型切换技能..."
echo ""

# 1. 检查依赖
echo "1️⃣ 检查依赖..."
if ! command -v node &> /dev/null; then
    echo "❌ 需要Node.js，请先安装"
    exit 1
fi

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
chmod +x "$SKILL_DIR"/scripts/*.sh
chmod +x "$SKILL_DIR"/scripts/*.js 2>/dev/null || true
echo "✅ 权限设置完成"
echo ""

# 3. 创建必要目录
echo "3️⃣ 创建必要目录..."
mkdir -p "$SKILL_DIR/data"
mkdir -p "$HOME/.openclaw/logs"
mkdir -p "$HOME/.openclaw/model-switch-requests"
echo "✅ 目录创建完成"
echo ""

# 4. 初始化状态文件
echo "4️⃣ 初始化状态文件..."
if [ ! -f "$SKILL_DIR/data/context-state.json" ]; then
    cat > "$SKILL_DIR/data/context-state.json" << EOF
{
  "consecutive_hits": 0,
  "last_check": null,
  "current_model": "zai/glm-5",
  "last_switch": null,
  "cooldown_until": null
}
EOF
    echo "✅ 状态文件已初始化"
else
    echo "ℹ️  状态文件已存在"
fi
echo ""

# 5. 配置定时任务（可选）
echo "5️⃣ 配置定时任务（上下文监控）..."
read -p "是否配置定时任务（每10分钟检查上下文）？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    CRON_JOB="*/10 * * * * $SKILL_DIR/scripts/context-switch-monitor.sh"
    
    # 检查是否已存在
    if crontab -l 2>/dev/null | grep -q "context-switch-monitor.sh"; then
        echo "ℹ️  定时任务已存在"
    else
        # 添加定时任务
        (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
        echo "✅ 定时任务已添加"
    fi
else
    echo "ℹ️  跳过定时任务配置"
fi
echo ""

# 6. 测试安装
echo "6️⃣ 测试安装..."
TEST_MESSAGE="分析一下旅行客平台的测试策略"
RESULT=$(node "$SKILL_DIR/scripts/analyze-complexity.js" "$TEST_MESSAGE" 2>&1)

if [ $? -eq 0 ]; then
    echo "✅ 测试通过"
    echo ""
    echo "测试消息：$TEST_MESSAGE"
    echo "$RESULT" | jq -r '"评分：\(.analysis.score)，推荐模型：\(.selectedModel)"'
else
    echo "❌ 测试失败：$RESULT"
    exit 1
fi
echo ""

# 7. 完成
echo "✅ 安装完成！"
echo ""
echo "📝 使用方法："
echo ""
echo "1. 分析消息复杂度："
echo "   node $SKILL_DIR/scripts/analyze-complexity.js \"你的消息\""
echo ""
echo "2. 智能切换模型："
echo "   $SKILL_DIR/scripts/smart-switch.sh \"你的消息\""
echo ""
echo "3. 手动切换模型："
echo "   $SKILL_DIR/scripts/switch-model.sh <model_id>"
echo ""
echo "4. 查看上下文监控状态："
echo "   cat $SKILL_DIR/data/context-state.json"
echo ""
echo "5. 查看监控日志："
echo "   tail -f $HOME/.openclaw/logs/context-switch.log"
echo ""
