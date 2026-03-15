#!/bin/bash
# 实时监控脚本 v1.0
# 功能：使用 inotify 监听文件变化，实时触发更新
# 创建时间：2026-03-07 22:13
# 作者：米粒儿

WORKSPACE="/root/.openclaw/workspace"
AGENT_NAME="${AGENT_NAME:-main}"
MEMORY_DIR="$WORKSPACE/memory/agents/$AGENT_NAME"
LOG_FILE="$WORKSPACE/logs/memory-watcher.log"
SESSION_MEMORY_SCRIPT="$WORKSPACE/skills/session-memory-enhanced/scripts/session-memory-enhanced-v3.2.sh"

# 监控阈值
MAX_MESSAGES_PER_PART=60
FLUSH_IDLE_SECONDS=1800  # 30分钟

# 确保目录存在
mkdir -p "$MEMORY_DIR" "$(dirname "$LOG_FILE")"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$AGENT_NAME] $1" >> "$LOG_FILE"
}

log "================================"
log "🔍 实时监控脚本 v1.0 启动（代理：$AGENT_NAME）"
log "================================"

# 检查 inotify-tools 是否安装
check_inotify() {
    if ! command -v inotifywait &> /dev/null; then
        log "⚠️ inotify-tools 未安装，尝试安装..."
        yum install -y inotify-tools 2>&1 >> "$LOG_FILE" || apt-get install -y inotify-tools 2>&1 >> "$LOG_FILE"

        if ! command -v inotifywait &> /dev/null; then
            log "❌ inotify-tools 安装失败，使用轮询模式"
            return 1
        fi
    fi
    log "✅ inotify-tools 已安装"
    return 0
}

# 检查是否需要固化
should_flush() {
    local tail_file="$MEMORY_DIR/.tail.tmp.json"

    # 1. tail文件存在
    [ ! -f "$tail_file" ] && return 1

    # 2. 检查消息数量
    local msg_count=$(jq '.messages | length' "$tail_file" 2>/dev/null || echo "0")
    [ "$msg_count" -ge "$MAX_MESSAGES_PER_PART" ] && return 0

    # 3. 检查闲置时间
    local last_modified=$(stat -c %Y "$tail_file" 2>/dev/null || echo "0")
    local now=$(date +%s)
    local idle_time=$((now - last_modified))
    [ "$idle_time" -ge "$FLUSH_IDLE_SECONDS" ] && return 0

    return 1
}

# 触发更新
trigger_update() {
    log "🔄 触发更新..."

    if [ ! -f "$SESSION_MEMORY_SCRIPT" ]; then
        log "⚠️ session-memory-enhanced 脚本不存在"
        return 1
    fi

    # 调用 session-memory-enhanced
    if AGENT_NAME="$AGENT_NAME" bash "$SESSION_MEMORY_SCRIPT" >> "$LOG_FILE" 2>&1; then
        log "✅ 更新完成（代理：$AGENT_NAME）"
        return 0
    else
        log "⚠️ 更新失败"
        return 1
    fi
}

# inotify 监控模式
inotify_mode() {
    log "📡 启动 inotify 监控模式..."

    # 监控 .tail.tmp.json 文件
    inotifywait -m -e modify,create,delete "$MEMORY_DIR" --format '%w%f %e' | while read file event; do
        log "📝 检测到文件变化：$file ($event)"

        # 检查是否需要固化
        if should_flush; then
            log "✅ 满足固化条件，触发更新..."
            trigger_update
        fi
    done
}

# 轮询模式（备用）
polling_mode() {
    log "🔄 启动轮询模式（每5分钟检查一次）..."

    while true; do
        # 检查是否需要固化
        if should_flush; then
            log "✅ 满足固化条件，触发更新..."
            trigger_update
        fi

        # 等待5分钟
        sleep 300
    done
}

# 主流程
main() {
    # 1. 检查 inotify
    if check_inotify; then
        # 使用 inotify 监控模式
        inotify_mode
    else
        # 使用轮询模式（备用）
        polling_mode
    fi
}

# 执行
main
