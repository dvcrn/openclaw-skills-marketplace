#!/bin/bash
# Model Switcher API
# 创建时间：2026-03-12 18:20
# 创建者：小米粒
# 功能：提供统一的模型切换API接口

# ============================================
# 版权声明
# ============================================
# MIT License
# Copyright (c) 2026 米粒儿 (miliger)
# GitHub: https://github.com/zhaog100/openclaw-skills
# ClawHub: https://clawhub.com
# 
# 免费使用、修改和重新分发时需注明出处

# ============================================
# 配置
# ============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SMART_MODEL_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="/tmp/smart_model_api"
LOG_FILE="$LOG_DIR/model_switcher_api_$(date +%Y%m%d).log"
CACHE_DIR="/tmp/smart_model_cache"

# 创建目录
mkdir -p "$LOG_DIR" "$CACHE_DIR"

# ============================================
# 模型配置
# ============================================

# 模型别名映射
declare -A MODEL_ALIASES
MODEL_ALIASES=(
    ["flash"]="快速响应模型"
    ["main"]="标准响应模型"
    ["complex"]="复杂任务模型"
    ["complex-deep"]="深度分析模型"
    ["coding"]="代码专用模型"
    ["vision"]="视觉处理模型"
    ["audio"]="音频处理模型"
)

# 实际模型ID映射（需要根据实际配置调整）
declare -A MODEL_IDS
MODEL_IDS=(
    ["flash"]="zai/glm-4-flash"
    ["main"]="zai/glm-5"
    ["complex"]="zai/glm-5"
    ["complex-deep"]="zai/glm-5"
    ["coding"]="zai/glm-5"
    ["vision"]="zai/glm-4v"
    ["audio"]="zai/glm-4"
)

# ============================================
# 核心API函数
# ============================================

# 获取当前模型
# 参数：$1 - 会话ID（可选）
# 返回：当前模型信息（JSON格式）
get_current_model() {
    local session_id="${1:-default}"
    local cache_file="$CACHE_DIR/current_model_${session_id}.json"
    
    # 检查缓存
    if [ -f "$cache_file" ]; then
        cat "$cache_file"
        return 0
    fi
    
    # 默认返回main模型
    cat << EOF
{
    "session_id": "$session_id",
    "model": "main",
    "model_id": "${MODEL_IDS[main]}",
    "alias": "${MODEL_ALIASES[main]}",
    "timestamp": "$(date -Iseconds)"
}
EOF
}

# 设置模型
# 参数：$1 - 模型名称
#       $2 - 会话ID（可选）
# 返回：设置结果（JSON格式）
set_model() {
    local model_name="$1"
    local session_id="${2:-default}"
    local cache_file="$CACHE_DIR/current_model_${session_id}.json"
    
    # 验证模型名称
    if [ -z "${MODEL_ALIASES[$model_name]}" ]; then
        echo '{"error": "invalid model name"}'
        return 1
    fi
    
    echo "[$(date -Iseconds)] 设置模型：$model_name (session=$session_id)" >> "$LOG_FILE"
    
    # 保存到缓存
    cat > "$cache_file" << EOF
{
    "session_id": "$session_id",
    "model": "$model_name",
    "model_id": "${MODEL_IDS[$model_name]}",
    "alias": "${MODEL_ALIASES[$model_name]}",
    "timestamp": "$(date -Iseconds)"
}
EOF
    
    # 返回结果
    cat "$cache_file"
}

# 切换模型
# 参数：$1 - 用户消息
#       $2 - 文件路径（可选）
#       $3 - 会话ID（可选）
# 返回：切换结果（JSON格式）
switch_model() {
    local message="$1"
    local file_path="${2:-}"
    local session_id="${3:-default}"
    
    echo "[$(date -Iseconds)] 模型切换请求：session=$session_id" >> "$LOG_FILE"
    
    # 获取当前模型
    local current=$(get_current_model "$session_id")
    local current_model=$(echo "$current" | grep -oP '"model": "\K[^"]+')
    
    # 调用Smart Model进行推荐
    if [ -f "$SMART_MODEL_DIR/smart-model-v2.sh" ]; then
        source "$SMART_MODEL_DIR/smart-model-v2.sh"
        
        local recommendation=$(smart_model_switch "$message" "$file_path" "$current_model")
        local recommended_model=$(echo "$recommendation" | grep -oP '"final_model": "\K[^"]+')
        local should_switch=$(echo "$recommendation" | grep -oP '"should_switch": \K[^,}]+')
        local reason=$(echo "$recommendation" | grep -oP '"reason": "\K[^"]+')
        
        # 执行切换
        if [ "$should_switch" = "true" ] && [ "$recommended_model" != "$current_model" ]; then
            local result=$(set_model "$recommended_model" "$session_id")
            
            # 返回切换结果
            cat << EOF
{
    "session_id": "$session_id",
    "switched": true,
    "from_model": "$current_model",
    "to_model": "$recommended_model",
    "reason": "$reason",
    "timestamp": "$(date -Iseconds)"
}
EOF
        else
            # 无需切换
            cat << EOF
{
    "session_id": "$session_id",
    "switched": false,
    "current_model": "$current_model",
    "recommended_model": "$recommended_model",
    "reason": "$reason",
    "timestamp": "$(date -Iseconds)"
}
EOF
        fi
    else
        echo '{"error": "smart model not found"}'
        return 1
    fi
}

