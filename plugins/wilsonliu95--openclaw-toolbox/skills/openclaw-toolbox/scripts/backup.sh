#!/bin/bash

# OpenClaw 自动备份脚本
# 使用方法: ./backup.sh [commit message]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
GIT_REMOTE="origin"

NO_PUSH=0
DRY_RUN=0
PULL_BEFORE=0
COMMIT_MSG=""

usage() {
  cat <<'USAGE'
Usage:
  backup.sh [message]

Options:
  --pull        备份前先 git pull --rebase（要求工作区干净）
  --no-push     只提交，不推送
  --dry-run     仅显示变更，不提交
  -m, --message 提交信息
  -h, --help    显示帮助

USAGE
}

parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --pull) PULL_BEFORE=1 ;;
      --no-push) NO_PUSH=1 ;;
      --dry-run) DRY_RUN=1 ;;
      -m|--message)
        shift
        COMMIT_MSG="$1"
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        if [ -z "$COMMIT_MSG" ]; then
          COMMIT_MSG="$1"
        else
          COMMIT_MSG="$COMMIT_MSG $1"
        fi
        ;;
    esac
    shift
  done
}

parse_args "$@"

cd "$BACKUP_DIR"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "✗ 当前目录不是 Git 仓库: $BACKUP_DIR"
  exit 1
fi

if ! git remote get-url "$GIT_REMOTE" >/dev/null 2>&1; then
  GIT_REMOTE="$(git remote | head -n1)"
fi
if [ -z "$GIT_REMOTE" ]; then
  echo "⚠️  未找到 Git 远端"
fi

REPO_URL=""
if [ -n "$GIT_REMOTE" ]; then
  REPO_URL="$(git remote get-url "$GIT_REMOTE" 2>/dev/null || true)"
fi
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)"

echo "🔄 开始备份 OpenClaw 配置..."

if [ "$PULL_BEFORE" -eq 1 ]; then
  if git diff --quiet && git diff --staged --quiet; then
    echo "⬇️  拉取最新代码..."
    git pull --rebase || echo "⚠️  git pull 失败，请手动处理"
  else
    echo "⚠️  工作区有未提交变更，跳过 git pull"
  fi
fi

# 检查是否有更改
if [ -z "$(git status --porcelain)" ]; then
  echo "✅ 没有需要备份的更改"
  exit 0
fi

if [ "$DRY_RUN" -eq 1 ]; then
  echo "📄 变更预览:"
  git status --short
  exit 0
fi

# 默认提交信息
if [ -z "$COMMIT_MSG" ]; then
  COMMIT_MSG="Backup: $(date '+%Y-%m-%d %H:%M:%S')"
fi

echo "➕ 添加更改到暂存区..."
git add -A

echo "💾 提交更改..."
git commit -m "$COMMIT_MSG"

if [ "$NO_PUSH" -eq 0 ]; then
  echo "☁️  推送到 GitHub..."
  if [ -n "$GIT_REMOTE" ] && [ -n "$CURRENT_BRANCH" ]; then
    if ! git push "$GIT_REMOTE" "$CURRENT_BRANCH"; then
      echo "✗ 推送失败：可能需要先 git pull --rebase"
      exit 1
    fi
  else
    if ! git push; then
      echo "✗ 推送失败：请检查 Git 远端或设置上游分支"
      exit 1
    fi
  fi
else
  echo "⚠️  跳过推送（--no-push）"
fi

echo "✅ 备份完成！"
echo "📦 仓库地址: ${REPO_URL:-N/A}"
if [ -n "$CURRENT_BRANCH" ]; then
  echo "🌿 分支: ${GIT_REMOTE:-?}/${CURRENT_BRANCH}"
fi
echo "📝 提交信息: $COMMIT_MSG"
