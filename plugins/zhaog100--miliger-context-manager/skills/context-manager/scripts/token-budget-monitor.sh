#!/bin/bash
# Token预算监控器（v1.1）
# 创建时间：2026-03-07 16:15
# 功能：监控工具调用Token预算，防止超限
# 参考：Moltbook - 工具调用优化策略

# Token预算配置
MAX_TOKENS_PER_HOUR=5000
WARNING_PERCENT=80

# 路径配置
LOG_FILE="$HOME/.openclaw/workspace/logs/token-budget.log"
OPENCLAW_LOG="/tmp/openclaw/openclaw-$(date +%Y-%m-%d).log"

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 统计工具调用
count_tool_calls() {
    # 统计最近1小时的工具调用
    local tool_calls=$(tail -1000 "$OPENCLAW_LOG" 2>/dev/null | \
        grep "Tool call:" | \
        wc -l || echo 0)
    
    # 确保是数字
    echo "${tool_calls:-0}"
}

# 发送告警
send_alert() {
    local title="$1"
    local message="$2"
    
    log "📨 发送告警：$title"
    
    # 发送到日志（实际可接入QQ Bot或其他通知）
    echo "$message" >> "$LOG_FILE"
}

# ============================================
# 主函数
# ============================================

main() {
    log "================================"
    log "🚀 Token预算监控启动（v1.1）"
    log "================================"
    
    # 统计工具调用
    local tool_calls=$(count_tool_calls)
    
    # 估算Token（每次调用约200 tokens）
    local estimated_tokens=$((tool_calls * 200))
    
    # 计算使用率（整数运算）
    local usage_percent=$((estimated_tokens * 100 / MAX_TOKENS_PER_HOUR))
    
    log "📊 工具调用：${tool_calls}次"
    log "📊 估算Token：${estimated_tokens}/${MAX_TOKENS_PER_HOUR} (${usage_percent}%)"
    
    # 预警检查
    if [ $estimated_tokens -ge $MAX_TOKENS_PER_HOUR ]; then
        log "🚨 Token预算超限！"
        send_alert "🚨 Token预算超限警告" "当前：${estimated_tokens} tokens\n预算：${MAX_TOKENS_PER_HOUR} tokens\n\n💡 建议：\n1. 减少工具调用\n2. 使用QMD检索\n3. 缓存结果"
    elif [ $usage_percent -ge $WARNING_PERCENT ]; then
        log "⚠️ Token预算接近上限"
        send_alert "⚠️ Token预算预警" "当前：${estimated_tokens} tokens (${usage_percent}%)\n预算：${MAX_TOKENS_PER_HOUR} tokens"
    else
        log "✅ Token预算正常"
    fi
    
    log "✅ Token预算监控完成"
    log "================================"
}

# 执行
main
