#!/bin/bash
# task-splitter.sh - 任务自动拆解器
# 基于关键词和模式自动将需求拆解为子任务

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REGISTRY="$SCRIPT_DIR/task-registry.sh"

# 任务模式定义
# 格式: 关键词 -> 子任务模板
declare -A TASK_PATTERNS=(
    ["用户"]="用户相关功能"
    ["登录"]="登录功能"
    ["注册"]="注册功能"
    ["密码"]="密码找回"
    ["API"]="API接口开发"
    ["前端"]="前端页面开发"
    ["后端"]="后端逻辑开发"
    ["数据库"]="数据库设计"
    ["测试"]="单元测试编写"
    ["修复"]="Bug修复"
    ["重构"]="代码重构"
    ["迁移"]="数据迁移"
    ["文档"]="文档编写"
    ["部署"]="部署配置"
)

# 拆分任务描述
split_task() {
    local description="$1"
    local parent_id="${2:-}"
    
    echo "🔍 分析任务: $description"
    echo ""
    
    # 提取关键词
    local keywords=()
    for key in "${!TASK_PATTERNS[@]}"; do
        if echo "$description" | grep -qi "$key"; then
            keywords+=("$key")
        fi
    done
    
    # 如果没有匹配，使用通用拆分
    if [[ ${#keywords[@]} -eq 0 ]]; then
        keywords=("开发" "测试")
    fi
    
    # 根据关键词组合生成子任务
    local subtasks=()
    
    # 检查是否包含"多个"相关的词
    if echo "$description" | grep -qiE "(多个|分别|包括|以及|和|,)"; then
        # 复杂任务，拆分为多个
        subtasks+=("后端API开发")
        subtasks+=("前端页面开发")
        subtasks+=("单元测试")
    else
        # 简单任务
        subtasks+=("功能开发")
    fi
    
    # 添加测试任务
    if ! echo "$description" | grep -qi "无需测试"; then
        subtasks+=("测试验证")
    fi
    
    # 创建子任务
    local created=()
    local task_index=1
    
    for subtask in "${subtasks[@]}"; do
        local task_name
        task_name="[$task_index/${#subtasks[@]}] $subtask"
        
        # 创建任务
        local task_id
        task_id=$($REGISTRY create "$task_name" "$description" "$parent_id")
        
        # 如果有父任务，关联起来
        if [[ -n "$parent_id" ]]; then
            $REGISTRY add-child "$parent_id" "$task_id"
        fi
        
        created+=("$task_id")
        echo "  ✅ 创建子任务: $task_name (ID: $task_id)"
        
        ((task_index++))
    done
    
    echo ""
    echo "📦 共创建 ${#created[@]} 个子任务"
    
    # 返回第一个子任务ID
    echo "${created[0]}"
}

# AI 智能拆分（调用 LLM）
ai_split_task() {
    local description="$1"
    local parent_id="${2:-}"
    local model="${3:-}"
    
    echo "🤖 AI 智能拆分任务..."
    echo ""
    
    # 构建 prompt
    local prompt
    prompt=$(cat <<EOF
请将以下开发任务拆分为子任务列表。返回 JSON 数组格式。

任务: $description

要求:
1. 每个子任务应该是一个独立可执行的工作单元
2. 包含: 名称、描述、优先级
3. 考虑并行可能性，能并行的任务标注 same_level
4. 考虑依赖关系

返回格式:
[{"name": "子任务名", "description": "描述", "priority": "high/medium/low", "parallel": true/false}]
EOF
)
    
    # 调用 LLM (如果可用)
    local result
    if command -v codex &>/dev/null; then
        result=$(codex -t "$prompt" 2>/dev/null || echo "[]")
    elif command -v claude &>/dev/null; then
        result=$(claude -p "$prompt" 2>/dev/null || echo "[]")
    else
        # 回退到规则拆分
        echo "⚠️ 未找到 LLM 工具，回退到规则拆分"
        split_task "$description" "$parent_id"
        return
    fi
    
    # 解析结果并创建任务
    local created=()
    local task_count
    task_count=$(echo "$result" | jq 'length' 2>/dev/null || echo "0")
    
    if [[ "$task_count" -eq 0 ]]; then
        echo "⚠️ AI 拆分失败，回退到规则拆分"
        split_task "$description" "$parent_id"
        return
    fi
    
    local i=0
    while [[ $i -lt $task_count ]]; do
        local name desc priority
        name=$(echo "$result" | jq -r ".[$i].name")
        desc=$(echo "$result" | jq -r ".[$i].description")
        
        local task_id
        task_id=$($REGISTRY create "$name" "$desc" "$parent_id")
        
        if [[ -n "$parent_id" ]]; then
            $REGISTRY add-child "$parent_id" "$task_id"
        fi
        
        created+=("$task_id")
        echo "  ✅ $name (ID: $task_id)"
        
        ((i++))
    done
    
    echo ""
    echo "📦 AI 拆分完成: ${#created[@]} 个子任务"
    echo "${created[0]}"
}

# 简单模式匹配拆分
simple_split() {
    local description="$1"
    local parent_id="${2:-}"
    
    echo "📋 任务拆分"
    echo "================================================================"
    echo "原始任务: $description"
    echo "================================================================"
    echo ""
    
    # 简单拆分策略
    local subtasks=()
    
    # 检查关键词
    if echo "$description" | grep -qi "API"; then
        subtasks+=("后端API开发")
    fi
    
    if echo "$description" | grep -qi "前端|界面|页面"; then
        subtasks+=("前端页面开发")
    fi
    
    if echo "$description" | grep -qi "数据库|表|模型"; then
        subtasks+=("数据库设计")
    fi
    
    if echo "$description" | grep -qi "测试"; then
        subtasks+=("编写测试")
    fi
    
    if echo "$description" | grep -qi "文档|说明"; then
        subtasks+=("编写文档")
    fi
    
    # 默认添加开发任务
    if [[ ${#subtasks[@]} -eq 0 ]]; then
        subtasks+=("功能开发")
        subtasks+=("测试验证")
    fi
    
    # 创建任务
    local created=()
    local i=1
    for task in "${subtasks[@]}"; do
        local task_id
        task_id=$($REGISTRY create "[$i/${#subtasks[@]}] $task" "$description" "$parent_id")
        
        if [[ -n "$parent_id" ]]; then
            $REGISTRY add-child "$parent_id" "$task_id"
        fi
        
        created+=("$task_id")
        echo "  ✅ [$i/${#subtasks[@]}] $task"
        
        ((i++))
    done
    
    echo ""
    echo "📦 共创建 ${#created[@]} 个子任务"
    
    echo "${created[0]}"
}

# 并行任务分析
analyze_parallel() {
    local parent_id="$1"
    
    echo "🔗 并行任务分析"
    echo "================================================================"
    
    # 获取所有子任务
    local children
    children=$($REGISTRY get "$parent_id" | jq -r '.children[]' 2>/dev/null || echo "")
    
    if [[ -z "$children" ]]; then
        echo "无子任务"
        return
    fi
    
    local parallel_groups=()
    local current_group=()
    
    while IFS= read -r child_id; do
        [[ -z "$child_id" ]] && continue
        
        local task_info
        task_info=$($REGISTRY get "$child_id")
        
        # 检查是否可以并行
        local can_parallel
        can_parallel=$(echo "$task_info" | jq -r '.parallel // false')
        
        if [[ "$can_parallel" == "true" ]]; then
            current_group+=("$child_id")
        else
            if [[ ${#current_group[@]} -gt 0 ]]; then
                parallel_groups+=("${current_group[*]}")
                current_group=()
            fi
            parallel_groups+=("$child_id")
        fi
    done <<< "$children"
    
    # 添加最后的组
    if [[ ${#current_group[@]} -gt 0 ]]; then
        parallel_groups+=("${current_group[*]}")
    fi
    
    echo "并行执行组:"
    local group_num=1
    for group in "${parallel_groups[@]}"; do
        echo "  组 $group_num: $group"
        ((group_num++))
    done
}

# 依赖分析
analyze_dependencies() {
    local parent_id="$1"
    
    echo "🔗 依赖关系分析"
    echo "================================================================"
    
    local children
    children=$($REGISTRY get "$parent_id" | jq -r '.children[]' 2>/dev/null || echo "")
    
    if [[ -z "$children" ]]; then
        echo "无子任务"
        return
    fi
    
    while IFS= read -r child_id; do
        [[ -z "$child_id" ]] && continue
        
        local task_info
        task_info=$($REGISTRY get "$child_id")
        
        local name depends
        name=$(echo "$task_info" | jq -r '.name')
        depends=$(echo "$task_info" | jq -r '.depends_on // [] | join(", ")')
        
        if [[ -n "$depends" ]]; then
            echo "  $name → 依赖: $depends"
        else
            echo "  $name → 无依赖"
        fi
    done <<< "$children"
}

# 帮助
show_help() {
    cat <<EOF
task-splitter.sh - 任务自动拆解器

用法: task-splitter.sh <command> [options]

命令:
  split <description> [parent_id]
    基于规则拆分任务
  
  ai-split <description> [parent_id] [model]
    AI 智能拆分 (需要 LLM 工具)
  
  simple <description> [parent_id]
    简单模式匹配拆分
  
  analyze-parallel <parent_id>
    分析并行任务组
  
  analyze-deps <parent_id>
    分析依赖关系

示例:
  task-splitter.sh split "实现用户注册和登录功能"
  task-splitter.sh ai-split "实现用户注册和登录功能"
  task-splitter.sh analyze-parallel task-20260309-xxxx
EOF
}

# 主命令
main() {
    local command="${1:-}"
    shift || true
    
    case "$command" in
        split)
            split_task "$@"
            ;;
        ai-split|ai)
            ai_split_task "$@"
            ;;
        simple)
            simple_split "$@"
            ;;
        analyze-parallel|parallel)
            analyze_parallel "$1"
            ;;
        analyze-deps|deps)
            analyze_dependencies "$1"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            show_help
            ;;
    esac
}

main "$@"
