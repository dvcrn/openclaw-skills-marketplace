#!/bin/bash
# 上下文监控脚本（v5.0 - 智能分层 + 预测性提醒）
# 创建时间：2026-03-07 10:47
# 功能：智能触发、分层监控、预测性提醒、用户友好通知
# 参考：Hazel_OC的token优化经验（减少78%消耗）

# 修复PATH问题（cron环境）
export PATH="/root/.nvm/versions/node/v22.22.0/bin:/root/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

# 阈值配置（智能分层）
LIGHT_THRESHOLD=10        # 轻量阈值（5分钟内10次工具调用）
HEAVY_THRESHOLD=30        # 重量阈值（1小时内30次）
CRITICAL_THRESHOLD=50     # 严重阈值（1小时内50次）
ACTIVITY_TIMEOUT=1800     # 活动超时（30分钟）

# 路径配置
LOG_FILE="$HOME/.openclaw/workspace/logs/context-monitor-v5.log"
FEISHU_TARGET="user:ou_64e8948aedd09549e512218c96702830"
QQ_TARGET="qqbot:c2c:1478D4753463307D2E176B905A8B7F5E"
OPENCLAW_LOG="/tmp/openclaw/openclaw-$(date +%Y-%m-%d).log"
ACTIVITY_FILE="/tmp/context-activity-tracker"
COOLDOWN_FILE="/tmp/context-notification-cooldown-v5"
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

# 检查是否有用户活动（智能触发）
check_user_activity() {
    log "🔍 检查用户活动..."
    
    if [ ! -f "$OPENCLAW_LOG" ]; then
        log "⚠️ OpenClaw日志不存在"
        return 1
    fi
    
    # 检查最近5分钟是否有用户消息（关键词：用户、消息、qqbot）
    local five_min_ago=$(date -d '5 minutes ago' +%s)
    local user_activity=$(tail -100 "$OPENCLAW_LOG" | grep -E "用户|消息|qqbot|ROBOT" | while read line; do
        local timestamp=$(echo "$line" | grep -oP '"time":"\K[^"]+')
        if [ -n "$timestamp" ]; then
            local log_time=$(date -d "${timestamp}" +%s 2>/dev/null || echo "0")
            if [ "$log_time" -ge "$five_min_ago" ]; then
                echo "$line"
            fi
        fi
    done | wc -l)
    
    if [ "$user_activity" -gt 0 ]; then
        log "✅ 检测到用户活动（${user_activity}次）"
        echo "$user_activity" > "$ACTIVITY_FILE"
        return 0
    else
        log "⏸️ 无用户活动，跳过检查（节省token）"
        return 1
    fi
}

# 第一层：轻量检查（快速判断）
lightweight_check() {
    log "⚡ 第一层：轻量检查..."
    
    if [ ! -f "$OPENCLAW_LOG" ]; then
        return 0
    fi
    
    # 只统计最近5分钟的日志行数（不解析内容）
    local five_min_ago=$(date -d '5 minutes ago' +%s)
    local log_lines=$(tail -50 "$OPENCLAW_LOG" | wc -l)
    
    # 估算工具调用次数（简单统计）
    local tool_calls=$(tail -50 "$OPENCLAW_LOG" | grep -c '\[tools\]')
    
    log "📊 轻量统计：${log_lines}行日志，约${tool_calls}次工具调用（5分钟内）"
    
    # 轻量阈值判断
    if [ "$tool_calls" -ge "$LIGHT_THRESHOLD" ]; then
        log "⚠️ 轻量检查发现异常（${tool_calls}次 >= ${LIGHT_THRESHOLD}次）"
        return 1
    fi
    
    log "✅ 轻量检查正常"
    return 0
}

