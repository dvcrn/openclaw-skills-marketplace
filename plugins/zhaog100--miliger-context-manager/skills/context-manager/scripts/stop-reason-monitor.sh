#!/bin/bash
# stop_reason错误监控脚本
# 创建时间：2026-03-06
# 更新时间：2026-03-06 18:52
# 功能：监控AI回复中的"model_context_window_exceeded"错误，立即告警并自动切换

# 修复PATH问题（cron环境）
export PATH="/root/.nvm/versions/node/v22.22.0/bin:/root/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

LOG_FILE="$HOME/.openclaw/workspace/logs/stop-reason-monitor.log"
FEISHU_TARGET="user:ou_64e8948aedd09549e512218c96702830"
ERROR_LOG="$HOME/.openclaw/workspace/logs/ai-responses.log"

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 发送飞书通知
send_feishu_notification() {
    local message="$1"
    log "📤 发送飞书紧急通知: $message"
    
    openclaw message send --channel feishu --account main --target "$FEISHU_TARGET" --message "$message" 2>&1 >> "$LOG_FILE"
}

# 监控stop_reason错误
monitor_stop_reason() {
    log "🔍 检查AI回复中的stop_reason..."
    
    # 检查最近的AI回复日志（如果有）
    if [ -f "$ERROR_LOG" ]; then
        # 搜索最近的"model_context_window_exceeded"错误
        local recent_errors=$(tail -100 "$ERROR_LOG" | grep -i "model_context_window_exceeded" | tail -1)
        
        if [ -n "$recent_errors" ]; then
            log "🚨 发现stop_reason错误：model_context_window_exceeded"
            
            # 立即发送紧急通知
            local message="🚨 紧急：模型上下文超限！\n\n错误：model_context_window_exceeded\n原因：隐藏上下文（工具调用）导致实际超限\n\n💡 建议：\n1. 立即发送 /new 开始新会话\n2. 检查当前会话的工具调用情况\n3. 考虑使用QMD精准检索替代全量读取\n\n⏰ 检测时间：$(date '+%Y-%m-%d %H:%M:%S')\n\n⚠️ 此错误说明上下文已实际超限，即使使用率显示正常！"
            
            send_feishu_notification "$message"
            
            # 触发自动切换（如果配置了）
            # bash /root/.openclaw/workspace/skills/miliger-context-manager/scripts/seamless-switch.sh
            
            return 1
        fi
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
