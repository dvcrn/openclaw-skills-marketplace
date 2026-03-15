#!/bin/bash
# AI主动检测模块
# 创建时间：2026-03-12 17:55
# 创建者：小米粒
# 功能：检测用户是否需要AI主动响应，分析用户意图，判断模型切换需求

# ============================================
# AI主动检测配置
# ============================================

# 需要AI主动响应的触发条件
AI_TRIGGERS=(
    "分析" "优化" "设计" "开发" "编程" "调试"
    "帮我" "请" "能否" "可以" "如何" "怎么"
    "为什么" "是什么" "有什么" "哪些"
    "建议" "推荐" "评价" "比较"
)

# 需要快速响应的触发条件
FAST_TRIGGERS=(
    "在吗" "在不在" "你好" "hi" "hello"
    "善" "对" "好" "嗯" "哦"
    "继续" "完成了吗" "执行"
)

# 需要深度分析的触发条件
DEEP_TRIGGERS=(
    "详细" "深入" "全面" "系统" "完整"
    "架构" "设计" "重构" "优化"
    "分析" "研究" "探索" "调研"
)

# ============================================
# 意图检测函数
# ============================================

# 检测用户意图
# 参数：$1 - 用户消息
# 返回：JSON格式的意图分析结果
detect_user_intent() {
    local message="$1"
    local intent="unknown"
    local confidence=0
    local need_ai=false
    local response_type="normal"
    
    # 转换为小写（便于匹配）
    local msg_lower=$(echo "$message" | tr '[:upper:]' '[:lower:]')
    
    # 检测AI触发词
    local ai_trigger_count=0
    for trigger in "${AI_TRIGGERS[@]}"; do
        if echo "$msg_lower" | grep -q "$trigger"; then
            ai_trigger_count=$((ai_trigger_count + 1))
        fi
    done
    
    # 检测快速响应触发词
    local fast_trigger_count=0
    for trigger in "${FAST_TRIGGERS[@]}"; do
        if echo "$msg_lower" | grep -q "$trigger"; then
            fast_trigger_count=$((fast_trigger_count + 1))
        fi
    done
    
    # 检测深度分析触发词
    local deep_trigger_count=0
    for trigger in "${DEEP_TRIGGERS[@]}"; do
        if echo "$msg_lower" | grep -q "$trigger"; then
            deep_trigger_count=$((deep_trigger_count + 1))
        fi
    done
    
    # 判断意图
    if [ "$fast_trigger_count" -gt 0 ]; then
        intent="greeting"
        confidence=90
        need_ai=true
        response_type="fast"
    elif [ "$deep_trigger_count" -gt 0 ]; then
        intent="deep_analysis"
        confidence=85
        need_ai=true
        response_type="deep"
    elif [ "$ai_trigger_count" -gt 0 ]; then
        intent="task_request"
        confidence=80
        need_ai=true
        response_type="normal"
    else
        intent="unknown"
        confidence=50
        need_ai=false
        response_type="normal"
    fi
    
    # 返回JSON格式结果
    cat << EOF
{
    "message": "$message",
    "intent": "$intent",
    "confidence": $confidence,
    "need_ai": $need_ai,
    "response_type": "$response_type",
    "triggers": {
        "ai": $ai_trigger_count,
        "fast": $fast_trigger_count,
        "deep": $deep_trigger_count
    },
    "timestamp": "$(date -Iseconds)"
}
EOF
}

# ============================================
# 模型需求判断
# ============================================

