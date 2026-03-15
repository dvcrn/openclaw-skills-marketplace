#!/bin/bash
# 上下文监控模块
# 创建时间：2026-03-12 17:52
# 创建者：小米粒
# 功能：监控当前会话上下文使用情况，触发预警机制

# ============================================
# 上下文监控配置
# ============================================

# 预警阈值配置
WARNING_THRESHOLD_LIGHT=60   # 轻度预警：60%
WARNING_THRESHOLD_HEAVY=75   # 重量预警：75%
WARNING_THRESHOLD_CRITICAL=90 # 严重预警：90%

# 预警冷却时间（秒）
WARNING_COOLDOWN=300 # 5分钟

# 上下文监控日志
CONTEXT_MONITOR_LOG="/tmp/smart_model_context_monitor.log"

# 预警通知文件
WARNING_NOTIFY_FILE="/tmp/smart_model_context_warning.txt"

# ============================================
# 上下文监控函数
# ============================================

# 获取当前上下文使用率
# 返回：上下文使用率（百分比）
get_context_usage() {
    # 调用session_status获取上下文信息
    # 注意：这里需要实际的上下文获取方法
    # 暂时使用模拟数据，实际使用时需要替换
    
    # 方法1：从session_status获取（需要实际实现）
    # local status=$(session_status 2>&1)
    # local usage=$(echo "$status" | grep -oP 'Context: \K[0-9]+')
    
    # 方法2：从环境变量获取（临时方案）
    local usage=${CONTEXT_USAGE:-0}
    
    # 方法3：从日志文件获取
    if [ -f "$CONTEXT_MONITOR_LOG" ]; then
        local last_usage=$(tail -1 "$CONTEXT_MONITOR_LOG" | grep -oP 'usage=\K[0-9]+')
        if [ -n "$last_usage" ]; then
            usage=$last_usage
        fi
    fi
    
    echo "$usage"
}

# 检查是否需要触发预警
# 参数：$1 - 当前使用率
# 返回：预警级别（none/light/heavy/critical）
check_warning_level() {
    local usage="$1"
    
    if [ "$usage" -ge $WARNING_THRESHOLD_CRITICAL ]; then
        echo "critical"
    elif [ "$usage" -ge $WARNING_THRESHOLD_HEAVY ]; then
        echo "heavy"
    elif [ "$usage" -ge $WARNING_THRESHOLD_LIGHT ]; then
        echo "light"
    else
        echo "none"
    fi
}

# 检查预警冷却
# 参数：$1 - 预警级别
# 返回：是否可以发送预警（true/false）
check_warning_cooldown() {
    local level="$1"
    local cooldown_file="/tmp/smart_model_cooldown_${level}.txt"
    
    if [ ! -f "$cooldown_file" ]; then
        echo "true"
        return 0
    fi
    
    local last_warning=$(cat "$cooldown_file" 2>/dev/null || echo "0")
    local current_time=$(date +%s)
    local elapsed=$((current_time - last_warning))
    
    if [ "$elapsed" -ge $WARNING_COOLDOWN ]; then
        echo "true"
    else
        echo "false"
    fi
}

# 记录预警时间
# 参数：$1 - 预警级别
record_warning_time() {
    local level="$1"
    local cooldown_file="/tmp/smart_model_cooldown_${level}.txt"
    
    date +%s > "$cooldown_file"
}

# ============================================
# 预警通知函数
# ============================================

