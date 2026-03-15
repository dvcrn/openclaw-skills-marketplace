#!/bin/bash
# Smart Model Switch v2.0 - 主控制器
# 创建时间：2026-03-12 17:56
# 创建者：小米粒
# 功能：整合4个核心模块，实现智能模型切换

# ============================================
# 配置
# ============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULES_DIR="$SCRIPT_DIR/modules"

# 日志配置
LOG_DIR="/tmp/smart_model_logs"
LOG_FILE="$LOG_DIR/smart_model_$(date +%Y%m%d).log"

# 创建日志目录
mkdir -p "$LOG_DIR"

# ============================================
# 加载模块
# ============================================

echo "[$(date -Iseconds)] 加载Smart Model v2.0模块..." >> "$LOG_FILE"

# 加载文件类型检测模块
if [ -f "$MODULES_DIR/file_type_detector.sh" ]; then
    source "$MODULES_DIR/file_type_detector.sh"
    init_file_type_map
    echo "[$(date -Iseconds)] ✅ 文件类型检测模块已加载" >> "$LOG_FILE"
else
    echo "[$(date -Iseconds)] ❌ 文件类型检测模块不存在" >> "$LOG_FILE"
    exit 1
fi

# 加载复杂度分析模块
if [ -f "$MODULES_DIR/complexity_analyzer.sh" ]; then
    source "$MODULES_DIR/complexity_analyzer.sh"
    init_complexity_keywords
    echo "[$(date -Iseconds)] ✅ 复杂度分析模块已加载" >> "$LOG_FILE"
else
    echo "[$(date -Iseconds)] ❌ 复杂度分析模块不存在" >> "$LOG_FILE"
    exit 1
fi

# 加载上下文监控模块
if [ -f "$MODULES_DIR/context_monitor.sh" ]; then
    source "$MODULES_DIR/context_monitor.sh"
    echo "[$(date -Iseconds)] ✅ 上下文监控模块已加载" >> "$LOG_FILE"
else
    echo "[$(date -Iseconds)] ❌ 上下文监控模块不存在" >> "$LOG_FILE"
    exit 1
fi

# 加载AI主动检测模块
if [ -f "$MODULES_DIR/ai_detector.sh" ]; then
    source "$MODULES_DIR/ai_detector.sh"
    echo "[$(date -Iseconds)] ✅ AI主动检测模块已加载" >> "$LOG_FILE"
else
    echo "[$(date -Iseconds)] ❌ AI主动检测模块不存在" >> "$LOG_FILE"
    exit 1
fi

# ============================================
# 核心功能
# ============================================

