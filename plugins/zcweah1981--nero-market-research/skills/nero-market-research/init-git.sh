#!/bin/bash

# Nero Market Research - 初始化Git仓库
# 用法: ./init-git.sh <github-username> <github-token>

set -e

USERNAME="$1"
TOKEN="$2"
REPO_NAME="nero-market-research"

if [ -z "$USERNAME" ] || [ -z "$TOKEN" ]; then
    echo "❌ 用法: ./init-git.sh <github-username> <github-token>"
    exit 1
fi

REPO_DIR="/root/.openclaw/workspace-work/nero-market-research"
cd "$REPO_DIR"

echo "🚀 初始化Git仓库..."
echo "用户名: $USERNAME"
echo "仓库名: $REPO_NAME"
echo ""

# 配置git
git config --global user.name "$USERNAME"
git config --global user.email "$USERNAME@users.noreply.github.com"

# 初始化仓库（如果还没有）
if [ ! -d ".git" ]; then
    git init
    git branch -M main
    echo "✅ Git仓库已初始化"
else
    echo "✅ Git仓库已存在"
fi

# 创建GitHub仓库
echo ""
echo "📦 创建GitHub仓库..."

RESPONSE=$(curl -s -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d "{\"name\":\"$REPO_NAME\",\"description\":\"AI 独立开发者的情报挖掘系统 - 从500条噪音中精准找到神仙点子\",\"private\":false,\"has_issues\":true,\"has_projects\":true,\"has_wiki\":true}")

# 检查是否创建成功
if echo "$RESPONSE" | grep -q '"full_name"'; then
    echo "✅ GitHub仓库已创建"
else
    echo "⚠️ 仓库可能已存在或创建失败"
    echo "$RESPONSE"
fi

# 添加远程仓库
git remote remove origin 2>/dev/null || true
git remote add origin "https://$TOKEN@github.com/$USERNAME/$REPO_NAME.git"

echo "✅ 远程仓库已配置"

# 添加所有文件
echo ""
echo "📝 添加文件..."
git add -A

# 提交
git commit -m "Initial commit: Nero Market Research v4.0.0

✨ 功能特性:
- 自动化数据收集（350个数据源）
- 智能评分系统（四维打分 + 一票否决）
- Notion自动同步（三字段结构）
- 每日报告自动生成

📚 文档:
- SKILL.md - 快速开始
- README.md - 详细说明
- docs/ - 完整文档

🔧 安装:
chmod +x install.sh
./install.sh
"

# 推送
echo ""
echo "🚀 推送到GitHub..."
git push -u origin main

echo ""
echo "✅ 完成！"
echo ""
echo "📦 仓库地址:"
echo "https://github.com/$USERNAME/$REPO_NAME"
echo ""
echo "🎉 现在可以使用 ./auto-sync.sh 自动同步变更"
