#!/bin/bash
# Session-Memory Enhanced v3.2.0 - AI 摘要版
# 功能：不可变分片 + 会话清洗 + 智能触发 + QMD + Git + 多代理隔离 + AI 摘要
# 借鉴：memu-engine 的核心思路
# 创建时间：2026-03-07 22:10
# 作者：米粒儿

WORKSPACE="/root/.openclaw/workspace"

# 多代理支持（从环境变量获取，默认 main）
AGENT_NAME="${AGENT_NAME:-main}"
MEMORY_DIR="$WORKSPACE/memory/agents/$AGENT_NAME"
SHARED_DIR="$WORKSPACE/memory/shared"

LOG_FILE="$WORKSPACE/logs/session-memory-enhanced.log"
TAIL_FILE="$MEMORY_DIR/.tail.tmp.json"
FLUSH_IDLE_SECONDS=1800  # 30分钟
MAX_MESSAGES_PER_PART=60

# AI 摘要脚本路径 ⭐
AI_SUMMARIZER="$WORKSPACE/skills/session-memory-enhanced/scripts/ai-summarizer.sh"

# 代理配置文件（未来支持）
AGENT_CONFIG="$WORKSPACE/config/agents.json"

# 确保目录存在
mkdir -p "$MEMORY_DIR" "$SHARED_DIR" "$(dirname "$LOG_FILE")"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$AGENT_NAME] $1" >> "$LOG_FILE"
}

log "================================"
log "🚀 Session-Memory Enhanced v3.2.0 启动（代理：$AGENT_NAME）"
log "================================"

# 1. 检查是否需要固化分片
should_flush() {
    # 1. tail文件存在
    [ ! -f "$TAIL_FILE" ] && return 1

    # 2. 检查消息数量
    local msg_count=$(jq '.messages | length' "$TAIL_FILE" 2>/dev/null || echo "0")
    [ "$msg_count" -ge "$MAX_MESSAGES_PER_PART" ] && return 0

    # 3. 检查闲置时间
    local last_modified=$(stat -c %Y "$TAIL_FILE" 2>/dev/null || echo "0")
    local now=$(date +%s)
    local idle_time=$((now - last_modified))
    [ "$idle_time" -ge "$FLUSH_IDLE_SECONDS" ] && return 0

    return 1
}

# 2. 固化分片（不可变）
flush_tail() {
    if [ ! -f "$TAIL_FILE" ]; then
        log "ℹ️ 无需固化（tail文件不存在）"
        return 0
    fi

    # 生成part编号（按代理隔离）
    local part_num=$(ls "$MEMORY_DIR"/part*.json 2>/dev/null | wc -l)
    local part_file="$MEMORY_DIR/part$(printf '%03d' $part_num).json"

    # 会话清洗（移除元数据、系统消息）
    jq '{
        messages: [.messages[] | select(.role != "system") | {
            role: .role,
            content: .content | gsub("^\\[message_id:[^\\]]+\\]\\s*"; "")
        }]
    }' "$TAIL_FILE" > "$part_file"

    log "✅ 分片固化完成：$part_file（代理：$AGENT_NAME）"

    # 删除tail文件
    rm -f "$TAIL_FILE"
    log "🗑️ 已删除tail文件"

    # 记录统计
    local msg_count=$(jq '.messages | length' "$part_file")
    log "📊 分片统计：$msg_count 条消息（代理：$AGENT_NAME）"
}

# 3. AI 摘要（新增 v3.2.0）⭐⭐⭐⭐⭐
generate_ai_summary() {
    log "🤖 生成 AI 摘要..."

    if [ ! -f "$AI_SUMMARIZER" ]; then
        log "⚠️ AI 摘要脚本不存在，跳过"
        return 1
    fi

    # 调用 AI 摘要脚本
    if AGENT_NAME="$AGENT_NAME" bash "$AI_SUMMARIZER" >> "$LOG_FILE" 2>&1; then
        log "✅ AI 摘要生成完成（代理：$AGENT_NAME）"
        return 0
    else
        log "⚠️ AI 摘要生成失败"
        return 1
    fi
}

# 4. 更新QMD知识库（包含共享文档）
update_qmd() {
    log "📚 更新QMD知识库（代理：$AGENT_NAME + 共享文档）..."
    cd "$WORKSPACE"

    # 更新代理专属记忆
    if qmd update 2>&1 >> "$LOG_FILE"; then
        log "✅ QMD知识库更新完成"
    else
        log "⚠️ QMD更新失败"
    fi
}

# 5. 提交到Git
commit_git() {
    log "📦 检查Git变更..."
    cd "$WORKSPACE"

    git add -A 2>&1 >> "$LOG_FILE"

    # 统计变更
    local STATUS=$(git status --short)
    if [ -n "$STATUS" ]; then
        local ADD_COUNT=$(echo "$STATUS" | grep "^A" | wc -l)
        local MODIFY_COUNT=$(echo "$STATUS" | grep "^M" | wc -l)
        local DELETE_COUNT=$(echo "$STATUS" | grep "^D" | wc -l)

        local COMMIT_MSG="chore: session-memory自动更新（v3.2.0 - AI 摘要）

时间：$(date '+%Y-%m-%d %H:%M:%S')
代理：$AGENT_NAME
变更统计：
- 新增：${ADD_COUNT}个文件
- 修改：${MODIFY_COUNT}个文件
- 删除：${DELETE_COUNT}个文件

包含 AI 摘要生成"

        if git commit -m "$COMMIT_MSG" 2>&1 >> "$LOG_FILE"; then
            log "✅ Git提交完成：+${ADD_COUNT} ~${MODIFY_COUNT} -${DELETE_COUNT}（代理：$AGENT_NAME）"
        else
            log "⚠️ Git提交失败"
        fi
    else
        log "ℹ️ Git无需提交（无变更）"
    fi
}

# 主流程
main() {
    # 1. 检查是否需要固化
    if should_flush; then
        log "🔄 满足固化条件，开始处理..."
        flush_tail

        # 2. AI 摘要（固化后生成）⭐
        generate_ai_summary
    else
        log "ℹ️ 未满足固化条件（消息数<60且闲置<30分钟）"
    fi

    # 3. 更新QMD（只处理固化的分片）
    update_qmd

    # 4. 提交Git
    commit_git

    log "✅ Session-Memory Enhanced v3.2.0 完成（代理：$AGENT_NAME）"
    log "================================"
}

# 执行
main
