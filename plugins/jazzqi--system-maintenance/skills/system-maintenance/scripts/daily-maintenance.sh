#!/bin/bash
# OpenClaw 日常维护脚本
# 每天凌晨执行，综合清理和健康检查

set -e

# 配置
CONFIG_FILE="$HOME/.openclaw/maintenance/config/schedule.json"
LOG_DIR="$HOME/.openclaw/maintenance/logs"
LOG_FILE="$LOG_DIR/daily-maintenance-$(date +%Y%m%d).log"
RETENTION_DAYS=3

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
log "INFO" "🚀 OpenClaw 日常维护开始"

# ===================== 1. 日志清理 =====================
log "INFO" "🧹 清理旧日志文件..."
log "INFO" "   清理 $RETENTION_DAYS 天前的日志"

# 清理 /tmp/openclaw 日志
TMP_LOG_COUNT=$(find /tmp/openclaw -name "*.log" -mtime +$RETENTION_DAYS 2>/dev/null | wc -l)
if [ "$TMP_LOG_COUNT" -gt 0 ]; then
    find /tmp/openclaw -name "*.log" -mtime +$RETENTION_DAYS -delete 2>/dev/null
    log "INFO" "✅ 清理了 $TMP_LOG_COUNT 个旧日志文件"
else
    log "INFO" "ℹ️  没有需要清理的旧日志"
fi

# 清理自己的维护日志 (保留7天)
MAINT_LOG_COUNT=$(find "$LOG_DIR" -name "*.log" -mtime +7 2>/dev/null | wc -l)
if [ "$MAINT_LOG_COUNT" -gt 0 ]; then
    find "$LOG_DIR" -name "*.log" -mtime +7 -delete 2>/dev/null
    log "INFO" "✅ 清理了 $MAINT_LOG_COUNT 个旧维护日志"
fi

# ===================== 2. 临时文件清理 =====================
log "INFO" "🗑️  清理临时文件..."

# 清理各种临时文件
TEMP_PATTERNS=(
    "/tmp/cron_test*.log"
    "/tmp/*news_summary*.md"
    "/tmp/instant_news_summary.md"
    "/tmp/finance_news_now.md"
    "/tmp/*.tmp"
    "/tmp/*.bak"
)

for pattern in "${TEMP_PATTERNS[@]}"; do
    TEMP_COUNT=$(find /tmp -name "$(basename "$pattern")" -mtime +1 2>/dev/null | wc -l)
    if [ "$TEMP_COUNT" -gt 0 ]; then
        find /tmp -name "$(basename "$pattern")" -mtime +1 -delete 2>/dev/null
        log "INFO" "✅ 清理了 $TEMP_COUNT 个 $(basename "$pattern") 文件"
    fi
done

# ===================== 3. Gateway 深度检查 =====================
log "INFO" "🔍 Gateway 深度健康检查..."

GATEWAY_PID=$(ps aux | grep "openclaw-gateway" | grep -v grep | awk '{print $2}' | head -1)
if [ -n "$GATEWAY_PID" ]; then
    # 获取详细进程信息
    GATEWAY_STATS=$(ps -p "$GATEWAY_PID" -o pid,user,%cpu,%mem,rss,vsz,etime,command 2>/dev/null | tail -1)
    if [ -n "$GATEWAY_STATS" ]; then
        PID=$(echo "$GATEWAY_STATS" | awk '{print $1}')
        USER=$(echo "$GATEWAY_STATS" | awk '{print $2}')
        CPU=$(echo "$GATEWAY_STATS" | awk '{print $3}')
        MEM=$(echo "$GATEWAY_STATS" | awk '{print $4}')
        RSS_MB=$(echo "$GATEWAY_STATS" | awk '{printf "%.1f", $5/1024}')
        VSZ_MB=$(echo "$GATEWAY_STATS" | awk '{printf "%.1f", $6/1024}')
        ELAPSED=$(echo "$GATEWAY_STATS" | awk '{print $7}')
        
        log "INFO" "✅ Gateway 健康状态:"
        log "INFO" "   PID: $PID, 用户: $USER, 运行时间: $ELAPSED"
        log "INFO" "   CPU: ${CPU}%, 内存: ${MEM}% (${RSS_MB}MB)"
        log "INFO" "   虚拟内存: ${VSZ_MB}MB"
    fi
    
    # 检查端口监听
    PORT_LISTEN=$(lsof -i :18789 2>/dev/null | grep LISTEN || true)
    if [ -n "$PORT_LISTEN" ]; then
        log "INFO" "✅ 端口 18789 正常监听"
    else
        log "WARN" "⚠️  端口 18789 未监听但进程存在"
    fi