# 发送上下文预警
# 参数：$1 - 预警级别
#       $2 - 当前使用率
#       $3 - 建议操作
send_context_warning() {
    local level="$1"
    local usage="$2"
    local suggestion="$3"
    
    # 检查冷却时间
    if [ "$(check_warning_cooldown "$level")" = "false" ]; then
        echo "预警冷却中，跳过通知"
        return 0
    fi
    
    # 记录预警时间
    record_warning_time "$level"
    
    # 创建预警通知文件
    cat > "$WARNING_NOTIFY_FILE" << EOF
{
    "type": "context_warning",
    "level": "$level",
    "usage": $usage,
    "threshold": {
        "light": $WARNING_THRESHOLD_LIGHT,
        "heavy": $WARNING_THRESHOLD_HEAVY,
        "critical": $WARNING_THRESHOLD_CRITICAL
    },
    "suggestion": "$suggestion",
    "timestamp": "$(date -Iseconds)"
}
EOF
    
    # 记录日志
    echo "[$(date -Iseconds)] 预警级别：$level，使用率：$usage%，建议：$suggestion" >> "$CONTEXT_MONITOR_LOG"
    
    # 发送通知到米粒儿（如果存在通知机制）
    if [ -f "/tmp/notify_mili.txt" ]; then
        echo "CONTEXT_WARNING:$level:$usage" >> /tmp/notify_mili.txt
    fi
    
    echo "✅ 预警已发送：$level（$usage%）"
}

# ============================================
# 上下文监控主函数
# ============================================

# 执行上下文监控
# 返回：JSON格式的监控结果
monitor_context() {
    local usage=$(get_context_usage)
    local level=$(check_warning_level "$usage")
    
    # 记录监控日志
    echo "[$(date -Iseconds)] usage=$usage, level=$level" >> "$CONTEXT_MONITOR_LOG"
    
    # 触发预警
    case "$level" in
        light)
            send_context_warning "light" "$usage" "建议精简上下文或切换会话"
            ;;
        heavy)
            send_context_warning "heavy" "$usage" "建议立即清理上下文或切换到新会话"
            ;;
        critical)
            send_context_warning "critical" "$usage" "上下文即将超限，请立即处理！"
            ;;
    esac
    
    # 返回JSON格式结果
    cat << EOF
{
    "usage": $usage,
    "level": "$level",
    "threshold": {
        "light": $WARNING_THRESHOLD_LIGHT,
        "heavy": $WARNING_THRESHOLD_HEAVY,
        "critical": $WARNING_THRESHOLD_CRITICAL
    },
    "status": "$(get_monitor_status "$level")",
    "timestamp": "$(date -Iseconds)"
}
EOF
}

# 获取监控状态
# 参数：$1 - 预警级别
# 返回：状态描述
get_monitor_status() {
    local level="$1"
    
    case "$level" in
        none)
            echo "正常"
            ;;
        light)
            echo "轻度预警"
            ;;
        heavy)
            echo "重量预警"
            ;;
        critical)
            echo "严重预警"
            ;;
    esac
}

# ============================================
# 与Context Manager集成
# ============================================

# 触发Context Manager清理
# 参数：$1 - 清理级别（light/heavy/critical）
trigger_context_cleanup() {
    local level="$1"
    
    # 检查Context Manager脚本是否存在
    local context_manager_script="/root/.openclaw/workspace/skills/miliger-context-manager/scripts/context-monitor-v6.sh"
    
    if [ -f "$context_manager_script" ]; then
        echo "触发Context Manager清理（$level）..."
        
        # 设置环境变量传递清理级别
        export CLEANUP_LEVEL="$level"
        
        # 执行Context Manager脚本
        bash "$context_manager_script" >> /tmp/context_cleanup.log 2>&1
        
        echo "✅ Context Manager清理完成"
    else
        echo "⚠️  Context Manager脚本不存在：$context_manager_script"
    fi
}

# ============================================
# 上下文预测函数
# ============================================