# 第二层：详细检查（深入分析）
detailed_check() {
    log "🔬 第二层：详细检查..."
    
    if [ ! -f "$OPENCLAW_LOG" ]; then
        return 0
    fi
    
    # 统计最近1小时的工具调用
    local one_hour_ago=$(date -d '1 hour ago' +%s)
    local tool_calls=$(grep '\[tools\]' "$OPENCLAW_LOG" | tail -200 | while read line; do
        local timestamp=$(echo "$line" | grep -oP '"time":"\K[^"]+')
        if [ -n "$timestamp" ]; then
            local log_time=$(date -d "${timestamp}" +%s 2>/dev/null || echo "0")
            if [ "$log_time" -ge "$one_hour_ago" ]; then
                echo "$line"
            fi
        fi
    done | wc -l)
    
    log "📊 详细统计：${tool_calls}次工具调用（1小时内）"
    
    # 严重预警（50次）
    if [ "$tool_calls" -ge "$CRITICAL_THRESHOLD" ]; then
        log "🚨 严重预警！(${tool_calls}次 >= ${CRITICAL_THRESHOLD}次)"
        
        if is_in_cooldown; then
            return 0
        fi
        
        local message="🚨 会话活动频繁提醒\n\n检测：最近1小时${tool_calls}次工具调用\n\n💡 建议：\n1. 使用QMD精准检索（减少读取）\n2. 考虑发送 /new 开始新会话\n\n原因：工具调用过多会导致隐藏上下文累积"
        send_notification "CRITICAL" "$message"
        return 1
    fi
    
    # 重量预警（30次）
    if [ "$tool_calls" -ge "$HEAVY_THRESHOLD" ]; then
        log "⚠️ 重量预警！(${tool_calls}次 >= ${HEAVY_THRESHOLD}次)"
        
        if is_in_cooldown; then
            return 0
        fi
        
        local message="⚠️ 会话较活跃提醒\n\n检测：最近1小时${tool_calls}次工具调用\n\n💡 建议：\n1. 注意工具调用频率\n2. 使用QMD精准检索\n3. 如会话超过2小时，考虑 /new"
        send_notification "WARNING" "$message"
        return 0
    fi
    
    log "✅ 详细检查正常"
    return 0
}

# 预测性分析（趋势判断）
predictive_analysis() {
    log "🔮 预测性分析..."
    
    if [ ! -f "$ACTIVITY_FILE" ]; then
        return 0
    fi
    
    # 读取历史活动数据（简化版：只记录最近几次）
    local current_activity=$(cat "$ACTIVITY_FILE" 2>/dev/null || echo "0")
    
    # 趋势判断：如果活动频率在增加
    if [ "$current_activity" -gt 5 ]; then
        log "📈 检测到活动趋势上升"
        
        # 记录活动时间戳
        local now=$(date +%s)
        echo "$now:$current_activity" >> "$ACTIVITY_FILE.history"
        
        # 检查最近30分钟的活动历史
        local recent_count=$(tail -10 "$ACTIVITY_FILE.history" | wc -l)
        if [ "$recent_count" -ge 3 ]; then
            log "⚠️ 持续高频活动（最近30分钟${recent_count}次）"
            
            if is_in_cooldown; then
                return 0
            fi
            
            local message="📊 会话趋势分析\n\n检测：持续高频活动\n频率：最近30分钟${recent_count}次活动\n\n💡 建议：\n1. 考虑使用QMD精准检索\n2. 2小时后建议开始新会话\n\n预防胜于治疗 🎯"
            send_notification "INFO" "$message"
            return 0
        fi
    fi
    
    log "✅ 预测性分析正常"
    return 0
}

# 错误检测（实时监控）
check_errors() {
    log "🔍 检查OpenClaw错误..."
    
    if [ ! -f "$OPENCLAW_LOG" ]; then
        return 0
    fi
    
    # 检查最近5分钟的错误
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
        log "🚨 检测到错误！(${error_count}次)"
        
        # 紧急通知，不检查冷却期
        local message="🚨 上下文紧急提醒\n\n检测到 ${error_count} 次超限错误\n时间：最近5分钟\n\n💡 立即发送 /new 开始新会话\n\n原因：隐藏上下文导致实际超限"
        send_notification "CRITICAL" "$message"
        return 1
    fi
    
    log "✅ 未检测到错误"
    return 0
}

# 主函数（智能触发 + 分层监控）
main() {
    log "🔍 ===== 开始v5.0监控（智能分层 + 预测性） ====="
    
    # 智能触发：只检查错误（无活动也检查）
    check_errors
    local error_status=$?
    
    # 检查用户活动
    if ! check_user_activity; then
        log "⏸️ 无用户活动，跳过详细检查（节省token）"
        log "✅ ===== 监控完成（轻量模式） =====\n"
        exit 0
    fi
    
    # 第一层：轻量检查
    lightweight_check
    local light_status=$?
    
    # 如果轻量检查发现异常，进入第二层
    if [ $light_status -ne 0 ]; then
        detailed_check
        local detailed_status=$?
    fi
    
    # 预测性分析
    predictive_analysis
    
    # 汇总
    if [ $error_status -eq 0 ] && [ $light_status -eq 0 ]; then
        log "✅ 系统正常"
    else
        log "⚠️ 发现潜在问题，已发送通知"
    fi
    
    log "✅ ===== 监控完成 =====\n"
}

main
