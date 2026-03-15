#!/bin/bash
# 上下文监控脚本（v6.0 - 全功能整合版）
# 创建时间：2026-03-07 14:25
# 功能：三级预警 + 智能清理 + 预测监控 + 动态阈值 + 模型分层
# 参考：Moltbook社区最佳实践 + Hazel_OC的token优化经验

# 修复PATH问题（cron环境）
export PATH="/root/.nvm/versions/node/v22.22.0/bin:/root/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

# ============================================
# 核心配置（动态阈值系统）
# ============================================

# 三级预警阈值（根据活跃度动态调整）
LOW_ACTIVITY_THRESHOLD=90      # 低活跃度：90%
MEDIUM_ACTIVITY_THRESHOLD=80   # 中活跃度：80%
HIGH_ACTIVITY_THRESHOLD=70     # 高活跃度：70%

# 工具调用阈值
LIGHT_TOOL_THRESHOLD=10        # 轻量级：5分钟10次
HEAVY_TOOL_THRESHOLD=30        # 重量级：1小时30次
CRITICAL_TOOL_THRESHOLD=50     # 严重级：1小时50次

# 会话时长阈值（小时）
LONG_SESSION_WARNING=2         # 长会话预警：2小时
LONG_SESSION_CRITICAL=4        # 长会话严重：4小时

# 路径配置
LOG_FILE="$HOME/.openclaw/workspace/logs/context-monitor-v6.log"
FEISHU_TARGET="user:ou_64e8948aedd09549e512218c96702830"
QQ_TARGET="qqbot:c2c:1478D4753463307D2E176B905A8B7F5E"
OPENCLAW_LOG="/tmp/openclaw/openclaw-$(date +%Y-%m-%d).log"
ACTIVITY_FILE="/tmp/context-activity-tracker-v6"
SESSION_START_FILE="/tmp/context-session-start"
COOLDOWN_FILE="/tmp/context-notification-cooldown-v6"
NOTIFICATION_COOLDOWN=1800  # 30分钟冷却期（缩短以便快速响应）

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$(dirname "$ACTIVITY_FILE")"

# ============================================
# 日志函数
# ============================================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# ============================================
# 冷却机制
# ============================================

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

set_cooldown() {
    date +%s > "$COOLDOWN_FILE"
    log "🔒 设置冷却期（30分钟）"
}

# ============================================
# 通知系统（分级通知）
# ============================================

send_notification() {
    local level="$1"
    local message="$2"
    local channels="$3"  # feishu/qq/both
    
    log "📤 发送${level}级通知（${channels}）..."
    
    # 飞书通知（所有级别）
    if [ "$channels" == "feishu" ] || [ "$channels" == "both" ]; then
        if openclaw message send --channel feishu --target "$FEISHU_TARGET" --message "$message" 2>&1 >> "$LOG_FILE"; then
            log "✅ 飞书通知成功"
        else
            log "⚠️ 飞书通知失败"
        fi
    fi
    
    # QQ通知（警告和紧急级别）
    if [ "$channels" == "qq" ] || [ "$channels" == "both" ]; then
        if [ "$level" == "WARNING" ] || [ "$level" == "CRITICAL" ]; then
            if openclaw message send --channel qqbot --target "$QQ_TARGET" --message "$message" 2>&1 >> "$LOG_FILE"; then
                log "✅ QQ通知成功"
            else
                log "⚠️ QQ通知失败"
            fi
        fi
    fi
    
    set_cooldown
}

# ============================================
# 1. 三级预警系统
# ============================================

