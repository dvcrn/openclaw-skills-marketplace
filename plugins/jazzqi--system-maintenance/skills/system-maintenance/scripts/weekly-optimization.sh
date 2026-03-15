#!/bin/bash
# OpenClaw 每周优化脚本
# 每周日执行，深度系统优化和健康分析
# 替代旧的 openclaw-weekly-optimizer.sh，功能增强

set -e

# 配置
MAINTENANCE_DIR="$HOME/.openclaw/maintenance"
CONFIG_FILE="$MAINTENANCE_DIR/config/schedule.json"
LOG_DIR="$MAINTENANCE_DIR/logs"
LOG_FILE="$LOG_DIR/weekly-optimization-$(date +%Y%m%d).log"
REPORT_DIR="$MAINTENANCE_DIR/reports"
BACKUP_DAYS=30
COMPRESS_SIZE_MB=10

# 颜色和样式（用于控制台输出）
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# 日志函数（同时输出到控制台和文件）
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local color="$NC"
    
    case "$level" in
        "SUCCESS") color="$GREEN" ;;
        "ERROR") color="$RED" ;;
        "WARN") color="$YELLOW" ;;
        "INFO") color="$BLUE" ;;
        "HEADER") color="$PURPLE" ;;
        "DETAIL") color="$CYAN" ;;
    esac
    
    # 控制台输出（带颜色）
    echo -e "${color}[$timestamp] [$level] $message${NC}"
    
    # 文件输出（不带颜色）
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# 确保目录存在
mkdir -p "$LOG_DIR"
mkdir -p "$REPORT_DIR"

# 开始
echo "========================================" >> "$LOG_FILE"
log "HEADER" "🚀 OpenClaw 每周优化开始"
log "INFO" "执行时间: $(date '+%Y-%m-%d %H:%M:%S %A')"
log "INFO" "用户: $(whoami)"
log "INFO" "主机: $(hostname)"
echo "========================================" >> "$LOG_FILE"

# ===================== 1. 系统概览 =====================
log "HEADER" "📊 1. 系统概览"

# 系统信息
log "INFO" "系统版本: $(sw_vers -productName) $(sw_vers -productVersion)"
log "INFO" "内核版本: $(uname -r)"
log "INFO" "正常运行时间: $(uptime | awk -F'up ' '{print $2}' | awk -F',' '{print $1}')"

# OpenClaw 版本
if command -v openclaw > /dev/null; then
    OPENCLAW_VERSION=$(openclaw --version 2>/dev/null || echo "未知")
    log "INFO" "OpenClaw 版本: $OPENCLAW_VERSION"
else
    log "WARN" "OpenClaw CLI 未找到"
fi

# ===================== 2. Gateway 深度检查 =====================
log "HEADER" "🔍 2. Gateway 深度检查"

# 改进的进程检测
GATEWAY_PID=$(ps aux | grep "openclaw-gateway" | grep -v grep | awk '{print $2}' | head -1)

