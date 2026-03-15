#!/bin/bash
# 上下文监控守护进程
# 创建时间：2026-03-12 18:18
# 创建者：小米粒
# 功能：实时监控上下文使用情况，自动调整模型

# ============================================
# 版权声明
# ============================================
# MIT License
# Copyright (c) 2026 米粒儿 (miliger)
# GitHub: https://github.com/zhaog100/openclaw-skills
# ClawHub: https://clawhub.com
# 
# 免费使用、修改和重新分发时需注明出处

# ============================================
# 配置
# ============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SMART_MODEL_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="/tmp/smart_model_watcher"
LOG_FILE="$LOG_DIR/context_watcher_$(date +%Y%m%d).log"
PID_FILE="$LOG_DIR/context_watcher.pid"

# 监控配置
MONITOR_INTERVAL=60  # 监控间隔（秒）
WARNING_THRESHOLD_LIGHT=60
WARNING_THRESHOLD_HEAVY=75
WARNING_THRESHOLD_CRITICAL=90

# 创建目录
mkdir -p "$LOG_DIR"

# ============================================
# 守护进程管理
# ============================================

# 启动守护进程
start_watcher() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "守护进程已在运行（PID: $pid）"
            return 1
        else
            rm -f "$PID_FILE"
        fi
    fi
    
    echo "[$(date -Iseconds)] 启动上下文监控守护进程..." >> "$LOG_FILE"
    
    # 后台运行监控循环
    (
        while true; do
            monitor_context_and_adjust
            sleep $MONITOR_INTERVAL
        done
    ) &
    
    echo $! > "$PID_FILE"
    echo "✅ 守护进程已启动（PID: $(cat $PID_FILE)）"
    echo "[$(date -Iseconds)] 守护进程已启动（PID: $(cat $PID_FILE)）" >> "$LOG_FILE"
}

# 停止守护进程
stop_watcher() {
    if [ ! -f "$PID_FILE" ]; then
        echo "守护进程未运行"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    
    if ps -p "$pid" > /dev/null 2>&1; then
        kill "$pid"
        echo "✅ 守护进程已停止（PID: $pid）"
        echo "[$(date -Iseconds)] 守护进程已停止（PID: $pid）" >> "$LOG_FILE"
    else
        echo "守护进程未运行"
    fi
    
    rm -f "$PID_FILE"
}

# 重启守护进程
restart_watcher() {
    stop_watcher
    sleep 2
    start_watcher
}

# 查看守护进程状态
status_watcher() {
    if [ ! -f "$PID_FILE" ]; then
        echo "守护进程未运行"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    
    if ps -p "$pid" > /dev/null 2>&1; then
        echo "守护进程运行中（PID: $pid）"
        
        # 显示最近日志
        if [ -f "$LOG_FILE" ]; then
            echo ""
            echo "最近5条日志："
            tail -5 "$LOG_FILE"
        fi
    else
        echo "守护进程已停止（PID文件存在但进程不存在）"
        rm -f "$PID_FILE"
    fi
}

# ============================================
# 核心监控函数
# ============================================

# 监控上下文并自动调整
monitor_context_and_adjust() {
    echo "[$(date -Iseconds)] 执行上下文监控..." >> "$LOG_FILE"
    
    # 加载Smart Model模块
    if [ -f "$SMART_MODEL_DIR/smart-model-v2.sh" ]; then
        source "$SMART_MODEL_DIR/smart-model-v2.sh"
    else
        echo "[$(date -Iseconds)] ❌ Smart Model主控制器不存在" >> "$LOG_FILE"
        return 1
    fi
    
    # 加载Model Switcher API
    if [ -f "$SMART_MODEL_DIR/integrations/model_switcher_api.sh" ]; then
        source "$SMART_MODEL_DIR/integrations/model_switcher_api.sh"
    else
        echo "[$(date -Iseconds)] ❌ Model Switcher API不存在" >> "$LOG_FILE"
        return 1
    fi
    
    # 获取所有活跃会话
    local sessions=$(find /tmp/smart_model_cache -name "current_model_*.json" 2>/dev/null | sed 's/.*current_model_\(.*\)\.json/\1/')
    
    if [ -z "$sessions" ]; then
        echo "[$(date -Iseconds)] 无活跃会话" >> "$LOG_FILE"
        return 0
    fi
    
    # 监控每个会话
    for session_id in $sessions; do
        monitor_session "$session_id"
    done
}

# 监控单个会话
# 参数：$1 - 会话ID
monitor_session() {
    local session_id="$1"
    
    # 获取上下文使用率（模拟，实际需要从OpenClaw获取）
    local context_usage=$(get_session_context_usage "$session_id")
    
    echo "[$(date -Iseconds)] 会话 $session_id 上下文使用率：$context_usage%" >> "$LOG_FILE"
    
    # 检查上下文级别
    local level=$(check_warning_level "$context_usage")
    
    # 根据级别调整模型
    case "$level" in
        critical)
            handle_critical_context "$session_id" "$context_usage"
            ;;
        heavy)
            handle_heavy_context "$session_id" "$context_usage"
            ;;
        light)
            handle_light_context "$session_id" "$context_usage"
            ;;
        none)
            # 上下文正常，无需调整
            ;;
    esac
}

