#!/bin/bash
# 上下文监控脚本（API版）
# 创建时间：2026-03-04
# 更新时间：2026-03-06 10:19
# 功能：通过OpenClaw API监控真实上下文使用率，超过85%自动发送飞书通知

# ⭐ 修复cron环境问题（2026-03-06）
export HOME="/home/zhaog"
export PATH="/home/zhaog/.npm-global/bin:$PATH"

THRESHOLD=85
LOG_FILE="$HOME/.openclaw/workspace/logs/context-monitor.log"
FEISHU_TARGET="user:ou_64e8948aedd09549e512218c96702830"
NOTIFICATION_COOLDOWN=3600  # 1小时冷却期（秒）
COOLDOWN_FILE="/tmp/context-notification-cooldown"

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 检查冷却期
is_in_cooldown() {
    if [ -f "$COOLDOWN_FILE" ]; then
        local last_notification=$(cat "$COOLDOWN_FILE" 2>/dev/null || echo "0")
        local current_time=$(date +%s)
        local elapsed=$((current_time - last_notification))
        
        if [ "$elapsed" -lt "$NOTIFICATION_COOLDOWN" ]; then
            log "⏸️ 冷却期中（距上次通知${elapsed}秒，需${NOTIFICATION_COOLDOWN}秒）"
            return 0  # 在冷却期
        fi
    fi
    return 1  # 不在冷却期
}

# 设置冷却期
set_cooldown() {
    date +%s > "$COOLDOWN_FILE"
    log "🔒 设置通知冷却期（1小时）"
}

# 发送飞书通知
send_feishu_notification() {
    local message="$1"
    log "📤 发送飞书通知: $message"
    
    # 使用openclaw message tool发送通知
    openclaw message send --channel feishu --account main --target "$FEISHU_TARGET" --message "$message" 2>&1 >> "$LOG_FILE"
    
    # 设置冷却期
    set_cooldown
}

# 获取真实上下文使用率（通过OpenClaw API）
get_context_usage() {
    log "📊 调用OpenClaw API获取会话信息..."
    
    # 获取最近2小时的活跃会话
    local sessions_json
    sessions_json=$(openclaw sessions --active 120 --json 2>&1)
    
    if [ $? -ne 0 ]; then
        log "⚠️ 获取会话列表失败"
        echo "0"
        return 1
    fi
    
    # 提取第一个会话的信息
    local session_info=$(echo "$sessions_json" | jq '.sessions[0]')
    local total_tokens=$(echo "$session_info" | jq -r '.totalTokens // 0')
    local context_tokens=$(echo "$session_info" | jq -r '.contextTokens // 202752')
    local session_key=$(echo "$session_info" | jq -r '.key // "unknown"')
    local model=$(echo "$session_info" | jq -r '.model // "unknown"')
    
    log "📝 会话: $session_key"
    log "🤖 模型: $model"
    log "📊 当前Tokens: $total_tokens / $context_tokens"
    
    # 计算使用率
    if [ "$context_tokens" -gt 0 ]; then
        local usage=$((total_tokens * 100 / context_tokens))
        log "✅ 上下文使用率: ${usage}%"
        echo "$usage"
        return 0
    else
        log "⚠️ 上下文大小为0，使用默认值"
        echo "0"
        return 1
    fi
}

# 检查上下文使用率
check_context() {
    local usage=$(get_context_usage)
    local status=$?
    
    if [ $status -ne 0 ]; then
        log "⚠️ 无法获取上下文使用率，使用估算值: ${usage}%"
    fi
    
    # 判断是否超过阈值
    if [ "$usage" -ge "$THRESHOLD" ]; then
        log "🚨 上下文超限！(${usage}% >= ${THRESHOLD}%)"
        
        # 检查冷却期
        if is_in_cooldown; then
            log "⏸️ 在冷却期，跳过通知"
            return 0
        fi
        
        # 发送飞书通知
        local message="🚨 上下文警告\n\n当前使用率：${usage}%\n阈值：${THRESHOLD}%\n\n💡 建议立即发送 /new 开始新会话\n\n⏰ 检查时间：$(date '+%Y-%m-%d %H:%M:%S')"
        send_feishu_notification "$message"
    else
        log "✅ 上下文正常（${usage}% < ${THRESHOLD}%）"
    fi
}

# 主函数
main() {
    log "🔍 ===== 开始上下文监控检查 ====="
    check_context
    log "✅ ===== 检查完成 =====\n"
}

main
