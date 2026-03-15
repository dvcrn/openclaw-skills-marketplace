#!/bin/bash
# 上下文监控脚本（增强版 v3.0）
# 创建时间：2026-03-06 23:12
# 功能：多重预警机制（时间 + 工具调用 + 使用率），主动预防上下文超限

# 修复PATH问题（cron环境）
export PATH="/root/.nvm/versions/node/v22.22.0/bin:/root/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

# 阈值配置（更保守的策略）
CONTEXT_THRESHOLD=60       # 上下文使用率阈值（60%就开始预警，但不准确）
TIME_THRESHOLD=10800       # 会话时长阈值（3小时 = 10800秒，更可靠）
TIME_WARNING=7200          # 会话时长警告（2小时 = 7200秒）
TOOL_CALL_THRESHOLD=50     # 工具调用严重阈值
TOOL_CALL_AGGRESSIVE=30    # 工具调用提醒阈值

LOG_FILE="$HOME/.openclaw/workspace/logs/context-monitor-enhanced.log"
FEISHU_TARGET="user:ou_64e8948aedd09549e512218c96702830"
QQ_TARGET="qqbot:c2c:1478D4753463307D2E176B905A8B7F5E"
OPENCLAW_LOG="/tmp/openclaw/openclaw-$(date +%Y-%m-%d).log"
COOLDOWN_FILE="/tmp/context-notification-cooldown"
NOTIFICATION_COOLDOWN=3600  # 1小时冷却期（秒）

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
            log "⏸️ 冷却期中（距上次通知${elapsed}秒）"
            return 0
        fi
    fi
    return 1
}

# 设置冷却期
set_cooldown() {
    date +%s > "$COOLDOWN_FILE"
    log "🔒 设置冷却期（1小时）"
}

# 发送通知（飞书 + QQ）
send_notification() {
    local level="$1"
    local message="$2"
    
    log "📤 发送${level}级通知..."
    log "通知内容：$message"
    
    # 尝试飞书通知
    if openclaw message send --channel feishu --target "$FEISHU_TARGET" --message "$message" 2>&1 >> "$LOG_FILE"; then
        log "✅ 飞书通知发送成功"
    else
        log "⚠️ 飞书通知发送失败（跳过）"
    fi
    
    # 尝试QQ通知（仅警告和紧急）
    if [ "$level" == "WARNING" ] || [ "$level" == "CRITICAL" ]; then
        if openclaw message send --channel qqbot --target "$QQ_TARGET" --message "$message" 2>&1 >> "$LOG_FILE"; then
            log "✅ QQ通知发送成功"
        else
            log "⚠️ QQ通知发送失败（跳过）"
        fi
    fi
    
    set_cooldown
    log "📋 通知已记录到日志（即使发送失败也会在日志中查看）"
}

# 获取当前会话信息
get_session_info() {
    log "📊 获取会话信息..."
    
    local sessions_json
    sessions_json=$(openclaw sessions --active 120 --json 2>&1)
    
    if [ $? -ne 0 ]; then
        log "⚠️ 获取会话列表失败"
        return 1
    fi
    
    # 提取QQ会话信息（使用更简单的方式）
    local session_info=$(echo "$sessions_json" | jq -r '.sessions[] | select(.key | contains("qqbot")) | @base64' | head -1)
    
    if [ -z "$session_info" ]; then
        log "⚠️ 未找到QQ会话"
        return 1
    fi
    
    echo "$session_info"
    return 0
}

# 检查1：会话时长
check_session_duration() {
    log "⏱️ 检查会话时长..."
    
    local session_base64=$(get_session_info)
    if [ -z "$session_base64" ]; then
        log "⚠️ 无活跃会话"
        return 0
    fi
    
    # 解码JSON
    local session_info=$(echo "$session_base64" | base64 -d)
    local updated_at=$(echo "$session_info" | jq -r '.updatedAt // 0')
    
    # 计算时长（updatedAt是毫秒时间戳）
    local current_time_ms=$(($(date +%s) * 1000))
    local duration_ms=$((current_time_ms - updated_at))
    local duration_sec=$((duration_ms / 1000))
    local duration_hours=$((duration_sec / 3600))
    local duration_min=$(((duration_sec % 3600) / 60))
    
    log "📊 会话时长：${duration_hours}小时${duration_min}分钟"

    # 2小时警告
    if [ "$duration_sec" -ge "$TIME_WARNING" ]; then
        log "⚠️ 会话较长！(${duration_hours}小时 >= 2小时)"

        if is_in_cooldown; then
            return 0
        fi

        local message="⏰ 会话时长提醒\n\n时长：${duration_hours}小时${duration_min}分钟\n提醒阈值：2小时\n\n💡 建议：\n1. 注意上下文累积\n2. 使用QMD精准检索\n3. 考虑发送 /new 开始新会话"
        send_notification "INFO" "$message"
        return 0
    fi

    # 3小时严重警告
    if [ "$duration_sec" -ge "$TIME_THRESHOLD" ]; then
        log "🚨 会话过长！(${duration_hours}小时 >= 3小时)"
        
        if is_in_cooldown; then
            return 0
        fi
        
        local message="⏰ 会话时长预警\n\n时长：${duration_hours}小时${duration_min}分钟\n阈值：6小时\n\n💡 建议发送 /new 开始新会话\n\n原因：长时间会话容易导致上下文累积超限"
        send_notification "WARNING" "$message"
        return 1
    fi
    
    log "✅ 会话时长正常"
    return 0
}