# 处理严重上下文
# 参数：$1 - 会话ID
#       $2 - 上下文使用率
handle_critical_context() {
    local session_id="$1"
    local context_usage="$2"
    
    echo "[$(date -Iseconds)] ⚠️  会话 $session_id 上下文严重（$context_usage%），切换到flash模型" >> "$LOG_FILE"
    
    # 切换到flash模型
    local result=$(set_model "flash" "$session_id")
    
    # 记录切换历史
    record_switch_history "$session_id" "auto" "context_critical" "$context_usage" "flash"
    
    # 触发通知（可选）
    if [ -f "/tmp/notify_mili.txt" ]; then
        echo "CONTEXT_CRITICAL:$session_id:$context_usage" >> /tmp/notify_mili.txt
    fi
}

# 处理较重上下文
# 参数：$1 - 会话ID
#       $2 - 上下文使用率
handle_heavy_context() {
    local session_id="$1"
    local context_usage="$2"
    
    echo "[$(date -Iseconds)] ⚠️  会话 $session_id 上下文较重（$context_usage%），建议切换到flash模型" >> "$LOG_FILE"
    
    # 可以选择自动切换或仅提供建议
    # 这里选择自动切换
    local result=$(set_model "flash" "$session_id")
    
    # 记录切换历史
    record_switch_history "$session_id" "auto" "context_heavy" "$context_usage" "flash"
}

# 处理轻度上下文
# 参数：$1 - 会话ID
#       $2 - 上下文使用率
handle_light_context() {
    local session_id="$1"
    local context_usage="$2"
    
    echo "[$(date -Iseconds)] 会话 $session_id 上下文轻度预警（$context_usage%）" >> "$LOG_FILE"
    
    # 轻度预警不自动切换，仅记录
    record_switch_history "$session_id" "warning" "context_light" "$context_usage" "none"
}

# ============================================
# 辅助函数
# ============================================

# 获取会话上下文使用率（模拟函数）
# 实际使用时需要从OpenClaw获取真实数据
get_session_context_usage() {
    local session_id="$1"
    
    # 方法1：从session_status获取（需要实际实现）
    # local status=$(session_status 2>&1)
    # local usage=$(echo "$status" | grep -oP 'Context: \K[0-9]+')
    
    # 方法2：从环境变量获取（临时方案）
    # local usage=${CONTEXT_USAGE:-0}
    
    # 方法3：从日志文件获取（临时方案）
    local usage_file="/tmp/context_usage_${session_id}.txt"
    if [ -f "$usage_file" ]; then
        cat "$usage_file"
    else
        echo "0"
    fi
}

# 记录切换历史
# 参数：$1 - 会话ID
#       $2 - 切换类型（auto/manual）
#       $3 - 切换原因
#       $4 - 上下文使用率
#       $5 - 目标模型
record_switch_history() {
    local session_id="$1"
    local switch_type="$2"
    local reason="$3"
    local context_usage="$4"
    local target_model="$5"
    
    local history_file="/tmp/smart_model_watcher/switch_history.log"
    
    echo "$(date -Iseconds)|$session_id|$switch_type|$reason|$context_usage|$target_model" >> "$history_file"
}

# 获取监控统计
get_watcher_stats() {
    local history_file="/tmp/smart_model_watcher/switch_history.log"
    
    if [ ! -f "$history_file" ]; then
        echo '{"error": "no history data"}'
        return 1
    fi
    
    local total_switches=$(wc -l < "$history_file")
    local auto_switches=$(grep "|auto|" "$history_file" | wc -l)
    local critical_switches=$(grep "context_critical" "$history_file" | wc -l)
    local heavy_switches=$(grep "context_heavy" "$history_file" | wc -l)
    
    cat << EOF
{
    "total_switches": $total_switches,
    "auto_switches": $auto_switches,
    "critical_switches": $critical_switches,
    "heavy_switches": $heavy_switches,
    "monitor_interval": $MONITOR_INTERVAL,
    "timestamp": "$(date -Iseconds)"
}
EOF
}

# ============================================
# 主入口
# ============================================

case "${1:-}" in
    --start)
        start_watcher
        ;;
    --stop)
        stop_watcher
        ;;
    --restart)
        restart_watcher
        ;;
    --status)
        status_watcher
        ;;
    --stats)
        get_watcher_stats
        ;;
    --monitor)
        monitor_context_and_adjust
        ;;
    --test)
        echo "=== 上下文监控守护进程测试 ==="
        echo ""
        
        echo "测试1：单次监控"
        monitor_context_and_adjust
        echo ""
        
        echo "测试2：查看统计"
        get_watcher_stats
        echo ""
        
        echo "测试3：启动守护进程"
        start_watcher
        sleep 3
        echo ""
        
        echo "测试4：查看状态"
        status_watcher
        echo ""
        
        echo "测试5：停止守护进程"
        stop_watcher
        echo ""
        
        echo "=== 测试完成 ==="
        ;;
    *)
        echo "用法："
        echo "  $0 --start      - 启动守护进程"
        echo "  $0 --stop       - 停止守护进程"
        echo "  $0 --restart    - 重启守护进程"
        echo "  $0 --status     - 查看状态"
        echo "  $0 --stats      - 查看统计"
        echo "  $0 --monitor    - 执行单次监控"
        echo "  $0 --test       - 运行测试"
        ;;
esac
