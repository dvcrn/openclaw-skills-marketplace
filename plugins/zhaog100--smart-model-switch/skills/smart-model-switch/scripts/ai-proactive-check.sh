#!/bin/bash

# AI主动检测脚本
# 功能：在每次回复前检查上下文使用率，主动触发切换或提醒

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$SKILL_DIR/config/model-rules.json"
STATE_FILE="$SKILL_DIR/data/context-state.json"
LOG_FILE="$HOME/.openclaw/logs/ai-proactive-check.log"

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 获取当前上下文使用率
get_context_usage() {
    # 支持测试模式：环境变量 TEST_CONTEXT_USAGE
    if [ -n "$TEST_CONTEXT_USAGE" ]; then
        echo "$TEST_CONTEXT_USAGE"
        return
    fi

    local script_dir="$(dirname "$0")"
    local usage=$("$script_dir/get-context-usage.sh" 2>/dev/null)

    if [ -z "$usage" ] || ! [[ "$usage" =~ ^[0-9]+$ ]]; then
        usage=0
    fi

    echo "$usage"
}

# 检查冷却期
is_in_cooldown() {
    local cooldown_until=$(jq -r '.cooldown_until // empty' "$STATE_FILE" 2>/dev/null)
    if [ -z "$cooldown_until" ] || [ "$cooldown_until" = "null" ]; then
        return 1
    fi
    
    local now=$(date +%s)
    local cooldown_ts=$(date -d "$cooldown_until" +%s 2>/dev/null || echo 0)
    
    if [ $now -lt $cooldown_ts ]; then
        return 0
    else
        # 清除过期的冷却期
        local temp_file=$(mktemp)
        jq '.cooldown_until = null' "$STATE_FILE" > "$temp_file" 2>/dev/null
        mv "$temp_file" "$STATE_FILE" 2>/dev/null
        return 1
    fi
}

# 检查是否应该提醒
should_notify() {
    local last_notify=$(jq -r '.last_notify // empty' "$STATE_FILE" 2>/dev/null)
    if [ -z "$last_notify" ] || [ "$last_notify" = "null" ]; then
        return 0
    fi
    
    local now=$(date +%s)
    local notify_ts=$(date -d "$last_notify" +%s 2>/dev/null || echo 0)
    local notify_interval=300  # 5分钟内不重复提醒
    
    if [ $((now - notify_ts)) -gt $notify_interval ]; then
        return 0
    else
        return 1
    fi
}

# 更新通知时间
update_notify_time() {
    local temp_file=$(mktemp)
    jq --arg now "$(date -Iseconds)" '(.last_notify = $now)' "$STATE_FILE" > "$temp_file" 2>/dev/null
    mv "$temp_file" "$STATE_FILE" 2>/dev/null
}

# 主动检测主逻辑
main() {
    log "开始AI主动检测"
    
    # 初始化状态文件（如果不存在）
    if [ ! -f "$STATE_FILE" ]; then
        cat > "$STATE_FILE" << EOF
{
  "consecutive_hits": 0,
  "last_check": null,
  "current_model": "zai/glm-5",
  "last_switch": null,
  "cooldown_until": null,
  "last_notify": null
}
EOF
    fi
    
    # 检查冷却期
    if is_in_cooldown; then
        log "在冷却期内，跳过检测"
        echo "⏸️  冷却期中，跳过检测"
        exit 0
    fi
    
    # 获取上下文使用率
    local usage=$(get_context_usage)
    log "当前上下文使用率：${usage}%"
    
    # 读取阈值
    local threshold=$(jq -r '.context_switch_strategy.rules[0].threshold // 85' "$CONFIG_FILE" 2>/dev/null)
    local consecutive_hits_required=$(jq -r '.context_switch_strategy.rules[0].consecutive_hits // 2' "$CONFIG_FILE" 2>/dev/null)
    
    # 读取当前状态
    local current_hits=$(jq -r '.consecutive_hits // 0' "$STATE_FILE" 2>/dev/null)
    
    # 判断是否超过阈值
    if [ "$usage" -ge "$threshold" ]; then
        current_hits=$((current_hits + 1))
        log "超过阈值（$usage% >= $threshold%），连续命中次数：$current_hits"
        
        # 更新状态
        local temp_file=$(mktemp)
        jq --arg hits "$current_hits" \
           --arg now "$(date -Iseconds)" \
           '(.consecutive_hits = ($hits | tonumber)) |
            (.last_check = $now)' "$STATE_FILE" > "$temp_file" 2>/dev/null
        mv "$temp_file" "$STATE_FILE"
        
        # 判断是否达到连续次数
        if [ "$current_hits" -ge "$consecutive_hits_required" ]; then
            log "达到连续${consecutive_hits_required}次阈值，触发AI主动切换"
            
            # 输出提醒信息
            if should_notify; then
                echo ""
                echo "⚠️  【AI主动提醒】"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                echo "检测到上下文使用率已达 ${usage}%（阈值${threshold}%）"
                echo "已连续${current_hits}次超过阈值"
                echo ""
                echo "建议操作："
                echo "1. 使用 /new 创建新会话（推荐）"
                echo "2. 切换到长上下文模型：/model bailian/kimi-k2.5"
                echo "3. 清理部分对话历史"
                echo ""
                echo "💡 Context Manager 可自动处理：https://clawhub.com/skill/miliger-context-manager"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                echo ""
                
                update_notify_time
                log "已发送AI主动提醒"
            else
                log "5分钟内已提醒过，跳过"
            fi
            
            # 自动切换模型（如果配置了自动切换）
            local auto_switch=$(jq -r '.context_switch_strategy.auto_switch // false' "$CONFIG_FILE" 2>/dev/null)
            if [ "$auto_switch" = "true" ]; then
                local target_model=$(jq -r '.context_switch_strategy.rules[0].target_model // "bailian/kimi-k2.5"' "$CONFIG_FILE" 2>/dev/null)
                "$SCRIPT_DIR/switch-model.sh" "$target_model" >> "$LOG_FILE" 2>&1
                log "已自动切换到模型：$target_model"
                echo "✅ 已自动切换到长上下文模型：$target_model"
            fi
        else
            log "未达到连续${consecutive_hits_required}次，继续监控（当前：$current_hits）"
        fi
    else
        # 重置计数器
        if [ "$current_hits" -gt 0 ]; then
            log "未超过阈值，重置计数器"
            local temp_file=$(mktemp)
            jq --arg now "$(date -Iseconds)" \
               '(.consecutive_hits = 0) |
                (.last_check = $now)' "$STATE_FILE" > "$temp_file" 2>/dev/null
            mv "$temp_file" "$STATE_FILE"
        fi
    fi
    
    log "AI主动检测完成"
}

# 执行主函数
main
