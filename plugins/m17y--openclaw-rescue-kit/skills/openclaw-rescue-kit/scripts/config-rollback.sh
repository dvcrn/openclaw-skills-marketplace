#!/bin/bash
# ~/.openclaw/scripts/config-rollback.sh
# OpenClaw 配置回滚脚本

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
LOG_DIR="$OPENCLAW_HOME/logs"
SAFE_CONFIG_DIR="$OPENCLAW_HOME/backups/safe-config"
LOG_FILE="$LOG_DIR/config-rollback.log"
CONFIG_FILE="$OPENCLAW_HOME/openclaw.json"
BACKUP_DIR="$OPENCLAW_HOME/backups"
LOCK_FILE="$LOG_DIR/rollback.lock"

mkdir -p "$LOG_DIR" "$BACKUP_DIR"

# 加载核心函数
source "$SCRIPT_DIR/core.sh"

# ==================== 锁文件机制 ====================
acquire_lock() {
    if [ -f "$LOCK_FILE" ]; then
        local lock_pid
        lock_pid=$(cat "$LOCK_FILE" 2>/dev/null)
        if [ -n "$lock_pid" ] && kill -0 "$lock_pid" 2>/dev/null; then
            log_error "另一个回滚实例正在运行 (PID: $lock_pid)，退出"
            exit 0
        else
            log_warn "发现过期锁文件，清理中..."
            rm -f "$LOCK_FILE"
        fi
    fi
    echo $$ > "$LOCK_FILE"
}

release_lock() {
    if [ -f "$LOCK_FILE" ]; then
        rm -f "$LOCK_FILE"
    fi
}

trap release_lock EXIT