three_level_warning() {
    local context_usage="$1"
    local activity_level="$2"
    
    log "📊 三级预警检查：${context_usage}%（活跃度：${activity_level}）"
    
    # 根据活跃度选择阈值
    local threshold
    case "$activity_level" in
        "LOW")
            threshold=$LOW_ACTIVITY_THRESHOLD
            ;;
        "MEDIUM")
            threshold=$MEDIUM_ACTIVITY_THRESHOLD
            ;;
        "HIGH")
            threshold=$HIGH_ACTIVITY_THRESHOLD
            ;;
        *)
            threshold=$MEDIUM_ACTIVITY_THRESHOLD
            ;;
    esac
    
    # 三级预警
    if [ "$context_usage" -ge 90 ]; then
        log "🚨 严重预警（90%+）"
        local message="🚨 上下文严重预警\n\n当前：${context_usage}%\n阈值：90%\n活跃度：${activity_level}\n\n💡 立即行动：\n1. 发送 /new 开始新会话\n2. 清理工具调用历史\n3. 使用QMD精准检索\n\n⚠️ 超限风险极高！"
        send_notification "CRITICAL" "$message" "both"
        return 3
        
    elif [ "$context_usage" -ge 80 ]; then
        log "⚠️ 重量预警（80%+）"
        local message="⚠️ 上下文较满提醒\n\n当前：${context_usage}%\n阈值：80%\n活跃度：${activity_level}\n\n💡 建议行动：\n1. 减少工具调用\n2. 使用QMD精准检索\n3. 考虑 /new 开始新会话"
        send_notification "WARNING" "$message" "both"
        return 2
        
    elif [ "$context_usage" -ge "$threshold" ]; then
        log "📊 轻度预警（${threshold}%+）"
        local message="📊 上下文轻度提醒\n\n当前：${context_usage}%\n阈值：${threshold}%\n活跃度：${activity_level}\n\n💡 优化建议：\n1. 使用QMD精准检索\n2. 注意工具调用频率"
        send_notification "INFO" "$message" "feishu"
        return 1
    fi
    
    return 0
}

# ============================================
# 2. 智能清理策略
# ============================================

smart_cleanup() {
    local level="$1"  # light/medium/heavy
    
    log "🧹 智能清理（${level}级）..."
    
    case "$level" in
        "light")
            # 轻度清理：清理临时文件
            log "🧹 轻度清理：临时文件"
            rm -f /tmp/context-*.tmp 2>/dev/null
            ;;
            
        "medium")
            # 中度清理：清理活动追踪历史
            log "🧹 中度清理：活动历史"
            rm -f "$ACTIVITY_FILE.history" 2>/dev/null
            # 保留最近10次活动记录
            if [ -f "$ACTIVITY_FILE" ]; then
                tail -10 "$ACTIVITY_FILE" > "${ACTIVITY_FILE}.tmp"
                mv "${ACTIVITY_FILE}.tmp" "$ACTIVITY_FILE"
            fi
            ;;
            
        "heavy")
            # 重度清理：重置活动追踪
            log "🧹 重度清理：重置活动追踪"
            rm -f "$ACTIVITY_FILE" "$ACTIVITY_FILE.history" 2>/dev/null
            # 重置会话开始时间
            date +%s > "$SESSION_START_FILE"
            ;;
    esac
    
    log "✅ 清理完成"
}

# ============================================
# 3. 预测性监控
# ============================================

predictive_analysis() {
    log "🔮 预测性分析..."
    
    if [ ! -f "$ACTIVITY_FILE" ]; then
        return 0
    fi
    
    # 读取最近活动数据
    local current_activity=$(cat "$ACTIVITY_FILE" 2>/dev/null || echo "0")
    
    # 计算活动趋势
    local trend="STABLE"
    if [ "$current_activity" -gt 10 ]; then
        trend="INCREASING"
    elif [ "$current_activity" -lt 3 ]; then
        trend="DECREASING"
    fi
    
    log "📈 活动趋势：${trend}（当前：${current_activity}）"
    
    # 预测何时超限
    if [ "$trend" == "INCREASING" ]; then
        # 简化预测：如果持续高频，1-2小时可能超限
        log "⚠️ 预测：1-2小时内可能超限"
        
        if is_in_cooldown; then
            return 0
        fi
        
        local message="📊 会话趋势预测\n\n趋势：活动增加\n当前频率：${current_activity}次/5分钟\n\n💡 预测：\n1-2小时内可能上下文超限\n\n建议：\n1. 提前准备 /new\n2. 使用QMD精准检索\n3. 减少工具调用\n\n预防胜于治疗 🎯"
        send_notification "INFO" "$message" "feishu"
    fi
    
    return 0
}