# 预测上下文使用趋势
# 参数：$1 - 监控日志文件路径（可选）
# 返回：JSON格式的预测结果
predict_context_trend() {
    local log_file="${1:-$CONTEXT_MONITOR_LOG}"
    
    if [ ! -f "$log_file" ]; then
        echo '{"error": "log file not found"}'
        return 1
    fi
    
    # 获取最近10次监控数据
    local recent_data=$(tail -10 "$log_file" | grep -oP 'usage=\K[0-9]+')
    
    if [ -z "$recent_data" ]; then
        echo '{"error": "no data available"}'
        return 1
    fi
    
    # 计算平均增长率（简化版）
    local first_usage=$(echo "$recent_data" | head -1)
    local last_usage=$(echo "$recent_data" | tail -1)
    local growth=$((last_usage - first_usage))
    
    # 预测趋势
    local trend
    if [ "$growth" -gt 10 ]; then
        trend="increasing"
    elif [ "$growth" -lt -10 ]; then
        trend="decreasing"
    else
        trend="stable"
    fi
    
    # 预测达到临界值的时间（简化计算）
    local estimated_time="unknown"
    if [ "$trend" = "increasing" ] && [ "$growth" -gt 0 ]; then
        # 假设每分钟增长growth/10
        local remaining=$((WARNING_THRESHOLD_CRITICAL - last_usage))
        if [ "$remaining" -gt 0 ]; then
            local minutes=$((remaining * 10 / growth))
            estimated_time="${minutes}分钟"
        fi
    fi
    
    # 返回JSON格式结果
    cat << EOF
{
    "current_usage": $last_usage,
    "first_usage": $first_usage,
    "growth": $growth,
    "trend": "$trend",
    "estimated_critical_time": "$estimated_time",
    "timestamp": "$(date -Iseconds)"
}
EOF
}

# ============================================
# 工具函数
# ============================================

# 清理监控日志（保留最近100行）
cleanup_monitor_log() {
    if [ -f "$CONTEXT_MONITOR_LOG" ]; then
        tail -100 "$CONTEXT_MONITOR_LOG" > "${CONTEXT_MONITOR_LOG}.tmp"
        mv "${CONTEXT_MONITOR_LOG}.tmp" "$CONTEXT_MONITOR_LOG"
        echo "✅ 监控日志已清理"
    fi
}

# 获取监控统计信息
get_monitor_stats() {
    if [ ! -f "$CONTEXT_MONITOR_LOG" ]; then
        echo '{"error": "log file not found"}'
        return 1
    fi
    
    local total_checks=$(wc -l < "$CONTEXT_MONITOR_LOG")
    local light_warnings=$(grep -c "预警级别：light" "$CONTEXT_MONITOR_LOG" || echo "0")
    local heavy_warnings=$(grep -c "预警级别：heavy" "$CONTEXT_MONITOR_LOG" || echo "0")
    local critical_warnings=$(grep -c "预警级别：critical" "$CONTEXT_MONITOR_LOG" || echo "0")
    local avg_usage=$(awk -F'usage=' '{print $2}' "$CONTEXT_MONITOR_LOG" | awk '{sum+=$1} END {print int(sum/NR)}')
    
    cat << EOF
{
    "total_checks": $total_checks,
    "warnings": {
        "light": $light_warnings,
        "heavy": $heavy_warnings,
        "critical": $critical_warnings
    },
    "average_usage": $avg_usage,
    "timestamp": "$(date -Iseconds)"
}
EOF
}

# ============================================
# 主函数（用于测试）
# ============================================

main() {
    echo "=== 上下文监控测试 ==="
    echo ""
    
    # 测试1：模拟不同使用率的监控
    echo "测试1：模拟不同使用率的监控"
    
    for usage in 50 65 80 95; do
        export CONTEXT_USAGE=$usage
        echo "使用率：$usage%"
        monitor_context
        echo ""
    done
    
    # 测试2：检查预警冷却
    echo "测试2：检查预警冷却"
    echo "冷却状态：$(check_warning_cooldown "light")"
    echo ""
    
    # 测试3：获取监控统计
    echo "测试3：获取监控统计"
    get_monitor_stats
    echo ""
    
    # 测试4：预测趋势（需要历史数据）
    echo "测试4：预测趋势"
    predict_context_trend
    echo ""
    
    echo "=== 测试完成 ==="
}

# 如果直接运行此脚本，执行主函数
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    main "$@"
fi
