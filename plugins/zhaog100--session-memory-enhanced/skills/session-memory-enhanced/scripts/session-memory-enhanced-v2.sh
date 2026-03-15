#!/bin/bash
# 增强版Session-Memory Hook（完整版）
# 功能：保存会话记忆 + 更新QMD + 提交Git（三位一体）
# 创建时间：2026-03-07 14:47
# 版本：2.0.0

WORKSPACE="/root/.openclaw/workspace"
MEMORY_FILE="$WORKSPACE/MEMORY.md"
LOG_FILE="$WORKSPACE/logs/session-memory-enhanced.log"

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "================================"
log "🚀 增强版Session-Memory Hook启动"
log "================================"

# 1. 等待原生session-memory hook完成（2秒）
log "⏳ 等待原生session-memory hook完成..."
sleep 2

# 2. 更新QMD知识库
log "📚 更新QMD知识库..."
cd "$WORKSPACE"

if qmd update 2>&1 >> "$LOG_FILE"; then
    log "✅ QMD知识库更新完成"
else
    log "⚠️ QMD更新失败"
fi

# 3. 提交到Git
log "📦 检查Git变更..."
cd "$WORKSPACE"

git add -A 2>&1 >> "$LOG_FILE"

# 统计变更
STATUS=$(git status --short)
if [ -n "$STATUS" ]; then
    ADD_COUNT=$(echo "$STATUS" | grep "^A" | wc -l)
    MODIFY_COUNT=$(echo "$STATUS" | grep "^M" | wc -l)
    DELETE_COUNT=$(echo "$STATUS" | grep "^D" | wc -l)
    
    COMMIT_MSG="chore: session-memory自动更新
    
时间：$(date '+%Y-%m-%d %H:%M:%S')
变更统计：
- 新增：${ADD_COUNT}个文件
- 修改：${MODIFY_COUNT}个文件
- 删除：${DELETE_COUNT}个文件"
    
    if git commit -m "$COMMIT_MSG" 2>&1 >> "$LOG_FILE"; then
        log "✅ Git提交完成：+${ADD_COUNT} ~${MODIFY_COUNT} -${DELETE_COUNT}"
    else
        log "⚠️ Git提交失败"
    fi
else
    log "ℹ️ Git无需提交（无变更）"
fi

# 4. 完成
log "✅ 增强版Session-Memory Hook完成"
log "================================"
