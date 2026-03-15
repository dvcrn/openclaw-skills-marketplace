#!/bin/bash
# 实时监控脚本 v2.0 - 防抖 + PID 锁
# 功能：使用 inotify 监听文件变化，实时触发更新（带防抖和PID锁）
# 改进：借鉴 memu-engine 的防抖机制和 PID 锁机制
# 创建时间：2026-03-07 22:40
# 作者：米粒儿

WORKSPACE="/root/.openclaw/workspace"
AGENT_NAME="${AGENT_NAME:-main}"
MEMORY_DIR="$WORKSPACE/memory/agents/$AGENT_NAME"
LOG_FILE="$WORKSPACE/logs/memory-watcher.log"
SESSION_MEMORY_SCRIPT="$WORKSPACE/skills/session-memory-enhanced/scripts/session-memory-enhanced-v3.4.sh"

# 监控阈值
MAX_MESSAGES_PER_PART=60
FLUSH_IDLE_SECONDS=1800  # 30分钟

# 防抖配置 ⭐⭐⭐⭐⭐
DEBOUNCE_SECONDS=20  # 防抖时间（借鉴 memu-engine）
LAST_RUN=0

# PID 锁配置 ⭐⭐⭐⭐⭐
LOCK_FILE="/tmp/memory-watcher-${AGENT_NAME}.lock"
LOCK_HANDLE=""

# 确保目录存在
mkdir -p "$MEMORY_DIR" "$(dirname "$LOG_FILE")"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$AGENT_NAME] $1" >> "$LOG_FILE"
}

log "================================"
log "🔍 实时监控脚本 v2.0 启动（代理：$AGENT_NAME）"
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

# PID 锁机制（借鉴 memu-engine）⭐⭐⭐⭐⭐
try_acquire_lock() {
    # 检查锁文件是否存在
    if [ -f "$LOCK_FILE" ]; then
        local pid=$(cat "$LOCK_FILE" 2>/dev/null)
        
        # 检查进程是否还在运行
        if [ -n "$pid" ] && [ "$pid" -gt 1 ]; then
            if kill -0 "$pid" 2>/dev/null; then
                log "🔒 另一个进程正在运行（PID: $pid），跳过"
                return 1
            else
                log "🧹 清理僵尸锁（PID: $pid 已不存在）"
                rm -f "$LOCK_FILE"
            fi
        fi
    fi
    
    # 尝试获取锁（使用 O_EXCL 确保原子性）
    local lock_fd
    exec {lock_fd}>"$LOCK_FILE" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo $$ >&$lock_fd
        LOCK_HANDLE=$lock_fd
        log "✅ 获取锁成功（PID: $$）"
        return 0
    else
        log "⚠️ 获取锁失败"
        return 1
    fi
}

# 释放锁
release_lock() {
    if [ -n "$LOCK_HANDLE" ]; then
        exec {LOCK_HANDLE}>&-
        LOCK_HANDLE=""
    fi
    rm -f "$LOCK_FILE"
    log "🔓 释放锁"
}

# 防抖机制（借鉴 memu-engine）⭐⭐⭐⭐⭐
check_debounce() {
    local now=$(date +%s)
    local elapsed=$((now - LAST_RUN))
    
    if [ $elapsed -lt $DEBOUNCE_SECONDS ]; then
        local remaining=$((DEBOUNCE_SECONDS - elapsed))
        log "⏸️ 防抖中（剩余 ${remaining}秒），跳过"
        return 1
    fi
    
    return 0
}

# 触发更新（带防抖和PID锁）⭐⭐⭐⭐⭐
trigger_update() {
    # 1. 防抖检查
    if ! check_debounce; then
        return 1
    fi
    
    # 2. 获取 PID 锁
    if ! try_acquire_lock; then
        return 1
    fi
    
    # 3. 执行更新
    log "🔄 触发更新..."

    if [ ! -f "$SESSION_MEMORY_SCRIPT" ]; then
        log "⚠️ session-memory-enhanced 脚本不存在"
        release_lock
        return 1
    fi

    # 调用 session-memory-enhanced
    if AGENT_NAME="$AGENT_NAME" bash "$SESSION_MEMORY_SCRIPT" >> "$LOG_FILE" 2>&1; then
        log "✅ 更新完成（代理：$AGENT_NAME）"
        LAST_RUN=$(date +%s)
        release_lock
        return 0
    else
        log "⚠️ 更新失败"
        release_lock
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

# 清理函数
cleanup() {
    log "🛑 接收到退出信号，清理资源..."
    release_lock
    exit 0
}

# 注册信号处理
trap cleanup SIGINT SIGTERM

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