# 批量切换模型
# 参数：$@ - 会话ID列表
# 返回：批量切换结果（JSON格式）
batch_switch_models() {
    local sessions=("$@")
    local results="["
    local first=true
    
    for session_id in "${sessions[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            results+=","
        fi
        
        local current=$(get_current_model "$session_id")
        results+="$current"
    done
    
    results+="]"
    echo "$results"
}

# ============================================
# 辅助函数
# ============================================

# 获取所有可用模型
get_available_models() {
    cat << EOF
{
    "models": [
        {"name": "flash", "alias": "${MODEL_ALIASES[flash]}", "model_id": "${MODEL_IDS[flash]}"},
        {"name": "main", "alias": "${MODEL_ALIASES[main]}", "model_id": "${MODEL_IDS[main]}"},
        {"name": "complex", "alias": "${MODEL_ALIASES[complex]}", "model_id": "${MODEL_IDS[complex]}"},
        {"name": "complex-deep", "alias": "${MODEL_ALIASES[complex-deep]}", "model_id": "${MODEL_IDS[complex-deep]}"},
        {"name": "coding", "alias": "${MODEL_ALIASES[coding]}", "model_id": "${MODEL_IDS[coding]}"},
        {"name": "vision", "alias": "${MODEL_ALIASES[vision]}", "model_id": "${MODEL_IDS[vision]}"},
        {"name": "audio", "alias": "${MODEL_ALIASES[audio]}", "model_id": "${MODEL_IDS[audio]}"}
    ],
    "timestamp": "$(date -Iseconds)"
}
EOF
}

# 清除缓存
clear_cache() {
    local session_id="${1:-all}"
    
    if [ "$session_id" = "all" ]; then
        rm -rf "$CACHE_DIR"/*
        echo '{"status": "all cache cleared"}'
    else
        rm -f "$CACHE_DIR/current_model_${session_id}.json"
        echo "{\"status\": \"cache cleared for session: $session_id\"}"
    fi
}

# 获取API状态
get_api_status() {
    local total_sessions=$(find "$CACHE_DIR" -name "current_model_*.json" | wc -l)
    
    cat << EOF
{
    "version": "2.1.0",
    "status": "running",
    "cache_dir": "$CACHE_DIR",
    "total_sessions": $total_sessions,
    "available_models": 7,
    "timestamp": "$(date -Iseconds)"
}
EOF
}

# ============================================
# 主入口
# ============================================

case "${1:-}" in
    --get|-g)
        get_current_model "${2:-default}"
        ;;
    --set|-s)
        set_model "$2" "${3:-default}"
        ;;
    --switch|-S)
        switch_model "$2" "${3:-}" "${4:-default}"
        ;;
    --batch|-b)
        shift
        batch_switch_models "$@"
        ;;
    --models|-m)
        get_available_models
        ;;
    --clear|-c)
        clear_cache "${2:-all}"
        ;;
    --status|-t)
        get_api_status
        ;;
    --test)
        echo "=== Model Switcher API 测试 ==="
        echo ""
        
        echo "测试1：获取当前模型"
        get_current_model "test_session"
        echo ""
        
        echo "测试2：设置模型"
        set_model "flash" "test_session"
        echo ""
        
        echo "测试3：切换模型"
        switch_model "帮我分析这个系统的架构设计" "" "test_session"
        echo ""
        
        echo "测试4：获取所有模型"
        get_available_models
        echo ""
        
        echo "测试5：API状态"
        get_api_status
        echo ""
        
        echo "测试6：清除缓存"
        clear_cache "test_session"
        echo ""
        
        echo "=== 测试完成 ==="
        ;;
    *)
        echo "用法："
        echo "  $0 --get [会话ID]                     - 获取当前模型"
        echo "  $0 --set 模型名称 [会话ID]            - 设置模型"
        echo "  $0 --switch 消息 [文件] [会话ID]      - 智能切换模型"
        echo "  $0 --batch 会话1 会话2 ...            - 批量切换"
        echo "  $0 --models                           - 获取所有模型"
        echo "  $0 --clear [会话ID|all]               - 清除缓存"
        echo "  $0 --status                           - API状态"
        echo "  $0 --test                             - 运行测试"
        ;;
esac