# 智能模型切换（主入口）
# 参数：$1 - 用户消息
#       $2 - 文件路径（可选）
#       $3 - 当前模型（可选）
# 返回：JSON格式的推荐结果
smart_model_switch() {
    local message="$1"
    local file_path="${2:-}"
    local current_model="${3:-main}"
    
    echo "[$(date -Iseconds)] 开始智能模型切换分析..." >> "$LOG_FILE"
    echo "[$(date -Iseconds)] 消息：$message" >> "$LOG_FILE"
    echo "[$(date -Iseconds)] 文件：$file_path" >> "$LOG_FILE"
    echo "[$(date -Iseconds)] 当前模型：$current_model" >> "$LOG_FILE"
    
    # 步骤1：文件类型检测
    local file_type="none"
    local file_model="main"
    
    if [ -n "$file_path" ] && [ -e "$file_path" ]; then
        file_type=$(detect_file_type "$file_path")
        file_model=$(get_recommended_model "$file_type")
        echo "[$(date -Iseconds)] 文件类型：$file_type → 模型：$file_model" >> "$LOG_FILE"
    fi
    
    # 步骤2：复杂度分析
    local complexity_result
    if [ -n "$file_path" ] && [ -e "$file_path" ]; then
        complexity_result=$(analyze_file_complexity "$file_path")
    else
        complexity_result=$(analyze_message_complexity "$message")
    fi
    
    local complexity_score=$(echo "$complexity_result" | grep -oP '"total": \K[0-9]+')
    local complexity_model=$(echo "$complexity_result" | grep -oP '"recommended_model": "\K[^"]+')
    
    echo "[$(date -Iseconds)] 复杂度得分：$complexity_score → 模型：$complexity_model" >> "$LOG_FILE"
    
    # 步骤3：上下文监控
    local context_result=$(monitor_context)
    local context_usage=$(echo "$context_result" | grep -oP '"usage": \K[0-9]+')
    local context_level=$(echo "$context_result" | grep -oP '"level": "\K[^"]+')
    
    echo "[$(date -Iseconds)] 上下文使用率：$context_usage% → 级别：$context_level" >> "$LOG_FILE"
    
    # 步骤4：AI主动检测
    local ai_result=$(analyze_message_comprehensive "$message" "$current_model")
    local ai_model=$(echo "$ai_result" | grep -oP '"recommended_model": "\K[^"]+')
    local should_respond=$(echo "$ai_result" | grep -oP '"should_respond": \K[^,}]+')
    local behavior_type=$(echo "$ai_result" | grep -oP '"behavior_type": "\K[^"]+')
    
    echo "[$(date -Iseconds)] AI检测：$behavior_type → 模型：$ai_model" >> "$LOG_FILE"
    
    # 步骤5：综合决策
    local final_model="$current_model"
    local reason=""
    local should_switch=false
    
    # 优先级：文件类型 > 上下文紧急度 > 复杂度 > AI检测
    if [ "$file_type" != "none" ] && [ "$file_model" != "$current_model" ]; then
        # 文件类型驱动
        final_model="$file_model"
        reason="文件类型：$file_type"
        should_switch=true
        echo "[$(date -Iseconds)] 决策：文件类型驱动" >> "$LOG_FILE"
    elif [ "$context_level" = "critical" ]; then
        # 上下文紧急
        final_model="flash"
        reason="上下文紧急"
        should_switch=true
        echo "[$(date -Iseconds)] 决策：上下文紧急" >> "$LOG_FILE"
    elif [ "$complexity_score" -ge 80 ]; then
        # 高复杂度
        final_model="complex-deep"
        reason="高复杂度任务"
        should_switch=true
        echo "[$(date -Iseconds)] 决策：高复杂度" >> "$LOG_FILE"
    elif [ "$behavior_type" = "fast_response" ]; then
        # 快速响应
        final_model="flash"
        reason="快速响应需求"
        should_switch=true
        echo "[$(date -Iseconds)] 决策：快速响应" >> "$LOG_FILE"
    elif [ "$ai_model" != "$current_model" ]; then
        # AI检测建议
        final_model="$ai_model"
        reason="AI检测建议"
        should_switch=true
        echo "[$(date -Iseconds)] 决策：AI检测建议" >> "$LOG_FILE"
    else
        # 保持当前模型
        final_model="$current_model"
        reason="无需切换"
        should_switch=false
        echo "[$(date -Iseconds)] 决策：保持当前模型" >> "$LOG_FILE"
    fi
    
    # 返回综合结果
    cat << EOF
{
    "input": {
        "message": "$message",
        "file": "$file_path",
        "current_model": "$current_model"
    },
    "analysis": {
        "file_type": "$file_type",
        "file_model": "$file_model",
        "complexity_score": $complexity_score,
        "complexity_model": "$complexity_model",
        "context_usage": $context_usage,
        "context_level": "$context_level",
        "ai_model": "$ai_model",
        "behavior_type": "$behavior_type"
    },
    "recommendation": {
        "final_model": "$final_model",
        "should_switch": $should_switch,
        "reason": "$reason",
        "should_respond": $should_respond
    },
    "timestamp": "$(date -Iseconds)"
}
EOF
    
    echo "[$(date -Iseconds)] 最终推荐模型：$final_model（原因：$reason）" >> "$LOG_FILE"
}