# 判断是否需要模型切换
# 参数：$1 - 用户消息
#       $2 - 当前模型（可选）
# 返回：JSON格式的模型切换建议
suggest_model_switch() {
    local message="$1"
    local current_model="${2:-main}"
    
    # 分析意图
    local intent_result=$(detect_user_intent "$message")
    local intent=$(echo "$intent_result" | grep -oP '"intent": "\K[^"]+')
    local response_type=$(echo "$intent_result" | grep -oP '"response_type": "\K[^"]+')
    local need_ai=$(echo "$intent_result" | grep -oP '"need_ai": \K[^,}]+')
    
    # 获取复杂度分析（调用complexity_analyzer模块）
    local complexity_result
    if [ -f "/root/.openclaw/workspace/skills/smart-model/modules/complexity_analyzer.sh" ]; then
        source /root/.openclaw/workspace/skills/smart-model/modules/complexity_analyzer.sh
        init_complexity_keywords
        complexity_result=$(analyze_message_complexity "$message")
    else
        # 如果complexity_analyzer不存在，使用简化版
        complexity_result='{"scores": {"total": 50}}'
    fi
    
    local complexity_score=$(echo "$complexity_result" | grep -oP '"total": \K[0-9]+')
    
    # 确定推荐模型
    local recommended_model="$current_model"
    local reason=""
    local should_switch=false
    
    # 根据响应类型和复杂度确定模型
    case "$response_type" in
        fast)
            recommended_model="flash"
            reason="快速响应需求"
            should_switch=true
            ;;
        deep)
            recommended_model="complex-deep"
            reason="深度分析需求"
            should_switch=true
            ;;
        normal)
            if [ "$complexity_score" -ge 80 ]; then
                recommended_model="complex-deep"
                reason="高复杂度任务"
                should_switch=true
            elif [ "$complexity_score" -ge 60 ]; then
                recommended_model="complex"
                reason="复杂任务"
                should_switch=true
            elif [ "$complexity_score" -lt 30 ]; then
                recommended_model="flash"
                reason="简单任务"
                should_switch=true
            fi
            ;;
    esac
    
    # 检查是否需要切换
    if [ "$recommended_model" != "$current_model" ]; then
        should_switch=true
    fi
    
    # 返回JSON格式结果
    cat << EOF
{
    "current_model": "$current_model",
    "recommended_model": "$recommended_model",
    "should_switch": $should_switch,
    "reason": "$reason",
    "complexity_score": $complexity_score,
    "response_type": "$response_type",
    "intent": "$intent",
    "need_ai": $need_ai,
    "timestamp": "$(date -Iseconds)"
}
EOF
}

# ============================================
# AI主动行为判断
# ============================================

# 判断AI是否应该主动响应
# 参数：$1 - 用户消息
#       $2 - 上下文信息（可选）
# 返回：JSON格式的AI行为建议
suggest_ai_behavior() {
    local message="$1"
    local context="${2:-{}}"
    
    # 分析意图
    local intent_result=$(detect_user_intent "$message")
    local intent=$(echo "$intent_result" | grep -oP '"intent": "\K[^"]+')
    local need_ai=$(echo "$intent_result" | grep -oP '"need_ai": \K[^,}]+')
    local confidence=$(echo "$intent_result" | grep -oP '"confidence": \K[0-9]+')
    
    # 判断AI行为
    local should_respond=false
    local behavior_type="passive"
    local suggested_action="wait"
    
    if [ "$need_ai" = "true" ]; then
        should_respond=true
        
        case "$intent" in
            greeting)
                behavior_type="fast_response"
                suggested_action="respond_immediately"
                ;;
            task_request)
                behavior_type="active"
                suggested_action="analyze_and_respond"
                ;;
            deep_analysis)
                behavior_type="proactive"
                suggested_action="deep_analysis_and_respond"
                ;;
            *)
                behavior_type="normal"
                suggested_action="respond_normally"
                ;;
        esac
    fi
    
    # 返回JSON格式结果
    cat << EOF
{
    "should_respond": $should_respond,
    "behavior_type": "$behavior_type",
    "suggested_action": "$suggested_action",
    "intent": "$intent",
    "confidence": $confidence,
    "timestamp": "$(date -Iseconds)"
}
EOF
}

# ============================================
# 综合分析函数
# ============================================

