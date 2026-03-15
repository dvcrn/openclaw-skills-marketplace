#!/bin/sh
# Git post-commit hook - 自动更新 SKILL.md
# 将此文件复制到 .git/hooks/post-commit 并添加执行权限

echo "📝 正在更新 SKILL.md..."
cd "$(git rev-parse --show-toplevel)"
node scripts/update-skill-doc.js

# 如果 SKILL.md 有变更，自动提交
git diff --quiet SKILL.md
if [ $? -ne 0 ]; then
    echo "📄 SKILL.md 已更新，正在自动提交..."
    git add SKILL.md
    git commit --amend --no-edit --no-verify
    echo "✅ SKILL.md 已自动提交"
fi