# 快速模型切换（简化版，性能优化）
# 参数：$1 - 用户消息
# 返回：推荐模型名称
smart_model_switch_fast() {
    local message="$1"
    
    # 快速检测
    local ai_need=$(need_ai_response_fast "$message")
    
    if [ "$ai_need" = "true" ]; then
        get_recommended_model_fast "$message"
    else
        echo "main"
    fi
}

# ============================================
# 批量处理
# ============================================

# 批量分析文件
# 参数：$@ - 文件路径列表
# 返回：JSON格式的批量分析结果
batch_analyze_files() {
    local files=("$@")
    local result="["
    local first=true
    
    for file in "${files[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            result+=","
        fi
        
        local analysis=$(smart_model_switch "" "$file" "main")
        result+="$analysis"
    done
    
    result+="]"
    echo "$result"
}

# ============================================
# 监控和统计
# ============================================

# 获取系统状态
get_system_status() {
    local total_logs=$(find "$LOG_DIR" -name "*.log" | wc -l)
    local today_logs=$(wc -l < "$LOG_FILE" 2>/dev/null || echo "0")
    
    cat << EOF
{
    "version": "2.0.0",
    "modules": {
        "file_type_detector": "loaded",
        "complexity_analyzer": "loaded",
        "context_monitor": "loaded",
        "ai_detector": "loaded"
    },
    "logs": {
        "total_files": $total_logs,
        "today_lines": $today_logs
    },
    "timestamp": "$(date -Iseconds)"
}
EOF
}

# ============================================
# 测试函数
# ============================================

test_smart_model() {
    echo "=== Smart Model v2.0 测试 ==="
    echo ""
    
    # 测试1：简单消息
    echo "测试1：简单消息"
    local test_msg1="在吗？"
    echo "消息：$test_msg1"
    smart_model_switch "$test_msg1" "" "main"
    echo ""
    
    # 测试2：代码任务
    echo "测试2：代码任务"
    local test_msg2="帮我写一个Python函数实现快速排序"
    echo "消息：$test_msg2"
    smart_model_switch "$test_msg2" "" "main"
    echo ""
    
    # 测试3：深度分析
    echo "测试3：深度分析"
    local test_msg3="请详细分析这个分布式系统的架构设计，包括服务发现、负载均衡、容错机制等核心功能"
    echo "消息：$test_msg3"
    smart_model_switch "$test_msg3" "" "main"
    echo ""
    
    # 测试4：快速切换
    echo "测试4：快速切换"
    echo "消息：$test_msg1 -> $(smart_model_switch_fast "$test_msg1")"
    echo "消息：$test_msg2 -> $(smart_model_switch_fast "$test_msg2")"
    echo "消息：$test_msg3 -> $(smart_model_switch_fast "$test_msg3")"
    echo ""
    
    # 测试5：系统状态
    echo "测试5：系统状态"
    get_system_status
    echo ""
    
    echo "=== 测试完成 ==="
}

# ============================================
# 主入口
# ============================================

case "${1:-}" in
    --test|-t)
        test_smart_model
        ;;
    --fast|-f)
        smart_model_switch_fast "$2"
        ;;
    --status|-s)
        get_system_status
        ;;
    --batch|-b)
        shift
        batch_analyze_files "$@"
        ;;
    *)
        # 默认：智能模型切换
        if [ -n "$1" ]; then
            smart_model_switch "$1" "${2:-}" "${3:-main}"
        else
            echo "用法："
            echo "  $0 \"消息\" [文件] [当前模型]  - 智能分析"
            echo "  $0 --fast \"消息\"             - 快速切换"
            echo "  $0 --status                   - 系统状态"
            echo "  $0 --test                     - 运行测试"
            echo "  $0 --batch 文件1 文件2 ...    - 批量分析"
        fi
        ;;
esac