# 综合分析用户消息
# 参数：$1 - 用户消息
#       $2 - 当前模型（可选）
#       $3 - 上下文信息（可选）
# 返回：JSON格式的综合分析结果
analyze_message_comprehensive() {
    local message="$1"
    local current_model="${2:-main}"
    local context="${3:-{}}"
    
    # 执行各项分析
    local intent_result=$(detect_user_intent "$message")
    local model_result=$(suggest_model_switch "$message" "$current_model")
    local behavior_result=$(suggest_ai_behavior "$message" "$context")
    
    # 提取关键信息
    local intent=$(echo "$intent_result" | grep -oP '"intent": "\K[^"]+')
    local recommended_model=$(echo "$model_result" | grep -oP '"recommended_model": "\K[^"]+')
    local should_switch=$(echo "$model_result" | grep -oP '"should_switch": \K[^,}]+')
    local should_respond=$(echo "$behavior_result" | grep -oP '"should_respond": \K[^,}]+')
    local behavior_type=$(echo "$behavior_result" | grep -oP '"behavior_type": "\K[^"]+')
    
    # 返回综合结果
    cat << EOF
{
    "message": "$message",
    "current_model": "$current_model",
    "analysis": {
        "intent": $intent_result,
        "model": $model_result,
        "behavior": $behavior_result
    },
    "recommendation": {
        "recommended_model": "$recommended_model",
        "should_switch": $should_switch,
        "should_respond": $should_respond,
        "behavior_type": "$behavior_type"
    },
    "timestamp": "$(date -Iseconds)"
}
EOF
}

# ============================================
# 快速检测函数（性能优化版）
# ============================================

# 快速检测是否需要AI响应
# 参数：$1 - 用户消息
# 返回：true/false
need_ai_response_fast() {
    local message="$1"
    local msg_lower=$(echo "$message" | tr '[:upper:]' '[:lower:]')
    
    # 快速检测触发词
    for trigger in "${AI_TRIGGERS[@]}" "${FAST_TRIGGERS[@]}"; do
        if echo "$msg_lower" | grep -q "$trigger"; then
            echo "true"
            return 0
        fi
    done
    
    echo "false"
}

# 快速获取推荐模型
# 参数：$1 - 用户消息
# 返回：推荐模型名称
get_recommended_model_fast() {
    local message="$1"
    local msg_lower=$(echo "$message" | tr '[:upper:]' '[:lower:]')
    
    # 快速检测响应类型
    for trigger in "${FAST_TRIGGERS[@]}"; do
        if echo "$msg_lower" | grep -q "$trigger"; then
            echo "flash"
            return 0
        fi
    done
    
    for trigger in "${DEEP_TRIGGERS[@]}"; do
        if echo "$msg_lower" | grep -q "$trigger"; then
            echo "complex-deep"
            return 0
        fi
    done
    
    # 默认返回main模型
    echo "main"
}

# ============================================
# 主函数（用于测试）
# ============================================

main() {
    echo "=== AI主动检测模块测试 ==="
    echo ""
    
    # 测试1：检测用户意图
    echo "测试1：检测用户意图"
    local test_msg1="帮我分析这个系统的架构设计"
    echo "消息：$test_msg1"
    detect_user_intent "$test_msg1"
    echo ""
    
    # 测试2：检测快速响应
    echo "测试2：检测快速响应"
    local test_msg2="在吗？"
    echo "消息：$test_msg2"
    detect_user_intent "$test_msg2"
    echo ""
    
    # 测试3：模型切换建议
    echo "测试3：模型切换建议"
    local test_msg3="请详细分析这个复杂算法的优化方案"
    echo "消息：$test_msg3"
    suggest_model_switch "$test_msg3" "main"
    echo ""
    
    # 测试4：AI行为建议
    echo "测试4：AI行为建议"
    local test_msg4="如何优化数据库性能？"
    echo "消息：$test_msg4"
    suggest_ai_behavior "$test_msg4"
    echo ""
    
    # 测试5：快速检测
    echo "测试5：快速检测"
    echo "消息：$test_msg1 -> 需要AI：$(need_ai_response_fast "$test_msg1")，模型：$(get_recommended_model_fast "$test_msg1")"
    echo "消息：$test_msg2 -> 需要AI：$(need_ai_response_fast "$test_msg2")，模型：$(get_recommended_model_fast "$test_msg2")"
    echo "消息：$test_msg3 -> 需要AI：$(need_ai_response_fast "$test_msg3")，模型：$(get_recommended_model_fast "$test_msg3")"
    echo ""
    
    # 测试6：综合分析
    echo "测试6：综合分析"
    local test_msg6="请帮我设计一个完整的微服务架构，包括服务发现、负载均衡、容错机制等"
    echo "消息：$test_msg6"
    analyze_message_comprehensive "$test_msg6" "main"
    echo ""
    
    echo "=== 测试完成 ==="
}

# 如果直接运行此脚本，执行主函数
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    main "$@"
fi
