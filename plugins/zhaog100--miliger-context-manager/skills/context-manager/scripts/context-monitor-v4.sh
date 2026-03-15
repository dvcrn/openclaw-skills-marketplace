#!/bin/bash
# 上下文监控脚本（v4.0 - 主动服务模式）
# 创建时间：2026-03-07 10:40
# 功能：简化监控，只关注可靠指标，主动提醒

# 修复PATH问题（cron环境）
export PATH="/root/.nvm/versions/node/v22.22.0/bin:/root/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

# 阈值配置（简化版）
TOOL_CALL_WARNING=30    # 工具调用提醒阈值（30次）
TOOL_CALL_CRITICAL=50   # 工具调用严重阈值（50次）
HOUR_CHECK=true         # 是否进行每小时检查

# 路径配置
LOG_FILE="$HOME/.openclaw/workspace/logs/context-monitor-v4.log"
FEISHU_TARGET="user:ou_64e8948aedd09549e512218c96702830"
QQ_TARGET="qqbot:c2c:1478D4753463307D2E176B905A8B7F5E"
OPENCLAW_LOG="/tmp/openclaw/openclaw-$(date +%Y-%m-%d).log"
COOLDOWN_FILE="/tmp/context-notification-cooldown-v4"
NOTIFICATION_COOLDOWN=3600  # 1小时冷却期

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
            log "⏸️ 冷却期中（距上次${elapsed}秒）"
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
    
    # 飞书通知
    if openclaw message send --channel feishu --target "$FEISHU_TARGET" --message "$message" 2>&1 >> "$LOG_FILE"; then
        log "✅ 飞书通知成功"
    else
        log "⚠️ 飞书通知失败"
    fi
    
    # QQ通知（警告和紧急级别）
    if [ "$level" == "WARNING" ] || [ "$level" == "CRITICAL" ]; then
        if openclaw message send --channel qqbot --target "$QQ_TARGET" --message "$message" 2>&1 >> "$LOG_FILE"; then
            log "✅ QQ通知成功"
        else
            log "⚠️ QQ通知失败"
        fi
    fi
    
    set_cooldown
}

# 检查1：工具调用次数（唯一可靠指标）
check_tool_calls() {
    log "🔧 检查工具调用次数..."
    
    if [ ! -f "$OPENCLAW_LOG" ]; then
        log "⚠️ OpenClaw日志不存在，跳过检查"
        return 0
    fi
    
    # 统计最近1小时的工具调用（关键词：[tools]）
    local one_hour_ago=$(date -d '1 hour ago' +%s)
    local tool_calls=$(grep '\[tools\]' "$OPENCLAW_LOG" | tail -200 | while read line; do
        # 提取时间戳（格式：2026-03-07T10:00:00.000Z）
        local timestamp=$(echo "$line" | grep -oP '"time":"\K[^"]+')
        if [ -n "$timestamp" ]; then
            # 转换时间戳
            local log_time=$(date -d "${timestamp}" +%s 2>/dev/null || echo "0")
            if [ "$log_time" -ge "$one_hour_ago" ]; then
                echo "$line"
            fi
        fi
    done | wc -l)
    
    log "📊 最近1小时工具调用：${tool_calls}次"
    
    # 严重预警（50次）
    if [ "$tool_calls" -ge "$TOOL_CALL_CRITICAL" ]; then
        log "🚨 工具调用过多！(${tool_calls}次 >= 50次)"
        
        if is_in_cooldown; then
            return 0
        fi
        
        local message="🚨 工具调用严重预警\n\n次数：${tool_calls}次（最近1小时）\n阈值：50次\n\n💡 建议：\n1. 使用QMD精准检索（减少读取）\n2. 考虑发送 /new 开始新会话\n\n原因：工具调用过多会导致隐藏上下文累积"
        send_notification "CRITICAL" "$message"
        return 1
    fi
    
    # 提醒（30次）
    if [ "$tool_calls" -ge "$TOOL_CALL_WARNING" ]; then
        log "⚠️ 工具调用较频繁！(${tool_calls}次 >= 30次)"
        
        if is_in_cooldown; then
            return 0
        fi
        
        local message="⚠️ 工具调用提醒\n\n次数：${tool_calls}次（最近1小时）\n提醒阈值：30次\n\n💡 建议：\n1. 注意工具调用频率\n2. 使用QMD精准检索\n3. 如已长时间会话，考虑 /new"
        send_notification "WARNING" "$message"
        return 0
    fi
    
    log "✅ 工具调用频率正常"
    return 0
}

# 检查2：错误检测（实时监控）
check_errors() {
    log "🔍 检查OpenClaw错误..."
    
    if [ ! -f "$OPENCLAW_LOG" ]; then
        log "⚠️ OpenClaw日志不存在，跳过检查"
        return 0
    fi
    
    # 检查最近5分钟的错误（关键词：model_context_window_exceeded）
    local five_min_ago=$(date -d '5 minutes ago' +%s)
    local error_count=$(grep 'model_context_window_exceeded' "$OPENCLAW_LOG" | tail -50 | while read line; do
        local timestamp=$(echo "$line" | grep -oP '"time":"\K[^"]+')
        if [ -n "$timestamp" ]; then
            local log_time=$(date -d "${timestamp}" +%s 2>/dev/null || echo "0")
            if [ "$log_time" -ge "$five_min_ago" ]; then
                echo "$line"
            fi
        fi
    done | wc -l)
    
    if [ "$error_count" -gt 0 ]; then
        log "🚨 检测到上下文超限错误！(${error_count}次)"
        
        # 紧急通知，不检查冷却期
        local message="🚨 上下文超限紧急通知\n\n检测到 ${error_count} 次超限错误\n时间：最近5分钟\n\n💡 立即发送 /new 开始新会话\n\n原因：隐藏上下文（工具调用结果）导致实际超限"
        send_notification "CRITICAL" "$message"
        return 1
    fi
    
    log "✅ 未检测到错误"
    return 0
}

# 主函数
main() {
    log "🔍 ===== 开始v4.0监控（主动服务模式） ====="
    
    # 只检查两个可靠指标
    check_tool_calls
    local tool_status=$?
    
    check_errors
    local error_status=$?
    
    # 汇总
    if [ $tool_status -eq 0 ] && [ $error_status -eq 0 ]; then
        log "✅ 系统正常"
    else
        log "⚠️ 发现问题，已发送通知"
    fi
    
    log "✅ ===== 监控完成 =====\n"
}

main
