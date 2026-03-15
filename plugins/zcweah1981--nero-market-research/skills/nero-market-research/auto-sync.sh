#!/bin/bash

# Nero Market Research - 自动同步到GitHub脚本
# 用法: ./auto-sync.sh "commit message"

set -e

REPO_DIR="/root/.openclaw/workspace-work/nero-market-research"
COMMIT_MSG="${1:-Auto sync: $(date '+%Y-%m-%d %H:%M:%S')}"

cd "$REPO_DIR"

# 检查是否有变更
if [ -z "$(git status --porcelain)" ]; then
    echo "✅ 没有变更需要提交"
    exit 0
fi

echo "📤 同步到GitHub..."
echo "Commit: $COMMIT_MSG"
echo ""

# 添加所有变更
git add -A

# 提交
git commit -m "$COMMIT_MSG"

# 推送
git push origin main

echo ""
echo "✅ 同步完成！"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