else
    log "ERROR" "❌ Gateway 进程未运行"
    log "INFO" "   尝试启动..."
    if openclaw gateway start 2>&1 | tee -a "$LOG_FILE"; then
        log "INFO" "✅ Gateway 启动成功"
    else
        log "ERROR" "❌ Gateway 启动失败"
    fi
fi

# ===================== 4. 服务连接测试 =====================
log "INFO" "🔌 测试 Gateway 服务连接..."
if curl -s --max-time 15 "http://localhost:18789/" > /dev/null; then
    log "INFO" "✅ Gateway Web 界面可访问"
    
    # 测试 API 端点
    if curl -s --max-time 10 "http://localhost:18789/api/health" > /dev/null; then
        log "INFO" "✅ Gateway API 健康检查通过"
    fi
else
    log "ERROR" "❌ Gateway 服务不可访问"
fi

# ===================== 5. 磁盘空间检查 =====================
log "INFO" "💾 检查磁盘空间..."

# 根目录
ROOT_DISK=$(df -h / | tail -1)
ROOT_AVAIL=$(echo "$ROOT_DISK" | awk '{print $4}')
ROOT_USE=$(echo "$ROOT_DISK" | awk '{print $5}')
log "INFO" "📌 根目录: 可用 $ROOT_AVAIL, 使用率 $ROOT_USE"

# 用户目录
HOME_DISK=$(df -h "$HOME" | tail -1)
HOME_AVAIL=$(echo "$HOME_DISK" | awk '{print $4}')
HOME_USE=$(echo "$HOME_DISK" | awk '{print $5}')
log "INFO" "📌 用户目录: 可用 $HOME_AVAIL, 使用率 $HOME_USE"

# 工作区大小
if [ -d "$HOME/.openclaw/workspace" ]; then
    WORKSPACE_SIZE=$(du -sh "$HOME/.openclaw/workspace" 2>/dev/null | cut -f1)
    log "INFO" "📁 工作区大小: $WORKSPACE_SIZE"
fi

# 警告检查
if [[ "$ROOT_USE" =~ ([0-9]+)% ]] && [ "${BASH_REMATCH[1]}" -gt 85 ]; then
    log "WARN" "⚠️  根目录磁盘使用率超过 85%: $ROOT_USE"
fi

if [[ "$HOME_USE" =~ ([0-9]+)% ]] && [ "${BASH_REMATCH[1]}" -gt 90 ]; then
    log "WARN" "⚠️  用户目录磁盘使用率超过 90%: $HOME_USE"
fi

# ===================== 6. 更新学习记录 =====================
log "INFO" "📚 更新学习记录系统..."

LEARNINGS_DIR="$HOME/.openclaw/workspace/.learnings"
if [ -d "$LEARNINGS_DIR" ]; then
    if [ -f "$LEARNINGS_DIR/LEARNINGS.md" ]; then
        echo "" >> "$LEARNINGS_DIR/LEARNINGS.md"
        echo "## [MAINT-$(date +%Y%m%d)] 日常维护执行" >> "$LEARNINGS_DIR/LEARNINGS.md"
        echo "**时间**: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LEARNINGS_DIR/LEARNINGS.md"
        echo "**状态**: 正常完成" >> "$LEARNINGS_DIR/LEARNINGS.md"
        echo "**清理日志**: $TMP_LOG_COUNT 个文件" >> "$LEARNINGS_DIR/LEARNINGS.md"
        echo "**Gateway 状态**: $([ -n "$GATEWAY_PID" ] && echo "运行中" || echo "未运行")" >> "$LEARNINGS_DIR/LEARNINGS.md"
        echo "---" >> "$LEARNINGS_DIR/LEARNINGS.md"
        log "INFO" "✅ 学习记录已更新"
    else
        log "INFO" "ℹ️  学习记录文件不存在"
    fi
else
    log "INFO" "ℹ️  学习记录目录不存在"
fi

# ===================== 7. 维护完成 =====================
log "INFO" "✅ 日常维护完成"
log "INFO" "========================================"

# 压缩大日志文件
if [ -f "$LOG_FILE" ] && [ $(wc -l < "$LOG_FILE") -gt 500 ]; then
    log "INFO" "📦 压缩维护日志..."
    gzip -c "$LOG_FILE" > "${LOG_FILE}.gz" 2>/dev/null && rm "$LOG_FILE"
    log "INFO" "✅ 日志已压缩: ${LOG_FILE}.gz"
fi

exit 0