#!/bin/bash

# Nero Market Research - 手动推送脚本（仓库已创建）
# 用法: ./push-manual.sh

set -e

REPO_DIR="/root/.openclaw/workspace-work/nero-market-research"
USERNAME="zcweah1981"
REPO_NAME="nero-market-research"

cd "$REPO_DIR"

echo "🚀 推送到 GitHub..."
echo "仓库: https://github.com/$USERNAME/$REPO_NAME"
echo ""

# 添加远程仓库
git remote remove origin 2>/dev/null || true
git remote add origin "git@github.com:$USERNAME/$REPO_NAME.git"

echo "✅ 远程仓库已配置"

# 推送
echo ""
echo "📤 推送代码..."
git push -u origin main

echo ""
echo "✅ 推送完成！"
echo ""
echo "📦 仓库地址:"
echo "https://github.com/$USERNAME/$REPO_NAME"
echo ""
echo "🎉 现在可以使用 ./auto-sync.sh 自动同步变更"
