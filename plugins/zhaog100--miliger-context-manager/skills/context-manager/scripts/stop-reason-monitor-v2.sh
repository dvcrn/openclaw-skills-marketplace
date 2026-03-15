#!/bin/bash
# stop_reason错误监控脚本 v2.0
# 创建时间：2026-03-06
# 更新时间：2026-03-06 21:15
# 功能：从OpenClaw日志中监控"model_context_window_exceeded"错误，立即告警

# 修复PATH问题（cron环境）
export PATH="/root/.nvm/versions/node/v22.22.0/bin:/root/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

LOG_FILE="$HOME/.openclaw/workspace/logs/stop-reason-monitor.log"
FEISHU_TARGET="user:ou_64e8948aedd09549e512218c96702830"
# 检查最近3天的日志（跨天错误检测）
OPENCLAW_LOGS=()
for i in 0 1 2; do
    log_date=$(date -d "$i days ago" +%Y-%m-%d 2>/dev/null || date -v-${i}d +%Y-%m-%d 2>/dev/null || date +%Y-%m-%d)
    OPENCLAW_LOGS+=("/tmp/openclaw/openclaw-${log_date}.log")
done
COOLDOWN_FILE="/tmp/openclaw/stop-reason-cooldown"
COOLDOWN_SECONDS=3600

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 检查冷却期
check_cooldown() {
    if [ -f "$COOLDOWN_FILE" ]; then
        local last_alert=$(cat "$COOLDOWN_FILE")
        local now=$(date +%s)
        local elapsed=$((now - last_alert))
        
        if [ $elapsed -lt $COOLDOWN_SECONDS ]; then
            log "⏸️ 冷却期中（剩余$((COOLDOWN_SECONDS - elapsed))秒）"
            return 1
        fi
    fi
    return 0
}

# 设置冷却期
set_cooldown() {
    date +%s > "$COOLDOWN_FILE"
}

# 发送飞书通知
send_feishu_notification() {
    local message="$1"
    log "📤 发送飞书紧急通知: $message"
    
    openclaw message send --channel feishu --account main --target "$FEISHU_TARGET" --message "$message" 2>&1 >> "$LOG_FILE"
}

# 发送QQ通知（给官家）
send_qq_notification() {
    local message="$1"
    log "📤 发送QQ通知: $message"
    
    openclaw message send --channel qqbot --target "qqbot:c2c:1478D4753463307D2E176B905A8B7F5E" --message "$message" 2>&1 >> "$LOG_FILE"
}

# 监控stop_reason错误
monitor_stop_reason() {
    log "🔍 检查OpenClaw日志中的stop_reason错误..."
    
    # 检查最近3天的日志（跨天错误检测）
    local recent_errors=""
    for log_file in "${OPENCLAW_LOGS[@]}"; do
        if [ -f "$log_file" ]; then
            log "📄 检查日志：$log_file"
            recent_errors=$(tail -1000 "$log_file" | grep -i "model_context_window_exceeded" | tail -1)
            if [ -n "$recent_errors" ]; then
                break
            fi
        else
            log "⚠️ 日志文件不存在：$log_file"
        fi
    done
    
    if [ -n "$recent_errors" ]; then
        log "🚨 发现stop_reason错误：model_context_window_exceeded"
        
        # 检查冷却期
        if ! check_cooldown; then
            log "⏸️ 冷却期中，跳过通知"
            return 0
        fi
        
        # 提取错误时间戳
        local error_time=$(echo "$recent_errors" | grep -oP '"time":"\K[^"]+' | head -1)
        if [ -z "$error_time" ]; then
            error_time=$(date '+%Y-%m-%d %H:%M:%S')
        fi
        
        # 立即发送紧急通知（飞书）
        local message="🚨 紧急：模型上下文超限！\n\n错误：model_context_window_exceeded\n时间：$error_time\n\n💡 建议：\n1. 立即发送 /new 开始新会话\n2. 检查工具调用频率\n3. 使用QMD精准检索替代全量读取\n\n⚠️ 此错误说明上下文已实际超限，即使使用率显示正常！"
        
        send_feishu_notification "$message"
        
        # 同时发送QQ通知（给官家）
        local qq_message="官家，我检测到上下文超限了！\n\n请发送 /new 开始新会话\n\n这是系统自动检测，不是你的问题 🌾"
        send_qq_notification "$qq_message"
        
        # 设置冷却期
        set_cooldown
        
        return 1
    fi
    
    log "✅ 未发现stop_reason错误"
    return 0
}

# 主函数
main() {
    log "🔍 ===== 开始stop_reason监控检查 ====="
    monitor_stop_reason
    local status=$?
    log "✅ ===== 检查完成 =====\n"
    exit $status
}

main
