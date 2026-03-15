#!/bin/bash

# Nero Market Research - 文件监控自动同步
# 用法: ./watch-sync.sh

REPO_DIR="/root/.openclaw/workspace-work/nero-market-research"
SYNC_SCRIPT="$REPO_DIR/auto-sync.sh"

echo "🔍 启动文件监控（每30秒检查一次）..."
echo "目录: $REPO_DIR"
echo "按 Ctrl+C 停止"
echo ""

while true; do
    # 检查是否有变更
    cd "$REPO_DIR"
    
    if [ -n "$(git status --porcelain)" ]; then
        echo ""
        echo "📝 检测到文件变更: $(date '+%H:%M:%S')"
        bash "$SYNC_SCRIPT" "Auto sync: $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    sleep 30
done
