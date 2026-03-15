#!/bin/bash
# OpenClaw 日志管理脚本
# 每天凌晨执行，专门处理日志文件

set -e

# 配置
LOG_DIR="$HOME/.openclaw/maintenance/logs"
LOG_FILE="$LOG_DIR/log-management-$(date +%Y%m%d).log"
RETENTION_DAYS=7
MAX_LOG_SIZE_MB=10
COMPRESS_DAYS=14

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
log "INFO" "📁 OpenClaw 日志管理开始"

# ===================== 1. 清理旧日志 =====================
log "INFO" "🗑️  清理过期日志文件..."
log "INFO" "   删除 $RETENTION_DAYS 天前的日志"

# 清理 OpenClaw 应用日志
OPENCLAW_LOG_COUNT=$(find /tmp/openclaw -name "*.log" -mtime +$RETENTION_DAYS 2>/dev/null | wc -l)
if [ "$OPENCLAW_LOG_COUNT" -gt 0 ]; then
    log "INFO" "🔍 找到 $OPENCLAW_LOG_COUNT 个过期 OpenClaw 日志"
    find /tmp/openclaw -name "*.log" -mtime +$RETENTION_DAYS -delete 2>/dev/null
    log "INFO" "✅ 清理了 $OPENCLAW_LOG_COUNT 个 OpenClaw 日志"
fi

# 清理已压缩的日志
OPENCLAW_GZ_COUNT=$(find /tmp/openclaw -name "*.log.gz" -mtime +$RETENTION_DAYS 2>/dev/null | wc -l)
if [ "$OPENCLAW_GZ_COUNT" -gt 0 ]; then
    find /tmp/openclaw -name "*.log.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null
    log "INFO" "✅ 清理了 $OPENCLAW_GZ_COUNT 个压缩日志"
fi

# 清理维护系统日志
MAINT_LOG_COUNT=$(find "$LOG_DIR" -name "*.log" -mtime +$RETENTION_DAYS 2>/dev/null | wc -l)
if [ "$MAINT_LOG_COUNT" -gt 0 ]; then
    find "$LOG_DIR" -name "*.log" -mtime +$RETENTION_DAYS -delete 2>/dev/null
    log "INFO" "✅ 清理了 $MAINT_LOG_COUNT 个维护日志"
fi

MAINT_GZ_COUNT=$(find "$LOG_DIR" -name "*.log.gz" -mtime +$RETENTION_DAYS 2>/dev/null | wc -l)
if [ "$MAINT_GZ_COUNT" -gt 0 ]; then
    find "$LOG_DIR" -name "*.log.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null
    log "INFO" "✅ 清理了 $MAINT_GZ_COUNT 个压缩维护日志"
fi

# ===================== 2. 轮转大日志文件 =====================
log "INFO" "🔄 轮转大日志文件..."
log "INFO" "   处理超过 ${MAX_LOG_SIZE_MB}MB 的日志"

# 查找大日志文件
BIG_LOGS=$(find /tmp/openclaw -name "*.log" -size +${MAX_LOG_SIZE_MB}M 2>/dev/null || true)
BIG_LOG_COUNT=$(echo "$BIG_LOGS" | grep -c "^" || echo 0)

if [ "$BIG_LOG_COUNT" -gt 0 ]; then
    log "INFO" "🔍 找到 $BIG_LOG_COUNT 个大日志文件"
    
    echo "$BIG_LOGS" | while IFS= read -r logfile; do
        if [ -f "$logfile" ]; then
            FILE_SIZE=$(du -h "$logfile" | cut -f1)
            log "INFO" "   📄 $logfile ($FILE_SIZE)"
            
            # 压缩并截断
            TIMESTAMP=$(date +%Y%m%d-%H%M%S)
            COMPRESSED_FILE="${logfile}.${TIMESTAMP}.gz"
            
            # 压缩
            if gzip -c "$logfile" > "$COMPRESSED_FILE" 2>/dev/null; then
                # 清空原文件
                : > "$logfile"
                log "INFO" "   ✅ 已压缩并清空: $(basename "$logfile") → $(basename "$COMPRESSED_FILE")"
            else
                # 如果压缩失败，只截断
                tail -1000 "$logfile" > "${logfile}.tmp" && mv "${logfile}.tmp" "$logfile"
                log "INFO" "   ✅ 已截断: $(basename "$logfile")"
            fi
        fi
    done
else
    log "INFO" "ℹ️  没有发现大日志文件"
fi

# ===================== 3. 压缩旧日志 =====================
log "INFO" "📦 压缩旧日志文件..."
log "INFO" "   压缩 $COMPRESS_DAYS 天前的日志"

OLD_LOGS=$(find /tmp/openclaw -name "*.log" -mtime +$COMPRESS_DAYS 2>/dev/null || true)
OLD_LOG_COUNT=$(echo "$OLD_LOGS" | grep -c "^" || echo 0)

