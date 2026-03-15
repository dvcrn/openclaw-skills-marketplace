#!/bin/bash
# task-monitor.sh - 任务监控脚本
# 自动检测任务状态、超时处理、通知

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REGISTRY="$SCRIPT_DIR/task-registry.sh"
AUTO_MERGE="$SCRIPT_DIR/auto-merge.sh"
NOTIFY="$SCRIPT_DIR/notify.sh"

REGISTRY_FILE="/tmp/codex-tasks/active-tasks.json"
LOG_FILE="/tmp/codex-tasks/monitor.log"

# 配置
TASK_TIMEOUT="${TASK_TIMEOUT:-3600}"  # 默认超时 1 小时
CHECK_INTERVAL="${CHECK_INTERVAL:-60}"  # 默认检查间隔 60 秒

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

print_msg() { echo -e "${1}${2}${NC}"; }

# 获取任务产出信息
get_task_outputs() {
    local task_id="$1"
    local task_dir="/tmp/codex-results/tasks/$task_id"
    
    if [[ ! -d "$task_dir" ]]; then
        echo ""
        return
    fi
    
    local outputs=""
    
    # 1. 检查输出日志
    if [[ -f "$task_dir/output.log" ]]; then
        # 提取文件创建信息
        local created_files
        created_files=$(grep -E "创建|mkdir|touch|new file|written to|created" "$task_dir/output.log" 2>/dev/null | head -10 || echo "")
        
        if [[ -n "$created_files" ]]; then
            outputs+="📁 创建的文件:\n"
            outputs+="$created_files\n"
        fi
    fi
    
    # 2. 检查 prompt 文件
    if [[ -f "$task_dir/prompt.txt" ]]; then
        outputs+="📝 任务描述: $(head -1 "$task_dir/prompt.txt" | cut -c1-80)\n"
    fi
    
    # 3. 检查 git 变化
    if [[ -d "$HOME/projects" ]]; then
        local recent_changes
        recent_changes=$(cd "$HOME/projects" && git status --short 2>/dev/null | head -10 || echo "")
        if [[ -n "$recent_changes" ]]; then
            outputs+="🔄 Git 变化:\n$recent_changes\n"
        fi
    fi
    
    echo -e "$outputs"
}

# 检查任务状态
check_tasks() {
    log "开始检查任务状态..."
    
    # 检查注册表是否存在
    if [[ ! -f "$REGISTRY_FILE" ]]; then
        log "注册表不存在，跳过"
        return
    fi
    
    local now
    now=$(date +%s)
    
    # 获取所有运行中的任务
    local running_tasks
    running_tasks=$(jq -r '.tasks[] | select(.status == "running") | .id' "$REGISTRY_FILE" 2>/dev/null || echo "")
    
    if [[ -z "$running_tasks" ]]; then
        log "无运行中的任务"
        return
    fi
    
    while IFS= read -r task_id; do
        [[ -z "$task_id" ]] && continue
        
        check_single_task "$task_id" "$now"
        
    done <<< "$running_tasks"
    
    # 检查完成待合并的任务
    check_completed_tasks
    
    log "检查完成"
}

