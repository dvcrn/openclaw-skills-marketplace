#!/bin/bash
# memu-engine 集成脚本 v1.0
# 功能：从 session-memory 分片提取结构化记忆
# 创建时间：2026-03-09 19:25
# 作者：米粒儿

WORKSPACE="/root/.openclaw/workspace"
AGENT_NAME="${AGENT_NAME:-main}"
MEMORY_DIR="$WORKSPACE/memory/agents/$AGENT_NAME"
MEMU_DB="$MEMORY_DIR/memu.db"
LOG_FILE="$WORKSPACE/logs/memu-integration.log"

# 确保目录存在
mkdir -p "$MEMORY_DIR" "$(dirname "$LOG_FILE")"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$AGENT_NAME] $1" >> "$LOG_FILE"
}

log "================================"
log "🔄 memu-engine 集成脚本启动（代理：$AGENT_NAME）"
log "================================"

# 从分片提取结构化记忆
extract_structured_memory() {
    local part_file="$1"
    
    if [ ! -f "$part_file" ]; then
        log "⚠️ 分片文件不存在：$part_file"
        return 1
    fi
    
    log "📊 从分片提取结构化记忆：$part_file"
    
    # 检查 Python 环境
    if ! command -v python3 &> /dev/null; then
        log "❌ Python3 未安装"
        return 1
    fi
    
    # 调用 Python 提取器（如果存在）
    local extractor="$WORKSPACE/skills/session-memory-enhanced/python/extractor.py"
    
    if [ -f "$extractor" ]; then
        python3 "$extractor" \
            --input "$part_file" \
            --output "$MEMU_DB" \
            --agent "$AGENT_NAME" 2>&1 | tee -a "$LOG_FILE"
        
        if [ ${PIPESTATUS[0]} -eq 0 ]; then
            log "✅ 结构化记忆提取完成"
            return 0
        else
            log "❌ 结构化记忆提取失败"
            return 1
        fi
    else
        log "⚠️ Python 提取器不存在，跳过结构化提取"
        log "💡 提示：安装完整版以启用结构化提取功能"
        return 0
    fi
}

# 生成向量嵌入
generate_embeddings() {
    local part_file="$1"
    
    log "🔍 生成向量嵌入：$part_file"
    
    # 检查环境变量
    if [ -z "$OPENAI_API_KEY" ]; then
        log "⚠️ OPENAI_API_KEY 未设置，跳过向量嵌入"
        return 0
    fi
    
    # 调用 Python 嵌入器（如果存在）
    local embedder="$WORKSPACE/skills/session-memory-enhanced/python/embedder.py"
    
    if [ -f "$embedder" ]; then
        python3 "$embedder" \
            --input "$part_file" \
            --db "$MEMU_DB" \
            --agent "$AGENT_NAME" 2>&1 | tee -a "$LOG_FILE"
        
        if [ ${PIPESTATUS[0]} -eq 0 ]; then
            log "✅ 向量嵌入生成完成"
            return 0
        else
            log "❌ 向量嵌入生成失败"
            return 1
        fi
    else
        log "⚠️ Python 嵌入器不存在，跳过向量嵌入"
        return 0
    fi
}

# 检查 memu-engine 是否可用
check_memu_available() {
    # 检查 Python 环境
    if ! command -v python3 &> /dev/null; then
        return 1
    fi
    
    # 检查 memu 模块（如果需要）
    # python3 -c "import memu" 2>/dev/null || return 1
    
    # 检查配置文件
    local config="$WORKSPACE/skills/session-memory-enhanced/config/integration.json"
    if [ -f "$config" ]; then
        local enabled=$(jq -r '.engines.memu_engine.enabled' "$config" 2>/dev/null)
        [ "$enabled" = "true" ] || return 1
    else
        return 1
    fi
    
    return 0
}

# 主流程
main() {
    local action="$1"
    shift
    
    case "$action" in
        extract)
            extract_structured_memory "$@"
            ;;
        embed)
            generate_embeddings "$@"
            ;;
        check)
            if check_memu_available; then
                log "✅ memu-engine 可用"
                exit 0
            else
                log "❌ memu-engine 不可用"
                exit 1
            fi
            ;;
        *)
            log "❌ 未知操作：$action"
            log "用法：$0 {extract|embed|check} [参数]"
            exit 1
            ;;
    esac
}

# 执行
main "$@"