if [ -n "$GATEWAY_PID" ]; then
    # 详细进程信息
    GATEWAY_INFO=$(ps -p "$GATEWAY_PID" -o pid,user,ppid,%cpu,%mem,rss,vsz,etime,command 2>/dev/null | tail -1)
    
    PID=$(echo "$GATEWAY_INFO" | awk '{print $1}')
    USER=$(echo "$GATEWAY_INFO" | awk '{print $2}')
    PARENT_PID=$(echo "$GATEWAY_INFO" | awk '{print $3}')
    CPU=$(echo "$GATEWAY_INFO" | awk '{print $4}')
    MEM=$(echo "$GATEWAY_INFO" | awk '{print $5}')
    RSS_MB=$(echo "$GATEWAY_INFO" | awk '{printf "%.1f", $6/1024}')
    VSZ_MB=$(echo "$GATEWAY_PID" | xargs ps -o vsz -p 2>/dev/null | tail -1 | awk '{printf "%.1f", $1/1024}')
    ELAPSED=$(echo "$GATEWAY_INFO" | awk '{print $8}')
    
    log "SUCCESS" "✅ Gateway 运行中"
    log "DETAIL" "   PID: $PID, 父进程: $PARENT_PID, 用户: $USER"
    log "DETAIL" "   运行时间: $ELAPSED"
    log "DETAIL" "   CPU: ${CPU}%, 内存: ${MEM}% (${RSS_MB}MB)"
    log "DETAIL" "   虚拟内存: ${VSZ_MB}MB"
    
    # 检查端口（macOS兼容方法）
    PORT_CHECK=$(lsof -i :18789 2>/dev/null || echo "")
    if [[ "$PORT_CHECK" == *"LISTEN"* ]]; then
        log "SUCCESS" "✅ 端口 18789 正常监听"
    else
        # 备用检查方法
        if curl -s --max-time 2 "http://localhost:18789/" > /dev/null; then
            log "SUCCESS" "✅ 端口 18789 服务可访问（lsof检测可能有权限问题）"
        else
            log "WARN" "⚠️  端口检测问题，但Gateway运行中"
        fi
    fi
    
    # 服务连接测试
    if curl -s --max-time 10 "http://localhost:18789/" > /dev/null; then
        log "SUCCESS" "✅ Gateway Web 界面可访问"
        
        # API 健康检查
        if curl -s --max-time 10 "http://localhost:18789/api/health" > /dev/null; then
            log "SUCCESS" "✅ Gateway API 健康检查通过"
        else
            log "WARN" "⚠️  Gateway API 健康检查失败"
        fi
    else
        log "ERROR" "❌ Gateway 服务不可访问"
    fi
    
    # 进程文件检查
    if [ -f "/proc/$PID/exe" ]; then
        log "DETAIL" "   进程文件: 存在"
    fi
else
    log "ERROR" "❌ Gateway 进程未运行"
    log "INFO" "   尝试启动服务..."
    
    if openclaw gateway start 2>&1 >> "$LOG_FILE"; then
        log "SUCCESS" "✅ Gateway 启动成功"
        sleep 5
        # 重新检查
        GATEWAY_PID=$(ps aux | grep "openclaw-gateway" | grep -v grep | awk '{print $2}' | head -1)
    else
        log "ERROR" "❌ Gateway 启动失败"
    fi
fi

# ===================== 3. 维护系统状态检查 =====================
log "HEADER" "🔄 3. 维护系统状态检查"

# 检查 crontab 任务
log "INFO" "检查定时任务状态..."
CRON_COUNT=$(crontab -l | grep -c "openclaw" 2>/dev/null || echo 0)
log "DETAIL" "   OpenClaw 定时任务: $CRON_COUNT 个"

if [ "$CRON_COUNT" -eq 8 ]; then
    log "SUCCESS" "✅ 定时任务配置正确 (4旧 + 4新)"
elif [ "$CRON_COUNT" -eq 4 ]; then
    log "WARN" "⚠️  只有旧系统任务，新系统未安装"
else
    log "ERROR" "❌ 定时任务数量异常: $CRON_COUNT 个"
fi

# 检查维护脚本
log "INFO" "检查维护脚本..."
SCRIPT_COUNT=0
EXECUTABLE_COUNT=0