if [ "$OLD_LOG_COUNT" -gt 0 ]; then
    log "INFO" "🔍 找到 $OLD_LOG_COUNT 个可压缩的旧日志"
    
    COMPRESSED_COUNT=0
    echo "$OLD_LOGS" | while IFS= read -r logfile; do
        if [ -f "$logfile" ] && [ ! -f "${logfile}.gz" ]; then
            if gzip "$logfile" 2>/dev/null; then
                COMPRESSED_COUNT=$((COMPRESSED_COUNT + 1))
                log "INFO" "   ✅ 压缩: $(basename "$logfile")"
            fi
        fi
    done
    
    log "INFO" "✅ 共压缩了 $COMPRESSED_COUNT 个日志文件"
else
    log "INFO" "ℹ️  没有需要压缩的旧日志"
fi

# ===================== 4. 统计日志状态 =====================
log "INFO" "📊 日志统计信息..."

# OpenClaw 日志
OPENCLAW_TOTAL=$(find /tmp/openclaw -name "*.log" 2>/dev/null | wc -l)
OPENCLAW_TOTAL_SIZE=$(find /tmp/openclaw -name "*.log" -exec du -ch {} + 2>/dev/null | tail -1 | cut -f1 || echo "0")

OPENCLAW_GZ_TOTAL=$(find /tmp/openclaw -name "*.log.gz" 2>/dev/null | wc -l)
OPENCLAW_GZ_SIZE=$(find /tmp/openclaw -name "*.log.gz" -exec du -ch {} + 2>/dev/null | tail -1 | cut -f1 || echo "0")

log "INFO" "📌 OpenClaw 日志:"
log "INFO" "   普通日志: $OPENCLAW_TOTAL 个文件, $OPENCLAW_TOTAL_SIZE"
log "INFO" "   压缩日志: $OPENCLAW_GZ_TOTAL 个文件, $OPENCLAW_GZ_SIZE"

# 维护日志
MAINT_TOTAL=$(find "$LOG_DIR" -name "*.log" 2>/dev/null | wc -l)
MAINT_TOTAL_SIZE=$(find "$LOG_DIR" -name "*.log" -exec du -ch {} + 2>/dev/null | tail -1 | cut -f1 || echo "0")

MAINT_GZ_TOTAL=$(find "$LOG_DIR" -name "*.log.gz" 2>/dev/null | wc -l)
MAINT_GZ_SIZE=$(find "$LOG_DIR" -name "*.log.gz" -exec du -ch {} + 2>/dev/null | tail -1 | cut -f1 || echo "0")

log "INFO" "📌 维护系统日志:"
log "INFO" "   普通日志: $MAINT_TOTAL 个文件, $MAINT_TOTAL_SIZE"
log "INFO" "   压缩日志: $MAINT_GZ_TOTAL 个文件, $MAINT_GZ_SIZE"

# 磁盘空间
DISK_INFO=$(df -h / | tail -1)
AVAIL_SPACE=$(echo "$DISK_INFO" | awk '{print $4}')
USED_PERCENT=$(echo "$DISK_INFO" | awk '{print $5}')
log "INFO" "💾 磁盘空间: 可用 $AVAIL_SPACE, 使用率 $USED_PERCENT"

# ===================== 5. 检查日志目录权限 =====================
log "INFO" "🔐 检查日志目录权限..."

# 检查 /tmp/openclaw 权限
if [ -d "/tmp/openclaw" ]; then
    TMP_PERM=$(stat -f "%Sp" "/tmp/openclaw" 2>/dev/null || stat -c "%A" "/tmp/openclaw")
    TMP_OWNER=$(stat -f "%Su:%Sg" "/tmp/openclaw" 2>/dev/null || stat -c "%U:%G" "/tmp/openclaw")
    log "INFO" "   /tmp/openclaw: $TMP_PERM, 所有者: $TMP_OWNER"
    
    # 检查是否可写
    if [ -w "/tmp/openclaw" ]; then
        log "INFO" "   ✅ 目录可写"
    else
        log "WARN" "   ⚠️  目录不可写，可能需要修复权限"
    fi
fi

# 检查维护日志目录
MAINT_PERM=$(stat -f "%Sp" "$LOG_DIR" 2>/dev/null || stat -c "%A" "$LOG_DIR")
MAINT_OWNER=$(stat -f "%Su:%Sg" "$LOG_DIR" 2>/dev/null || stat -c "%U:%G" "$LOG_DIR")
log "INFO" "   $LOG_DIR: $MAINT_PERM, 所有者: $MAINT_OWNER"

# ===================== 6. 完成 =====================
TOTAL_CLEANED=$((OPENCLAW_LOG_COUNT + OPENCLAW_GZ_COUNT + MAINT_LOG_COUNT + MAINT_GZ_COUNT))
log "INFO" "✅ 日志管理完成"
log "INFO" "   共清理了 $TOTAL_CLEANED 个日志文件"
log "INFO" "   轮转了 $BIG_LOG_COUNT 个大日志文件"
log "INFO" "========================================"

# 压缩自己的日志
if [ -f "$LOG_FILE" ] && [ $(wc -l < "$LOG_FILE") -gt 300 ]; then
    log "INFO" "📦 压缩当前日志..."
    gzip -c "$LOG_FILE" > "${LOG_FILE}.gz" 2>/dev/null && rm "$LOG_FILE"
fi

exit 0