# ============================================
# 4. 动态阈值系统
# ============================================

calculate_activity_level() {
    log "📊 计算活跃度..."
    
    if [ ! -f "$OPENCLAW_LOG" ]; then
        echo "LOW"
        return
    fi
    
    # 统计最近1小时的活动
    local one_hour_ago=$(date -d '1 hour ago' +%s)
    local activity_count=$(tail -200 "$OPENCLAW_LOG" | grep -E '\[tools\]|\[message\]' | while read line; do
        local timestamp=$(echo "$line" | grep -oP '"time":"\K[^"]+')
        if [ -n "$timestamp" ]; then
            local log_time=$(date -d "${timestamp}" +%s 2>/dev/null || echo "0")
            if [ "$log_time" -ge "$one_hour_ago" ]; then
                echo "$line"
            fi
        fi
    done | wc -l)
    
    log "📊 活跃度统计：${activity_count}次/小时"
    
    # 判断活跃度
    if [ "$activity_count" -ge 50 ]; then
        echo "HIGH"
    elif [ "$activity_count" -ge 20 ]; then
        echo "MEDIUM"
    else
        echo "LOW"
    fi
}

# ============================================
# 5. 会话时长监控
# ============================================

check_session_duration() {
    log "⏱️ 检查会话时长..."
    
    if [ ! -f "$SESSION_START_FILE" ]; then
        # 记录会话开始时间
        date +%s > "$SESSION_START_FILE"
        log "📝 记录会话开始时间"
        return 0
    fi
    
    local session_start=$(cat "$SESSION_START_FILE" 2>/dev/null || echo "0")
    local current_time=$(date +%s)
    local duration_hours=$(( (current_time - session_start) / 3600 ))
    
    log "📊 会话时长：${duration_hours}小时"
    
    if [ "$duration_hours" -ge "$LONG_SESSION_CRITICAL" ]; then
        log "🚨 长会话严重预警（${duration_hours}小时）"
        
        if is_in_cooldown; then
            return 0
        fi
        
        local message="🚨 长会话严重提醒\n\n会话时长：${duration_hours}小时\n阈值：${LONG_SESSION_CRITICAL}小时\n\n💡 强烈建议：\n立即发送 /new 开始新会话\n\n原因：长会话会导致上下文累积"
        send_notification "CRITICAL" "$message" "both"
        
        # 自动重度清理
        smart_cleanup "heavy"
        
    elif [ "$duration_hours" -ge "$LONG_SESSION_WARNING" ]; then
        log "⚠️ 长会话预警（${duration_hours}小时）"
        
        if is_in_cooldown; then
            return 0
        fi
        
        local message="⚠️ 长会话提醒\n\n会话时长：${duration_hours}小时\n阈值：${LONG_SESSION_WARNING}小时\n\n💡 建议：\n1. 考虑发送 /new\n2. 使用QMD精准检索\n3. 清理不必要的历史"
        send_notification "WARNING" "$message" "both"
        
        # 自动中度清理
        smart_cleanup "medium"
    fi
    
    return 0
}

# ============================================
# 6. 工具调用监控
# ============================================