# 检查2：工具调用次数
check_tool_calls() {
    log "🔧 检查工具调用次数..."
    
    if [ ! -f "$OPENCLAW_LOG" ]; then
        log "⚠️ OpenClaw日志文件不存在"
        return 0
    fi
    
    # 统计最近1小时的工具调用次数
    local one_hour_ago=$(date -d '1 hour ago' +%s)
    local tool_calls=$(grep "run tool start" "$OPENCLAW_LOG" | tail -100 | while read line; do
        local timestamp=$(echo "$line" | grep -oP '"time":"\K[^"]+')
        if [ -n "$timestamp" ]; then
            local log_time=$(date -d "$timestamp" +%s 2>/dev/null || echo "0")
            if [ "$log_time" -ge "$one_hour_ago" ]; then
                echo "$line"
            fi
        fi
    done | wc -l)
    
    log "📊 最近1小时工具调用：${tool_calls}次"

    # 激进预警（30次）
    if [ "$tool_calls" -ge "$TOOL_CALL_AGGRESSIVE" ]; then
        log "⚠️ 工具调用较频繁！(${tool_calls}次 >= ${TOOL_CALL_AGGRESSIVE}次)"

        if is_in_cooldown; then
            return 0
        fi

        local message="🔧 工具调用频繁提醒\n\n次数：${tool_calls}次\n阈值：${TOOL_CALL_AGGRESSIVE}次\n\n💡 建议：\n1. 注意上下文累积\n2. 使用QMD精准检索（减少读取）\n3. 如会话超过3小时，考虑 /new"
        send_notification "INFO" "$message"
        return 0
    fi

    # 严重预警（50次）
    if [ "$tool_calls" -ge "$TOOL_CALL_THRESHOLD" ]; then
        log "🚨 工具调用过于频繁！(${tool_calls}次 >= ${TOOL_CALL_THRESHOLD}次)"
        
        if is_in_cooldown; then
            return 0
        fi
        
        local message="🔧 工具调用预警\n\n次数：${tool_calls}次（最近1小时）\n阈值：${TOOL_CALL_THRESHOLD}次\n\n💡 建议：\n1. 使用QMD精准检索替代全量读取\n2. 减少不必要的工具调用\n3. 考虑 /new 开始新会话"
        send_notification "WARNING" "$message"
        return 1
    fi
    
    log "✅ 工具调用频率正常"
    return 0
}

# 检查3：上下文使用率
check_context_usage() {
    log "📊 检查上下文使用率..."
    
    local session_base64=$(get_session_info)
    if [ -z "$session_base64" ]; then
        log "⚠️ 无活跃会话"
        return 0
    fi
    
    # 解码JSON
    local session_info=$(echo "$session_base64" | base64 -d)
    local total_tokens=$(echo "$session_info" | jq -r '.totalTokens // 0')
    local context_tokens=$(echo "$session_info" | jq -r '.contextTokens // 205000')
    
    if [ "$context_tokens" -gt 0 ]; then
        local usage=$((total_tokens * 100 / context_tokens))
        log "📊 上下文使用率：${usage}%（${total_tokens}/${context_tokens} tokens）"
        
        if [ "$usage" -ge "$CONTEXT_THRESHOLD" ]; then
            log "🚨 上下文超限！(${usage}% >= ${CONTEXT_THRESHOLD}%)"
            
            if is_in_cooldown; then
                return 0
            fi
            
            local message="🚨 上下文紧急预警\n\n使用率：${usage}%\n阈值：${CONTEXT_THRESHOLD}%\n\n💡 必须立即发送 /new 开始新会话"
            send_notification "CRITICAL" "$message"
            return 1
        fi
        
        log "✅ 上下文使用率正常"
    fi
    
    return 0
}

# 主函数
main() {
    log "🔍 ===== 开始增强版上下文监控 ====="
    
    # 三重检查
    check_session_duration
    local duration_status=$?
    
    check_tool_calls
    local tool_status=$?
    
    check_context_usage
    local usage_status=$?
    
    # 汇总
    if [ $duration_status -eq 0 ] && [ $tool_status -eq 0 ] && [ $usage_status -eq 0 ]; then
        log "✅ 所有检查通过，系统正常"
    else
        log "⚠️ 发现潜在风险，已发送通知"
    fi
    
    log "✅ ===== 监控完成 =====\n"
}

main
