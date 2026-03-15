#!/bin/bash
# OpenClaw集成钩子
# 创建时间：2026-03-12 18:16
# 创建者：小米粒
# 功能：与OpenClaw深度集成，自动触发模型切换

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
LOG_DIR="/tmp/smart_model_integrations"
LOG_FILE="$LOG_DIR/openclaw_hook_$(date +%Y%m%d).log"

# 创建日志目录
mkdir -p "$LOG_DIR"

# ============================================
# 核心函数
# ============================================

# OpenClaw消息钩子
# 当OpenClaw收到消息时调用
# 参数：$1 - 用户消息
#       $2 - 文件路径（可选）
#       $3 - 当前会话ID（可选）
# 返回：推荐的模型配置
openclaw_message_hook() {
    local message="$1"
    local file_path="${2:-}"
    local session_id="${3:-default}"
    
    echo "[$(date -Iseconds)] OpenClaw钩子触发：session=$session_id" >> "$LOG_FILE"
    echo "[$(date -Iseconds)] 消息：$message" >> "$LOG_FILE"
    
    # 加载Smart Model主控制器
    if [ -f "$SMART_MODEL_DIR/smart-model-v2.sh" ]; then
        source "$SMART_MODEL_DIR/smart-model-v2.sh"
        
        # 获取模型推荐
        local result=$(smart_model_switch "$message" "$file_path" "main")
        local recommended_model=$(echo "$result" | grep -oP '"final_model": "\K[^"]+')
        local should_switch=$(echo "$result" | grep -oP '"should_switch": \K[^,}]+')
        
        echo "[$(date -Iseconds)] 推荐模型：$recommended_model，是否切换：$should_switch" >> "$LOG_FILE"
        
        # 返回配置
        cat << EOF
{
    "session_id": "$session_id",
    "recommended_model": "$recommended_model",
    "should_switch": $should_switch,
    "hook_type": "message",
    "timestamp": "$(date -Iseconds)"
}
EOF
    else
        echo "[$(date -Iseconds)] ❌ Smart Model主控制器不存在" >> "$LOG_FILE"
        echo '{"error": "smart model not found"}'
    fi
}

# OpenClaw文件钩子
# 当OpenClaw处理文件时调用
# 参数：$1 - 文件路径
#       $2 - 当前会话ID（可选）
# 返回：推荐的模型配置
openclaw_file_hook() {
    local file_path="$1"
    local session_id="${2:-default}"
    
    echo "[$(date -Iseconds)] OpenClaw文件钩子触发：session=$session_id" >> "$LOG_FILE"
    echo "[$(date -Iseconds)] 文件：$file_path" >> "$LOG_FILE"
    
    if [ ! -e "$file_path" ]; then
        echo "[$(date -Iseconds)] ❌ 文件不存在：$file_path" >> "$LOG_FILE"
        echo '{"error": "file not found"}'
        return 1
    fi
    
    # 加载Smart Model主控制器
    if [ -f "$SMART_MODEL_DIR/smart-model-v2.sh" ]; then
        source "$SMART_MODEL_DIR/smart-model-v2.sh"
        
        # 获取模型推荐
        local result=$(smart_model_switch "" "$file_path" "main")
        local recommended_model=$(echo "$result" | grep -oP '"final_model": "\K[^"]+')
        local file_type=$(echo "$result" | grep -oP '"file_type": "\K[^"]+')
        
        echo "[$(date -Iseconds)] 文件类型：$file_type → 模型：$recommended_model" >> "$LOG_FILE"
        
        # 返回配置
        cat << EOF
{
    "session_id": "$session_id",
    "file_path": "$file_path",
    "file_type": "$file_type",
    "recommended_model": "$recommended_model",
    "hook_type": "file",
    "timestamp": "$(date -Iseconds)"
}
EOF
    else
        echo "[$(date -Iseconds)] ❌ Smart Model主控制器不存在" >> "$LOG_FILE"
        echo '{"error": "smart model not found"}'
    fi
}