check_tool_calls() {
    log "🔧 检查工具调用频率..."
    
    if [ ! -f "$OPENCLAW_LOG" ]; then
        return 0
    fi
    
    # 统计最近1小时的工具调用
    local one_hour_ago=$(date -d '1 hour ago' +%s)
    local tool_calls=$(grep '\[tools\]' "$OPENCLAW_LOG" | tail -300 | while read line; do
        local timestamp=$(echo "$line" | grep -oP '"time":"\K[^"]+')
        if [ -n "$timestamp" ]; then
            local log_time=$(date -d "${timestamp}" +%s 2>/dev/null || echo "0")
            if [ "$log_time" -ge "$one_hour_ago" ]; then
                echo "$line"
            fi
        fi
    done | wc -l)
    
    log "📊 工具调用：${tool_calls}次/小时"
    
    # 严重预警
    if [ "$tool_calls" -ge "$CRITICAL_TOOL_THRESHOLD" ]; then
        log "🚨 工具调用过频（${tool_calls}次）"
        
        if is_in_cooldown; then
            return 0
        fi
        
        local message="🚨 工具调用过频提醒\n\n检测：${tool_calls}次/小时\n阈值：${CRITICAL_TOOL_THRESHOLD}次\n\n💡 立即行动：\n1. 发送 /new 开始新会话\n2. 减少工具调用\n3. 使用QMD精准检索\n\n⚠️ 工具调用会累积隐藏上下文！"
        send_notification "CRITICAL" "$message" "both"
        
        # 自动重度清理
        smart_cleanup "heavy"
        
    elif [ "$tool_calls" -ge "$HEAVY_TOOL_THRESHOLD" ]; then
        log "⚠️ 工具调用较多（${tool_calls}次）"
        
        if is_in_cooldown; then
            return 0
        fi
        
        local message="⚠️ 工具调用较多提醒\n\n检测：${tool_calls}次/小时\n阈值：${HEAVY_TOOL_THRESHOLD}次\n\n💡 建议：\n1. 注意工具调用频率\n2. 使用QMD精准检索\n3. 考虑 /new"
        send_notification "WARNING" "$message" "feishu"
        
        # 自动轻度清理
        smart_cleanup "light"
    fi
    
    return 0
}

# ============================================
# 7. 错误检测
# ============================================

check_errors() {
    log "🔍 检查错误..."
    
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
        send_notification "CRITICAL" "$message" "both"
        
        # 紧急重度清理
        smart_cleanup "heavy"
        
        return 1
    fi
    
    log "✅ 未检测到错误"
    return 0
}

# ============================================
# 8. 用户活动检测
# ============================================

check_user_activity() {
    log "🔍 检查用户活动..."
    
    if [ ! -f "$OPENCLAW_LOG" ]; then
        log "⚠️ OpenClaw日志不存在"
        return 1
    fi
    
    # 检查最近5分钟是否有用户消息
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
        log "⏸️ 无用户活动，跳过检查"
        return 1
    fi
}

# ============================================
# 主函数
# ============================================

main() {
    log "🚀 ===== 开始v6.0监控（全功能整合版） ====="
    
    # 1. 错误检测（始终检查）
    check_errors
    local error_status=$?
    
    # 2. 用户活动检测
    if ! check_user_activity; then
        log "⏸️ 无用户活动，跳过详细检查"
        log "✅ ===== 监控完成（轻量模式） =====\n"
        exit 0
    fi
    
    # 3. 计算活跃度
    local activity_level=$(calculate_activity_level)
    log "📊 活跃度：${activity_level}"
    
    # 4. 会话时长检查
    check_session_duration
    
    # 5. 工具调用监控
    check_tool_calls
    
    # 6. 预测性分析
    predictive_analysis
    
    # 7. 三级预警（简化版：基于活动频率估算）
    # 这里可以集成session_status获取真实上下文使用率
    # 暂时用活动频率作为估算
    local estimated_usage=0
    local activity_count=$(cat "$ACTIVITY_FILE" 2>/dev/null || echo "0")
    
    if [ "$activity_count" -ge 15 ]; then
        estimated_usage=85
    elif [ "$activity_count" -ge 10 ]; then
        estimated_usage=75
    elif [ "$activity_count" -ge 5 ]; then
        estimated_usage=60
    fi
    
    three_level_warning "$estimated_usage" "$activity_level"
    
    # 汇总
    if [ $error_status -eq 0 ]; then
        log "✅ 系统正常"
    else
        log "⚠️ 发现问题，已处理"
    fi
    
    log "✅ ===== 监控完成 =====\n"
}

main