# ==================== 备份文件列表 ====================
get_backup_files() {
    local backups=()
    
    # 自定义备份目录 - 优先搜索带时间戳的备份文件
    # 格式: openclaw.json.backup_YYYY-MM-DD HH:MM:SS
    if [ -d "$BACKUP_DIR" ]; then
        while IFS= read -r -d '' backup; do
            [ -n "$backup" ] && backups+=("$backup")
        done < <(find "$BACKUP_DIR" -maxdepth 1 -type f -name "openclaw.json.backup_*" -print0 2>/dev/null)
    fi
    
    # OpenClaw 自动备份
    if [ -f "$CONFIG_FILE.bak" ]; then
        backups+=("$CONFIG_FILE.bak")
    fi
    
    # 编号备份
    for i in 1 2 3 4; do
        if [ -f "$CONFIG_FILE.bak.$i" ]; then
            backups+=("$CONFIG_FILE.bak.$i")
        fi
    done
    
    # 主目录的 .bak.safe 备份
    if [ -f "$CONFIG_FILE.bak.safe" ]; then
        backups+=("$CONFIG_FILE.bak.safe")
    fi
    
    # 回滚备份目录
    if [ -d "$BACKUP_DIR" ]; then
        while IFS= read -r -d '' backup; do
            [ -n "$backup" ] && backups+=("$backup")
        done < <(find "$BACKUP_DIR" -type f \( -name "openclaw.json.rollback_*" -o -name "*openclaw*.json*" \) -print0 2>/dev/null)
    fi
    
    # 按修改时间排序（最新优先）并返回
    if [ ${#backups[@]} -gt 0 ]; then
        local sorted_backups
        sorted_backups=$(printf '%s\n' "${backups[@]}" | xargs stat -f "%m\t%N" 2>/dev/null | \
            sort -rn | cut -f2- | head -10)
        printf '%s\n' "$sorted_backups"
    fi
}

# ==================== 验证备份文件 ====================
validate_backup() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        log_error "备份文件不存在: $backup_file"
        return 1
    fi
    
    # 使用 openclaw 命令验证（临时替换配置进行验证）
    if command -v openclaw >/dev/null 2>&1; then
        local temp_backup="/tmp/openclaw_backup_restore_$$.json"
        # 备份当前配置
        cp "$CONFIG_FILE" "$temp_backup" 2>/dev/null || true
        # 临时用备份替换配置进行验证
        cp "$backup_file" "$CONFIG_FILE"
        if openclaw gateway call config.get --json >/dev/null 2>&1; then
            # 验证通过，恢复原配置
            cp "$temp_backup" "$CONFIG_FILE" 2>/dev/null || true
            rm -f "$temp_backup"
            return 0
        fi
        # 验证失败，恢复原配置
        cp "$temp_backup" "$CONFIG_FILE" 2>/dev/null || true
        rm -f "$temp_backup"
    fi
    
    # 备用: 使用 jq 验证 JSON
    if command -v jq >/dev/null 2>&1; then
        if jq empty "$backup_file" 2>/dev/null; then
            log_info "备份文件 JSON 格式有效: $backup_file"
            return 0
        fi
    fi
    
    log_error "备份文件无效: $backup_file"
    return 1
}

# ==================== 停止网关 ====================
stop_gateway() {
    log_info "停止网关..."
    
    if command -v openclaw >/dev/null 2>&1; then
        openclaw gateway stop 2>&1 | tee -a "$LOG_FILE" || true
    fi
    
    # 等待进程结束
    sleep 3
    
    # 强制结束（只杀 openclaw gateway 进程，不误杀其他进程）
    pkill -9 -f "openclaw-gateway" 2>/dev/null || true
    # 兜底：检查端口是否释放
    local port="${GATEWAY_PORT:-18789}"
    if command -v lsof >/dev/null 2>&1; then
        local remaining=$(lsof -ti:"$port" 2>/dev/null || true)
        if [ -n "$remaining" ]; then
            for pid in $remaining; do
                kill -9 "$pid" 2>/dev/null || true
            done
        fi
    fi
    
    # 等待端口释放
    sleep 2
    
    log_info "网关已停止"
}

# ==================== 启动网关 ====================
start_gateway() {
    log_info "启动网关..."
    
    # 先停止网关（增加等待时间给旧进程足够的退出时间）
    if command -v openclaw >/dev/null 2>&1; then
        openclaw gateway stop 2>&1 | tee -a "$LOG_FILE" || true
        sleep 5
    fi
    
    # 使用 LaunchAgent 启动（确保使用 gateway-start.sh 的端口清理逻辑）
    local plist=~/Library/LaunchAgents/ai.openclaw.gateway.plist
    local started=false
    if [ -f "$plist" ]; then
        launchctl bootstrap "gui/$(id -u)" "$plist" 2>&1 | tee -a "$LOG_FILE" || true
        sleep 3
        # 检查是否已启动
        local port="${GATEWAY_PORT:-18789}"
        if command -v lsof >/dev/null 2>&1 && lsof -i :"$port" -sTCP:LISTEN >/dev/null 2>&1; then
            log_info "已通过 LaunchAgent 启动网关"
            started=true
        fi
    fi
    # 只有确实没启动时才 fallback
    if [ "$started" = false ] && command -v openclaw >/dev/null 2>&1; then
        nohup openclaw gateway start > "$LOG_DIR/gateway-start.log" 2>&1 &
        log_info "网关已在后台启动（fallback），PID: $!"
    fi
    
    # 等待启动（增加到 20 秒，给网关足够的启动时间）
    log_info "等待网关启动..."
    sleep 20
    
    # 验证：检查端口是否监听（比 pgrep 更可靠）
    local port="${GATEWAY_PORT:-18789}"
    if command -v lsof >/dev/null 2>&1; then
        if lsof -i :"$port" -sTCP:LISTEN >/dev/null 2>&1; then
            log_info "网关已启动（端口 $port 监听正常）"
            return 0
        fi
    fi
    # 备用：pgrep
    if pgrep -f "openclaw.*gateway" >/dev/null 2>&1; then
        log_info "网关已启动（进程存在）"
        return 0
    fi
    
    log_error "网关启动失败"
    return 1
}

# ==================== 验证网关运行 ====================
verify_gateway() {
    log_info "验证网关..."
    
    # 等待 10 秒，给网关充分的启动时间
    sleep 10
    
    local port="${GATEWAY_PORT:-18789}"
    
    # 优先检查端口监听（最可靠的验证方式）
    if command -v lsof >/dev/null 2>&1; then
        if lsof -i :"$port" -sTCP:LISTEN >/dev/null 2>&1; then
            log_info "网关验证成功（端口 $port 监听正常）"
            return 0
        fi
    fi
    
    # 备用：检查进程 + RPC 响应
    if command -v openclaw >/dev/null 2>&1; then
        if openclaw gateway status 2>&1 | grep -q "Running\|pid\|PID"; then
            log_info "网关验证成功（RPC 响应正常）"
            return 0
        fi
    fi
    
    # 最后备用：pgrep
    if pgrep -f "openclaw.*gateway" >/dev/null 2>&1; then
        log_info "网关验证成功（进程存在）"
        return 0
    fi
    
    log_error "网关验证失败"
    return 1
}

# ==================== 执行回滚 ====================
do_rollback() {
    local backup_file="$1"
    
    log_info "========== 开始回滚 =========="
    log_info "使用备份: $backup_file"
    
    # 备份当前配置
    if [ -f "$CONFIG_FILE" ]; then
        local timestamp
        timestamp=$(date '+%Y%m%d_%H%M%S')
        cp "$CONFIG_FILE" "$BACKUP_DIR/openclaw.json.rollback_$timestamp"
        log_info "已备份当前配置到: $BACKUP_DIR/openclaw.json.rollback_$timestamp"
    fi
    
    # 停止网关
    stop_gateway
    
    # 恢复配置
    log_info "恢复配置..."
    cp "$backup_file" "$CONFIG_FILE"
    
    # 清理无效的配置键
    if command -v openclaw >/dev/null 2>&1; then
        log_info "清理无效配置键..."
        openclaw doctor --fix >/dev/null 2>&1 || true
    fi
    
    # 启动网关
    start_gateway
    
    # 验证
    if verify_gateway; then
        log_info "========== 回滚成功 =========="
        
        # 发送通知
        notify "INFO" "配置已回滚到: $(basename "$backup_file")"
        
        return 0
    else
        log_error "========== 回滚后验证失败 =========="
        return 1
    fi
}

# ==================== 主函数 ====================
main() {
    load_notify_config
    
    # 解析参数
    local use_safe=false
    local dry_run=false
    for arg in "${@:-}"; do
        case "$arg" in
            --safe|-s) use_safe=true ;;
            --dry-run|-n) dry_run=true ;;
        esac
    done
    
    if [ "$dry_run" = true ]; then
        log_info "========== [试运行] 配置回滚脚本启动 =========="
    else
        acquire_lock
        log_info "========== 配置回滚脚本启动 =========="
    fi
    
    if [ "$use_safe" = true ]; then
        log_info "模式: 回滚到安全配置"
    fi
    
    local backups=""
    
    # 如果使用安全配置，优先使用安全配置
    if [ "$use_safe" = true ]; then
        local safe_config="$SAFE_CONFIG_DIR/openclaw.json.safe"
        if [ -f "$safe_config" ]; then
            log_info "找到安全配置: $safe_config"
            backups="$safe_config"
        else
            log_error "未找到安全配置: $safe_config"
            log_error "请先运行: bash security-hardening.sh --save-safe"
            exit 1
        fi
    else
        # 获取可用备份
        backups=$(get_backup_files)
    fi
    
    if [ -z "$backups" ]; then
        log_error "未找到任何可用备份"
        
        if [ "$use_safe" = true ]; then
            notify "ERROR" "配置回滚失败: 安全配置不存在，需重新保存!"
        else
            notify "ERROR" "配置回滚失败: 未找到任何可用备份，需人工干预!"
        fi
        
        exit 1
    fi
    
    log_info "可用备份列表:"
    local backup_list=()
    while IFS= read -r backup; do
        [ -z "$backup" ] && continue
        backup_list+=("$backup")
        local size=$(du -h "$backup" 2>/dev/null | awk '{print $1}')
        local mtime=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$backup" 2>/dev/null)
        log_info "  - $(basename "$backup")  (${size:-?}, ${mtime:-?})"
    done <<< "$backups"
    
    # Dry-run 模式：只显示不执行
    if [ "$dry_run" = true ]; then
        echo ""
        log_info "========== [试运行] 回滚计划 =========="
        
        local first_valid=""
        for backup in "${backup_list[@]}"; do
            if validate_backup "$backup" 2>/dev/null; then
                first_valid="$backup"
                break
            fi
        done
        
        if [ -n "$first_valid" ]; then
            log_info "将使用的备份: $(basename "$first_valid")"
            log_info "完整路径: $first_valid"
            echo ""
            log_info "将执行的操作:"
            log_info "  1. 备份当前配置到: $BACKUP_DIR/openclaw.json.rollback_<timestamp>"
            log_info "  2. 停止网关"
            log_info "  3. 恢复配置: $(basename "$first_valid") → openclaw.json"
            log_info "  4. 清理无效配置键 (openclaw doctor --fix)"
            log_info "  5. 启动网关"
            log_info "  6. 验证网关运行"
            echo ""
            log_info "[试运行] 未执行任何修改。去掉 --dry-run 参数执行实际回滚。"
        else
            log_error "[试运行] 没有找到有效的备份文件"
        fi
        
        exit 0
    fi
    
    # 依次尝试每个备份
    local rollback_success=false
    local tried_backups=()
    
    for backup in "${backup_list[@]}"; do
        tried_backups+=("$backup")
        
        log_info "尝试备份: $backup"
        
        if validate_backup "$backup"; then
            if do_rollback "$backup"; then
                rollback_success=true
                break
            fi
        else
            log_warn "备份验证失败，跳过: $backup"
        fi
    done
    
    # 如果普通备份都失败，尝试安全配置
    if [ "$rollback_success" = false ]; then
        log_warn "========== 普通备份均失败，尝试安全配置 =========="
        
        local safe_config="$SAFE_CONFIG_DIR/openclaw.json.safe"
        if [ -f "$safe_config" ]; then
            log_info "找到安全配置: $safe_config"
            
            if validate_backup "$safe_config"; then
                if do_rollback "$safe_config"; then
                    rollback_success=true
                    log_info "安全配置回滚成功!"
                fi
            else
                log_error "安全配置验证失败"
            fi
        else
            log_error "未找到安全配置: $safe_config"
        fi
    fi
    
    if [ "$rollback_success" = false ]; then
        log_error "========== 所有备份均失败 =========="
        
        notify "ERROR" "配置回滚失败: 所有备份均损坏，需人工干预!"
        
        exit 1
    fi
    
    log_info "========== 配置回滚完成 =========="
    exit 0
}

main "$@"