# OpenClaw上下文钩子
# 当OpenClaw检测到上下文变化时调用
# 参数：$1 - 当前上下文使用率
#       $2 - 当前会话ID（可选）
# 返回：推荐的模型配置
openclaw_context_hook() {
    local context_usage="$1"
    local session_id="${2:-default}"
    
    echo "[$(date -Iseconds)] OpenClaw上下文钩子触发：session=$session_id" >> "$LOG_FILE"
    echo "[$(date -Iseconds)] 上下文使用率：$context_usage%" >> "$LOG_FILE"
    
    # 加载Smart Model主控制器
    if [ -f "$SMART_MODEL_DIR/smart-model-v2.sh" ]; then
        source "$SMART_MODEL_DIR/smart-model-v2.sh"
        
        # 检查上下文监控
        local level=$(check_warning_level "$context_usage")
        
        # 根据上下文级别推荐模型
        local recommended_model="main"
        local should_switch=false
        
        if [ "$level" = "critical" ]; then
            recommended_model="flash"
            should_switch=true
            echo "[$(date -Iseconds)] ⚠️  上下文严重，切换到flash模型" >> "$LOG_FILE"
        elif [ "$level" = "heavy" ]; then
            recommended_model="flash"
            should_switch=true
            echo "[$(date -Iseconds)] ⚠️  上下文较重，建议切换到flash模型" >> "$LOG_FILE"
        fi
        
        # 返回配置
        cat << EOF
{
    "session_id": "$session_id",
    "context_usage": $context_usage,
    "context_level": "$level",
    "recommended_model": "$recommended_model",
    "should_switch": $should_switch,
    "hook_type": "context",
    "timestamp": "$(date -Iseconds)"
}
EOF
    else
        echo "[$(date -Iseconds)] ❌ Smart Model主控制器不存在" >> "$LOG_FILE"
        echo '{"error": "smart model not found"}'
    fi
}

# ============================================
# OpenClaw集成API
# ============================================

# 初始化OpenClaw集成
# 参数：$1 - 配置文件路径（可选）
init_openclaw_integration() {
    local config_file="${1:-$SCRIPT_DIR/openclaw_config.json}"
    
    echo "[$(date -Iseconds)] 初始化OpenClaw集成..." >> "$LOG_FILE"
    
    # 检查依赖
    if [ ! -f "$SMART_MODEL_DIR/smart-model-v2.sh" ]; then
        echo "[$(date -Iseconds)] ❌ 依赖检查失败：Smart Model主控制器不存在" >> "$LOG_FILE"
        return 1
    fi
    
    # 创建配置文件（如果不存在）
    if [ ! -f "$config_file" ]; then
        cat > "$config_file" << EOF
{
    "version": "2.1.0",
    "hooks": {
        "message": true,
        "file": true,
        "context": true
    },
    "auto_switch": true,
    "cache_enabled": true,
    "log_level": "info"
}
EOF
        echo "[$(date -Iseconds)] ✅ 配置文件已创建：$config_file" >> "$LOG_FILE"
    fi
    
    echo "[$(date -Iseconds)] ✅ OpenClaw集成初始化完成" >> "$LOG_FILE"
    return 0
}

# 获取集成状态
get_integration_status() {
    local config_file="${1:-$SCRIPT_DIR/openclaw_config.json}"
    
    if [ -f "$config_file" ]; then
        cat "$config_file"
    else
        echo '{"error": "config not found"}'
    fi
}

# ============================================
# 主入口
# ============================================

case "${1:-}" in
    --message|-m)
        openclaw_message_hook "$2" "${3:-}" "${4:-default}"
        ;;
    --file|-f)
        openclaw_file_hook "$2" "${3:-default}"
        ;;
    --context|-c)
        openclaw_context_hook "$2" "${3:-default}"
        ;;
    --init|-i)
        init_openclaw_integration "${2:-}"
        ;;
    --status|-s)
        get_integration_status "${2:-}"
        ;;
    --test|-t)
        echo "=== OpenClaw集成测试 ==="
        echo ""
        
        echo "测试1：消息钩子"
        openclaw_message_hook "帮我写一个Python函数" "" "test_session"
        echo ""
        
        echo "测试2：文件钩子"
        openclaw_file_hook "/root/.openclaw/workspace/skills/smart-model/README.md" "test_session"
        echo ""
        
        echo "测试3：上下文钩子"
        openclaw_context_hook "85" "test_session"
        echo ""
        
        echo "测试4：集成状态"
        get_integration_status
        echo ""
        
        echo "=== 测试完成 ==="
        ;;
    *)
        echo "用法："
        echo "  $0 --message \"消息\" [文件] [会话ID]  - 消息钩子"
        echo "  $0 --file 文件路径 [会话ID]           - 文件钩子"
        echo "  $0 --context 使用率 [会话ID]          - 上下文钩子"
        echo "  $0 --init [配置文件]                  - 初始化集成"
        echo "  $0 --status [配置文件]                - 集成状态"
        echo "  $0 --test                             - 运行测试"
        ;;
esac
