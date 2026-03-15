#!/bin/bash
# OpenClaw 实时监控脚本
# 每5分钟执行，监控进程状态和自动恢复

set -e

# 配置
CONFIG_FILE="$HOME/.openclaw/maintenance/config/schedule.json"
LOG_DIR="$HOME/.openclaw/maintenance/logs"
LOG_FILE="$LOG_DIR/real-time-monitor-$(date +%Y%m%d).log"
MAX_RESTART_ATTEMPTS=3
GATEWAY_PORT=18789

# 日志函数
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# 确保日志目录存在
mkdir -p "$LOG_DIR"

# 开始
log "INFO" "🚀 OpenClaw 实时监控开始"

# ===================== 1. 检查 Gateway 进程 =====================
log "INFO" "🔍 检查 OpenClaw Gateway 进程..."

# 改进的进程检测方法（解决 macOS pgrep 问题）
GATEWAY_PID=$(ps aux | grep "openclaw-gateway" | grep -v grep | awk '{print $2}' | head -1)

# 备用检测：通过端口检查
if [ -z "$GATEWAY_PID" ]; then
    GATEWAY_PID=$(lsof -ti:18789 2>/dev/null | head -1)
fi

if [ -n "$GATEWAY_PID" ]; then
    # 获取进程信息
    GATEWAY_INFO=$(ps -p "$GATEWAY_PID" -o pid,user,%cpu,%mem,rss,command 2>/dev/null | tail -1)
    MEMORY_MB=$(echo "$GATEWAY_INFO" | awk '{printf "%.1f", $5/1024}')
    CPU_PERCENT=$(echo "$GATEWAY_PID" | xargs ps -o %cpu -p 2>/dev/null | tail -1 | tr -d ' ')
    
    log "INFO" "✅ Gateway 运行中 (PID: $GATEWAY_PID)"
    log "INFO" "   内存: ${MEMORY_MB}MB, CPU: ${CPU_PERCENT}%"
    
    # 检查资源使用
    if [ -n "$CPU_PERCENT" ] && [ "${CPU_PERCENT%.*}" -gt 80 ]; then
        log "WARN" "⚠️  Gateway CPU 使用过高: ${CPU_PERCENT}%"
    fi
    
    if [ -n "$MEMORY_MB" ] && [ "${MEMORY_MB%.*}" -gt 1000 ]; then
        log "WARN" "⚠️  Gateway 内存使用过高: ${MEMORY_MB}MB"
    fi
else
    log "WARN" "❌ Gateway 进程未找到，尝试重启..."
    
    # 尝试重启
    if openclaw gateway restart 2>&1 | tee -a "$LOG_FILE"; then
        log "INFO" "✅ Gateway 重启成功"
        sleep 5
        
        # 验证重启
        if curl -s --max-time 10 "http://localhost:$GATEWAY_PORT/" > /dev/null; then
            log "INFO" "✅ Gateway 服务已恢复"
        else
            log "ERROR" "❌ Gateway 重启但服务未响应"
        fi
    else
        log "ERROR" "❌ Gateway 重启失败"
    fi
fi

# ===================== 2. 检查 Gateway 服务响应 =====================
log "INFO" "🔍 检查 Gateway 服务连接..."
if curl -s --max-time 10 "http://localhost:$GATEWAY_PORT/" > /dev/null; then
    log "INFO" "✅ Gateway 服务响应正常"
else
    log "WARN" "⚠️  Gateway 服务无响应，检查进程..."
    
    # 如果进程存在但服务无响应，可能是卡死
    if [ -n "$GATEWAY_PID" ]; then
        log "WARN" "⚠️  进程存在但服务无响应，尝试重启..."
        kill "$GATEWAY_PID" 2>/dev/null && sleep 2
        openclaw gateway start 2>&1 | tee -a "$LOG_FILE"
    fi
fi

# ===================== 3. 检查关键定时任务 =====================
log "INFO" "🔍 检查关键定时任务状态..."
if command -v openclaw > /dev/null; then
    OPENCLAW_TASKS=$(openclaw cron list 2>&1 | grep -E "(财经|news)" | head -5 || true)
    if [ -n "$OPENCLAW_TASKS" ]; then
        log "INFO" "📅 定时任务状态:"
        echo "$OPENCLAW_TASKS" | while IFS= read -r line; do
            log "INFO" "   $line"
        done
    fi
else
    log "WARN" "⚠️  openclaw 命令不可用"
fi

# ===================== 4. 检查系统资源 =====================
log "INFO" "🔍 检查系统资源..."
DISK_USAGE=$(df -h / | tail -1 | awk '{print "可用: " $4 ", 使用率: " $5}')
log "INFO" "💾 磁盘: $DISK_USAGE"

MEMORY_USAGE=$(free -m 2>/dev/null | awk 'NR==2{printf "%.1f%%", $3*100/$2}' || echo "未知")
log "INFO" "🧠 内存使用: $MEMORY_USAGE"

# ===================== 5. 检查日志文件大小 =====================
log "INFO" "🔍 检查日志文件..."
LOG_FILES=$(find /tmp/openclaw -name "*.log" -size +50M 2>/dev/null | head -5 || true)
if [ -n "$LOG_FILES" ]; then
    log "WARN" "⚠️  发现大日志文件:"
    echo "$LOG_FILES" | while IFS= read -r file; do
        SIZE=$(du -h "$file" | cut -f1)
        log "WARN" "   $file ($SIZE)"
    done
fi

# 结束
log "INFO" "✅ 实时监控完成"
log "INFO" "---"

# 保持日志文件合理大小
if [ -f "$LOG_FILE" ] && [ $(wc -l < "$LOG_FILE") -gt 1000 ]; then
    tail -500 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
fi

exit 0