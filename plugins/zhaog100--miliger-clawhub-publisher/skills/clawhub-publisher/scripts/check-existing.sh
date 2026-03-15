#!/bin/bash
# check-existing.sh - 检查ClawHub/GitHub上的现有技能版本
# 用法: bash check-existing.sh <skill-name>
# 退出码:
#   0 - 不存在（可以发布）
#   1 - 存在且所有者是当前用户（需要更新）
#   2 - 存在但所有者不是当前用户（需要换slug或放弃）

set -e

SKILL_NAME="$1"
CURRENT_USER="${CLAWHUB_USER:-zhaog100}"  # 从环境变量获取，默认zhaog100

if [ -z "$SKILL_NAME" ]; then
    echo "用法: bash check-existing.sh <skill-name>"
    exit 1
fi

echo "=== 检查技能: $SKILL_NAME ==="
echo ""

# 检查ClawHub
echo "【ClawHub】"
CLAWHUB_INFO=$(clawhub inspect "$SKILL_NAME" 2>&1)
CLAWHUB_EXIT_CODE=$?

if [ $CLAWHUB_EXIT_CODE -eq 0 ]; then
    # 存在，解析信息
    VERSION=$(echo "$CLAWHUB_INFO" | grep -oP 'version:\s*\K[\d.]+' || echo "未知")
    OWNER=$(echo "$CLAWHUB_INFO" | grep -oP 'owner:\s*\K\w+' || echo "未知")
    PACKAGE_ID=$(echo "$CLAWHUB_INFO" | grep -oP 'packageId:\s*\K\w+' || echo "未知")
    
    echo "  ✅ 已存在"
    echo "  - 版本: $VERSION"
    echo "  - 所有者: $OWNER"
    echo "  - Package ID: $PACKAGE_ID"
    echo ""
    
    # 判断所有者
    if [ "$OWNER" = "$CURRENT_USER" ]; then
        echo "  📌 所有者是当前用户，可以更新"
        exit 1
    else
        echo "  ⚠️  所有者不是当前用户，需要换slug或放弃"
        exit 2
    fi
else
    echo "  ❌ 不存在"
    echo ""
fi

# 检查GitHub（可选，需要配置GitHub CLI）
echo "【GitHub】"
if command -v gh &> /dev/null; then
    GITHUB_CHECK=$(gh repo view "openclaw/skills/$SKILL_NAME" 2>&1)
    if [ $? -eq 0 ]; then
        echo "  ✅ 已存在"
        echo "  - 仓库: openclaw/skills/$SKILL_NAME"
    else
        echo "  ❌ 未找到"
    fi
else
    echo "  ⏭️  跳过（未安装gh CLI）"
fi

echo ""
echo "=== 结论 ==="
echo "✅ 不存在，可以直接发布"
exit 0