# 检查单个任务
check_single_task() {
    local task_id="$1"
    local now="$2"
    
    local task_info started_at tmux_session
    task_info=$(jq -c ".tasks[] | select(.id == \"$task_id\")" "$REGISTRY_FILE")
    
    if [[ -z "$task_info" || "$task_info" == "null" ]]; then
        return
    fi
    
    started_at=$(echo "$task_info" | jq -r '.started_at')
    tmux_session=$(echo "$task_info" | jq -r '.tmux_session')
    
    # 计算运行时长
    local elapsed=$((now - started_at))
    local elapsed_min=$((elapsed / 60))
    
    # 1. 检查超时
    if [[ $elapsed -gt $TASK_TIMEOUT ]]; then
        log "⚠️ 任务 $task_id 超时 (${elapsed_min}分钟)，标记为失败"
        
        $REGISTRY update "$task_id" "status" "timeout"
        $REGISTRY log "$task_id" "任务超时 (${elapsed_min}分钟)" "error"
        
        # 发送超时通知
        local task_name
        task_name=$(echo "$task_info" | jq -r '.name')
        $NOTIFY error "$task_id" "$task_name" "任务超时 (${elapsed_min}分钟)"
        return
    fi
    
    # 2. 检查 tmux 会话状态
    if [[ -n "$tmux_session" && "$tmux_session" != "null" ]]; then
        if tmux has-session -t "$tmux_session" 2>/dev/null; then
            # 检查是否显示 shell 提示符（任务完成）
            if tmux capture-pane -t "$tmux_session" -p 2>/dev/null | grep -qE "^moltbot@.*%"; then
                # 任务完成，清理 tmux 并更新状态
                log "任务 $task_id 已完成"
                tmux kill-session -t "$tmux_session" 2>/dev/null
                $REGISTRY update "$task_id" "status" "done"
                $REGISTRY progress "$task_id" 100 "done"
                $NOTIFY complete "$task_id" "$(echo "$task_info" | jq -r '.name')"
            else
                log "任务 $task_id 运行中 (${elapsed_min}分钟)"
                if [[ $((elapsed_min % 5)) -eq 0 && $elapsed_min -gt 0 ]]; then
                    local task_name
                    task_name=$(echo "$task_info" | jq -r '.name')
                    $NOTIFY progress "$task_id" 50 "运行中 (${elapsed_min}分钟)"
                fi
            fi
        else
            # tmux 会话不存在，任务可能完成或失败
            log "任务 $task_id 的 tmux 会话已结束"
            
            # 检查输出文件判断是否成功
            local output_file="/tmp/codex-results/tasks/$task_id/output.log"
            if [[ -f "$output_file" ]] && grep -q "error\|failed\|Error\|Failed" "$output_file" 2>/dev/null; then
                $REGISTRY update "$task_id" "status" "failed"
                $REGISTRY log "$task_id" "任务执行失败" "error"
                
                local task_name
                task_name=$(echo "$task_info" | jq -r '.name')
                $NOTIFY error "$task_id" "$task_name" "执行失败"
            else
                # 没有错误，标记完成
                $REGISTRY complete "$task_id"
                
                local task_name
                task_name=$(echo "$task_info" | jq -r '.name')
                
                # 获取产出信息
                local outputs
                outputs=$(get_task_outputs "$task_id")
                
                $NOTIFY complete "$task_id" "$task_name" "" "$outputs"
            fi
        fi
    else
        # 无 tmux，检查后台进程
        # 如果没有进程在运行，标记为完成
        log "任务 $task_id 无 tmux 会话，检查进程..."
        
        # 检查任务目录是否有输出
        local task_dir="/tmp/codex-results/tasks/$task_id"
        if [[ -f "$task_dir/output.log" ]]; then
            local output
            output=$(cat "$task_dir/output.log" 2>/dev/null || echo "")
            
            if echo "$output" | grep -qiE "error|failed|exception"; then
                $REGISTRY update "$task_id" "status" "failed"
                $REGISTRY log "$task_id" "任务执行失败" "error"
                
                local task_name
                task_name=$(echo "$task_info" | jq -r '.name')
                $NOTIFY error "$task_id" "$task_name" "执行失败"
            else
                $REGISTRY complete "$task_id"
                
                local task_name
                task_name=$(echo "$task_info" | jq -r '.name')
                $NOTIFY complete "$task_id" "$task_name"
            fi
        fi
    fi
}

# 检查已完成待合并的任务
check_completed_tasks() {
    local done_tasks
    done_tasks=$(jq -r '.tasks[] | select(.status == "done" and (.pr == null or .pr == "null")) | .id' "$REGISTRY_FILE" 2>/dev/null || echo "")
    
    if [[ -n "$done_tasks" ]]; then
        log "发现已完成但未合并的任务: $done_tasks"
        # 这里可以触发自动合并流程
    fi
}

# 清理孤立 worktree
cleanup_worktrees() {
    log "检查孤立 worktree..."
    
    # 获取活跃分支
    local active_branches
    active_branches=$(jq -r '.tasks[] | select(.branch != "" and .branch != "null") | .branch' "$REGISTRY_FILE" 2>/dev/null || echo "")
    
    if command -v git &>/dev/null; then
        log "Worktree 检查完成"
    fi
}

# 主循环
main() {
    local interval="${1:-$CHECK_INTERVAL}"
    
    log "========== 任务监控启动 (间隔: ${interval}s, 超时: ${TASK_TIMEOUT}s) =========="
    
    while true; do
        check_tasks
        cleanup_worktrees
        
        sleep "$interval"
    done
}

# 单次检查
check() {
    check_tasks
}

# 帮助
show_help() {
    cat <<EOF
task-monitor.sh - 任务监控

用法: task-monitor.sh [command] [options]

环境变量:
  TASK_TIMEOUT      任务超时秒数 (默认 3600 = 1小时)
  CHECK_INTERVAL   检查间隔秒数 (默认 60)

命令:
  start [interval]
    启动监控循环
  
  check
    单次检查
  
  help
    帮助

示例:
  # 每分钟检查一次
  task-monitor.sh start 60
  
  # 超时设置为 30 分钟
  TASK_TIMEOUT=1800 task-monitor.sh start
EOF
}

# 主命令
command="${1:-}"
shift || true

case "$command" in
    start|run)
        main "$@"
        ;;
    check)
        check
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        show_help
        ;;
esac