# macOS兼容的检测方法
for script in "$MAINTENANCE_DIR/scripts"/*.sh; do
    if [ -f "$script" ]; then
        SCRIPT_COUNT=$((SCRIPT_COUNT + 1))
        if [ -x "$script" ]; then
            EXECUTABLE_COUNT=$((EXECUTABLE_COUNT + 1))
        fi
    fi
done

log "DETAIL" "   脚本总数: $SCRIPT_COUNT"
log "DETAIL" "   可执行脚本: $EXECUTABLE_COUNT"

if [ "$SCRIPT_COUNT" -eq "$EXECUTABLE_COUNT" ] && [ "$SCRIPT_COUNT" -gt 0 ]; then
    log "SUCCESS" "✅ 所有脚本可执行"
else
    log "WARN" "⚠️  脚本权限可能有问题 ($EXECUTABLE_COUNT/$SCRIPT_COUNT 可执行)"
fi

# 检查日志文件
log "INFO" "检查日志文件..."
LOG_FILE_COUNT=$(find "$LOG_DIR" -name "*.log" 2>/dev/null | wc -l)
log "DETAIL" "   维护日志文件: $LOG_FILE_COUNT 个"

# ===================== 4. 深度清理操作 =====================
log "HEADER" "🧹 4. 深度清理操作"

# 清理旧备份文件
log "INFO" "清理 $BACKUP_DAYS 天前的备份文件..."
BACKUP_CLEAN_COUNT=$(find "$HOME" -name "crontab.backup.*" -mtime +$BACKUP_DAYS 2>/dev/null | wc -l)
if [ "$BACKUP_CLEAN_COUNT" -gt 0 ]; then
    find "$HOME" -name "crontab.backup.*" -mtime +$BACKUP_DAYS -delete 2>/dev/null
    log "SUCCESS" "✅ 清理了 $BACKUP_CLEAN_COUNT 个旧备份文件"
else
    log "INFO" "ℹ️  无旧备份文件需要清理"
fi

# 清理旧日志（比日常维护更激进）
log "INFO" "深度清理 OpenClaw 日志..."
# 30天前的日志
OLD_LOG_COUNT=$(find /tmp/openclaw -name "*.log" -mtime +30 2>/dev/null | wc -l)
if [ "$OLD_LOG_COUNT" -gt 0 ]; then
    find /tmp/openclaw -name "*.log" -mtime +30 -delete 2>/dev/null
    log "SUCCESS" "✅ 清理了 $OLD_LOG_COUNT 个30天前的日志"
fi

# 60天前的压缩日志
OLD_GZ_COUNT=$(find /tmp/openclaw -name "*.log.gz" -mtime +60 2>/dev/null | wc -l)
if [ "$OLD_GZ_COUNT" -gt 0 ]; then
    find /tmp/openclaw -name "*.log.gz" -mtime +60 -delete 2>/dev/null
    log "SUCCESS" "✅ 清理了 $OLD_GZ_COUNT 个60天前的压缩日志"
fi

# 压缩大日志文件
log "INFO" "压缩大日志文件 (>${COMPRESS_SIZE_MB}MB)..."
BIG_LOGS=$(find /tmp/openclaw -name "*.log" -size +${COMPRESS_SIZE_MB}M 2>/dev/null || true)
BIG_LOG_COUNT=$(echo "$BIG_LOGS" | grep -c "^" || echo 0)

if [ "$BIG_LOG_COUNT" -gt 0 ]; then
    COMPRESSED_COUNT=0
    echo "$BIG_LOGS" | while IFS= read -r logfile; do
        if [ -f "$logfile" ] && [ ! -f "${logfile}.gz" ]; then
            if gzip "$logfile" 2>/dev/null; then
                COMPRESSED_COUNT=$((COMPRESSED_COUNT + 1))
                log "DETAIL" "   压缩: $(basename "$logfile")"
            fi
        fi
    done
    log "SUCCESS" "✅ 压缩了 $COMPRESSED_COUNT 个大日志文件"
else
    log "INFO" "ℹ️  无大日志文件需要压缩"
fi

# 清理临时文件
log "INFO" "清理临时文件..."
TEMP_PATTERNS=(
    "/tmp/*.tmp"
    "/tmp/*.bak"
    "/tmp/cron_test*.log"
    "/tmp/*news_summary*.md"
)

TEMP_CLEANED=0
for pattern in "${TEMP_PATTERNS[@]}"; do
    COUNT=$(find /tmp -name "$(basename "$pattern")" -mtime +7 2>/dev/null | wc -l)
    if [ "$COUNT" -gt 0 ]; then
        find /tmp -name "$(basename "$pattern")" -mtime +7 -delete 2>/dev/null
        TEMP_CLEANED=$((TEMP_CLEANED + COUNT))
    fi
done

if [ "$TEMP_CLEANED" -gt 0 ]; then
    log "SUCCESS" "✅ 清理了 $TEMP_CLEANED 个临时文件"
else
    log "INFO" "ℹ️  无临时文件需要清理"
fi

# ===================== 5. 磁盘和资源分析 =====================
log "HEADER" "💾 5. 磁盘和资源分析"

# 磁盘空间
log "INFO" "磁盘空间分析:"
df -h / | tail -1 | while read -r fs size used avail capacity mounted; do
    log "DETAIL" "   根目录: 可用 $avail, 使用率 $capacity"
    
    # 警告检查
    if [[ "$capacity" =~ ([0-9]+)% ]] && [ "${BASH_REMATCH[1]}" -gt 85 ]; then
        log "WARN" "⚠️  根目录磁盘使用率超过 85%: $capacity"
    fi
done

df -h "$HOME" | tail -1 | while read -r fs size used avail capacity mounted; do
    log "DETAIL" "   用户目录: 可用 $avail, 使用率 $capacity"
    
    if [[ "$capacity" =~ ([0-9]+)% ]] && [ "${BASH_REMATCH[1]}" -gt 90 ]; then
        log "WARN" "⚠️  用户目录磁盘使用率超过 90%: $capacity"
    fi
done

# 目录大小分析
log "INFO" "目录大小分析:"
if [ -d "$HOME/.openclaw" ]; then
    OPENCLAW_SIZE=$(du -sh "$HOME/.openclaw" 2>/dev/null | cut -f1)
    log "DETAIL" "   OpenClaw 目录: $OPENCLAW_SIZE"
fi

if [ -d "$HOME/.openclaw/workspace" ]; then
    WORKSPACE_SIZE=$(du -sh "$HOME/.openclaw/workspace" 2>/dev/null | cut -f1)
    log "DETAIL" "   工作区目录: $WORKSPACE_SIZE"
fi

if [ -d "/tmp/openclaw" ]; then
    TMP_OPENCLAW_SIZE=$(du -sh "/tmp/openclaw" 2>/dev/null | cut -f1)
    log "DETAIL" "   临时日志目录: $TMP_OPENCLAW_SIZE"
fi

# 内存使用
log "INFO" "内存使用分析:"
MEMORY_INFO=$(top -l 1 -s 0 | grep PhysMem)
log "DETAIL" "   $MEMORY_INFO"

# ===================== 6. 错误和性能分析 =====================
log "HEADER" "📈 6. 错误和性能分析"

# Gateway 日志分析
GATEWAY_LOG="$HOME/.openclaw/logs/gateway.log"
if [ -f "$GATEWAY_LOG" ]; then
    # 最近7天的错误统计
    ERROR_COUNT=$(tail -n 10000 "$GATEWAY_LOG" 2>/dev/null | grep -c -i "error\|fail\|timeout" || echo 0)
    WARN_COUNT=$(tail -n 10000 "$GATEWAY_LOG" 2>/dev/null | grep -c -i "warn\|warning" || echo 0)
    
    log "INFO" "Gateway 日志分析 (最近10000行):"
    log "DETAIL" "   错误数量: $ERROR_COUNT"
    log "DETAIL" "   警告数量: $WARN_COUNT"
    
    if [ "$ERROR_COUNT" -gt 10 ]; then
        log "WARN" "⚠️  错误较多，建议检查 Gateway 日志"
        log "DETAIL" "   最近错误示例:"
        tail -n 10000 "$GATEWAY_LOG" 2>/dev/null | grep -i "error" | tail -3 | while read -r line; do
            log "DETAIL" "     - ${line:0:100}..."
        done
    fi
    
    if [ "$WARN_COUNT" -gt 20 ]; then
        log "WARN" "⚠️  警告较多，建议优化配置"
    fi
else
    log "WARN" "⚠️  Gateway 日志文件不存在"
fi

# 重启统计
RESTART_COUNT=$(tail -n 5000 "$GATEWAY_LOG" 2>/dev/null | grep -c "SIGUSR1\|restart\|启动\|停止" || echo 0)
log "DETAIL" "   最近重启次数: $RESTART_COUNT"

if [ "$RESTART_COUNT" -gt 5 ]; then
    log "WARN" "⚠️  重启频繁，稳定性需关注"
fi

# ===================== 7. 定时任务分析 =====================
log "HEADER" "⏰ 7. 定时任务分析"

# 检查 OpenClaw 内部 cron 任务
if command -v openclaw > /dev/null; then
    log "INFO" "检查 OpenClaw 内部定时任务..."
    CRON_LIST=$(openclaw cron list 2>&1 || echo "无法获取")
    
    if [[ "$CRON_LIST" != "无法获取" ]] && [[ "$CRON_LIST" != *"error"* ]]; then
        CRON_TASK_COUNT=$(echo "$CRON_LIST" | grep -c "^[a-f0-9-]\{36\}" || echo 0)
        log "DETAIL" "   内部定时任务: $CRON_TASK_COUNT 个"
        
        # 检查错误状态
        ERROR_TASKS=$(echo "$CRON_LIST" | grep "error" || echo "")
        if [ -n "$ERROR_TASKS" ]; then
            ERROR_TASK_COUNT=$(echo "$ERROR_TASKS" | wc -l)
            log "WARN" "⚠️  有 $ERROR_TASK_COUNT 个任务状态为 error"
            echo "$ERROR_TASKS" | head -3 | while read -r task; do
                log "DETAIL" "     - ${task:0:80}..."
            done
        fi
    else
        log "WARN" "⚠️  无法获取 OpenClaw 内部定时任务"
    fi
fi

# ===================== 8. 健康评分和报告 =====================
log "HEADER" "🏥 8. 健康评分和报告"

# 计算健康评分 (0-100)
HEALTH_SCORE=100
REASONS=""

# 扣分规则
if [ -z "$GATEWAY_PID" ]; then
    HEALTH_SCORE=$((HEALTH_SCORE - 30))
    REASONS="$REASONS Gateway未运行;"
fi

if [ "$ERROR_COUNT" -gt 20 ]; then
    HEALTH_SCORE=$((HEALTH_SCORE - 20))
    REASONS="$REASONS 错误过多;"
elif [ "$ERROR_COUNT" -gt 10 ]; then
    HEALTH_SCORE=$((HEALTH_SCORE - 10))
    REASONS="$REASONS 错误较多;"
fi

if [ "$RESTART_COUNT" -gt 10 ]; then
    HEALTH_SCORE=$((HEALTH_SCORE - 15))
    REASONS="$REASONS 重启频繁;"
elif [ "$RESTART_COUNT" -gt 5 ]; then
    HEALTH_SCORE=$((HEALTH_SCORE - 8))
    REASONS="$REASONS 重启较多;"
fi

# 磁盘空间检查
DISK_USE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USE" -gt 90 ]; then
    HEALTH_SCORE=$((HEALTH_SCORE - 20))
    REASONS="$REASONS 磁盘空间不足;"
elif [ "$DISK_USE" -gt 80 ]; then
    HEALTH_SCORE=$((HEALTH_SCORE - 10))
    REASONS="$REASONS 磁盘空间紧张;"
fi

# 确保分数在0-100之间
if [ "$HEALTH_SCORE" -lt 0 ]; then
    HEALTH_SCORE=0
elif [ "$HEALTH_SCORE" -gt 100 ]; then
    HEALTH_SCORE=100
fi

# 输出评分
log "INFO" "系统健康评分: ${HEALTH_SCORE}/100"

if [ "$HEALTH_SCORE" -ge 90 ]; then
    log "SUCCESS" "✅ 状态: 优秀"
    EMOJI="🎉"
elif [ "$HEALTH_SCORE" -ge 70 ]; then
    log "SUCCESS" "✅ 状态: 良好"
    EMOJI="👍"
elif [ "$HEALTH_SCORE" -ge 50 ]; then
    log "WARN" "⚠️  状态: 一般"
    EMOJI="🤔"
else
    log "ERROR" "❌ 状态: 需要关注"
    EMOJI="🚨"
fi

if [ -n "$REASONS" ]; then
    log "DETAIL" "   扣分原因: $REASONS"
fi

# ===================== 9. 生成详细报告 =====================
log "HEADER" "📋 9. 生成详细报告"

REPORT_FILE="$REPORT_DIR/weekly-report-$(date +%Y%m%d).md"

cat > "$REPORT_FILE" << EOF
# OpenClaw 每周优化报告
**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')  
**执行周期**: 每周优化

## 执行摘要
- **健康评分**: ${HEALTH_SCORE}/100 ${EMOJI}
- **Gateway 状态**: $([ -n "$GATEWAY_PID" ] && echo "运行中 (PID: $GATEWAY_PID)" || echo "未运行")
- **定时任务**: $CRON_COUNT 个 (系统级)
- **清理操作**: 清理了 $((OLD_LOG_COUNT + OLD_GZ_COUNT + TEMP_CLEANED)) 个文件
- **磁盘空间**: 根目录 $(df / | tail -1 | awk '{print $5}') 已使用

## 详细内容
### 1. Gateway 状态
- 进程: $([ -n "$GATEWAY_PID" ] && echo "运行中" || echo "未运行")
- 端口: $([ -n "$PORT_INFO" ] && echo "监听正常" || echo "未监听")
- 运行时间: $([ -n "$ELAPSED" ] && echo "$ELAPSED" || echo "未知")

### 2. 维护系统
- 脚本数量: $SCRIPT_COUNT 个
- 可执行脚本: $EXECUTABLE_COUNT 个
- 维护日志: $LOG_FILE_COUNT 个文件

### 3. 清理结果
- 30天前日志: $OLD_LOG_COUNT 个
- 60天前压缩日志: $OLD_GZ_COUNT 个
- 临时文件: $TEMP_CLEANED 个
- 大日志压缩: $COMPRESSED_COUNT 个

### 4. 错误统计
- 最近错误: $ERROR_COUNT 个
- 最近警告: $WARN_COUNT 个
- 重启次数: $RESTART_COUNT 次

### 5. 资源使用
- 磁盘使用率: $(df / | tail -1 | awk '{print $5}')
- OpenClaw目录: $OPENCLAW_SIZE
- 工作区: $WORKSPACE_SIZE

### 6. 建议
$([ "$HEALTH_SCORE" -lt 70 ] && echo "1. **建议立即检查系统状态**" || echo "1. 系统状态良好，继续保持")
$([ "$ERROR_COUNT" -gt 10 ] && echo "2. **检查 Gateway 日志中的错误**" || echo "2. 错误数量在正常范围")
$([ "$RESTART_COUNT" -gt 5 ] && echo "3. **调查频繁重启的原因**" || echo "3. 重启频率正常")
$([ "$DISK_USE" -gt 80 ] && echo "4. **清理磁盘空间**" || echo "4. 磁盘空间充足")

---

*报告由 OpenClaw 统一维护系统自动生成*
EOF

log "SUCCESS" "✅ 详细报告已生成: $REPORT_FILE"
log "DETAIL" "   报告包含健康评分、状态分析和建议"

# ===================== 10. 完成和通知 =====================
log "HEADER" "🎯 10. 优化完成"

# 统计执行时间
END_TIME=$(date +%s)
START_TIME=$(date -r "$LOG_FILE" +%s 2>/dev/null || echo "$END_TIME")
DURATION=$((END_TIME - START_TIME))

log "SUCCESS" "✅ 每周优化完成"
log "INFO" "   执行时间: ${DURATION} 秒"
log "INFO" "   清理文件: $((OLD_LOG_COUNT + OLD_GZ_COUNT + TEMP_CLEANED)) 个"
log "INFO" "   健康评分: ${HEALTH_SCORE}/100 $EMOJI"

# 生成简短摘要
SUMMARY="📊 OpenClaw每周优化完成
🏥 健康评分: ${HEALTH_SCORE}/100
🔄 Gateway: $([ -n "$GATEWAY_PID" ] && echo "✅ 运行中" || echo "❌ 未运行")
🧹 清理: $((OLD_LOG_COUNT + OLD_GZ_COUNT + TEMP_CLEANED)) 个文件
📈 错误: $ERROR_COUNT 个 | 重启: $RESTART_COUNT 次
📄 报告: $REPORT_FILE
📝 日志: $LOG_FILE"

log "INFO" "优化摘要:"
echo "$SUMMARY" | while read -r line; do
    log "DETAIL" "   $line"
done

echo "========================================" >> "$LOG_FILE"
log "HEADER" "🎉 OpenClaw 每周优化脚本执行完成！"
echo "========================================" >> "$LOG_FILE"

# 退出码基于健康评分
if [ "$HEALTH_SCORE" -ge 70 ]; then
    exit 0
elif [ "$HEALTH_SCORE" -ge 50 ]; then
    exit 1  # 警告
else
    exit 2  # 错误
fi