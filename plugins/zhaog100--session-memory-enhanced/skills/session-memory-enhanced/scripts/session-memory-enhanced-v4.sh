#!/bin/bash
# Session-Memory Enhanced v4.0 - 统一增强版
# 融合 session-memory + memu-engine 核心功能
# 创建时间：2026-03-09 19:30
# 作者：米粒儿

WORKSPACE="/root/.openclaw/workspace"
AGENT_NAME="${AGENT_NAME:-main}"
MEMORY_DIR="$WORKSPACE/memory/agents/$AGENT_NAME"
SHARED_DIR="$WORKSPACE/memory/shared"
LOG_FILE="$WORKSPACE/logs/session-memory-enhanced.log"
TAIL_FILE="$MEMORY_DIR/.tail.tmp.json"

# Python 组件路径（吸收 memu-engine 优势）
PYTHON_DIR="$WORKSPACE/skills/session-memory-enhanced/python"
VENV_DIR="$WORKSPACE/skills/session-memory-enhanced/venv"
EXTRACTOR="$PYTHON_DIR/extractor.py"
EMBEDDER="$PYTHON_DIR/embedder.py"
SEARCHER="$PYTHON_DIR/searcher.py"
REVIEWER="$PYTHON_DIR/reviewer.py"

# 配置文件
CONFIG_FILE="$WORKSPACE/skills/session-memory-enhanced/config/unified.json"
AGENT_CONFIG="$WORKSPACE/config/agents.json"

# 默认配置
FLUSH_IDLE_SECONDS=1800
MAX_MESSAGES_PER_PART=60
ENABLE_STRUCTURED_EXTRACTION=false
ENABLE_VECTOR_SEARCH=false
OPENAI_API_KEY=""

# 确保目录存在
mkdir -p "$MEMORY_DIR" "$SHARED_DIR" "$(dirname "$LOG_FILE")"

# **关键：在脚本开始时激活虚拟环境（官家要求）**
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate" 2>/dev/null && log "✅ 虚拟环境已激活：$VENV_DIR"
fi

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$AGENT_NAME] $1" >> "$LOG_FILE"
}

log "================================"
log "🚀 Session-Memory Enhanced v4.0 启动（统一增强版）"
log "🎯 融合 session-memory + memu-engine 核心功能"
log "================================"

# 加载配置
load_config() {
    # 加载主配置
    if [ -f "$CONFIG_FILE" ]; then
        log "📋 加载主配置：$CONFIG_FILE"
        
        FLUSH_IDLE_SECONDS=$(jq -r '.flushIdleSeconds // 1800' "$CONFIG_FILE")
        MAX_MESSAGES_PER_PART=$(jq -r '.maxMessagesPerPart // 60' "$CONFIG_FILE")
        ENABLE_STRUCTURED_EXTRACTION=$(jq -r '.features.structuredExtraction // false' "$CONFIG_FILE")
        ENABLE_VECTOR_SEARCH=$(jq -r '.features.vectorSearch // false' "$CONFIG_FILE")
    fi
    
    # 加载代理配置
    if [ -f "$AGENT_CONFIG" ]; then
        log "📋 加载代理配置：$AGENT_CONFIG"
        
        AGENT_FLUSH=$(jq -r ".agents.${AGENT_NAME}.flushIdleSeconds // empty" "$AGENT_CONFIG")
        AGENT_MAX=$(jq -r ".agents.${AGENT_NAME}.maxMessagesPerPart // empty" "$AGENT_CONFIG")
        
        [ -n "$AGENT_FLUSH" ] && FLUSH_IDLE_SECONDS="$AGENT_FLUSH"
        [ -n "$AGENT_MAX" ] && MAX_MESSAGES_PER_PART="$AGENT_MAX"
    fi
    
    # 加载 OpenAI API Key（多层fallback）
    # 1. 从 openai.env 文件加载
    if [ -f "$WORKSPACE/config/openai.env" ]; then
        source "$WORKSPACE/config/openai.env" 2>/dev/null
    fi
    
    # 2. 从配置文件读取（可能是占位符）
    local config_key=$(jq -r '.openaiApiKey // empty' "$CONFIG_FILE" 2>/dev/null)
    
    # 3. 如果配置文件是占位符，使用环境变量
    if [[ "$config_key" == *'$'* ]]; then
        # 占位符，使用环境变量（已从 openai.env 加载）
        :
    elif [ -n "$config_key" ]; then
        # 配置文件有实际值
        OPENAI_API_KEY="$config_key"
    fi
    
    log "✅ 配置加载完成"
    log "   - 闲置时间：${FLUSH_IDLE_SECONDS}秒"
    log "   - 消息上限：${MAX_MESSAGES_PER_PART}条"
    log "   - 结构化提取：${ENABLE_STRUCTURED_EXTRACTION}"
    log "   - 向量检索：${ENABLE_VECTOR_SEARCH}"
}

# 检查 Python 环境
check_python_available() {
    # 优先使用虚拟环境
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate" 2>/dev/null
    fi
    
    if ! command -v python3 &> /dev/null; then
        log "⚠️ Python3 未安装"
        return 1
    fi
    
    # 检查依赖
    if [ -f "$PYTHON_DIR/requirements.txt" ]; then
        python3 -c "import openai" 2>/dev/null || {
            log "⚠️ Python 依赖未安装"
            return 1
        }
    fi
    
    return 0
}

# 1. 检查是否需要固化分片
should_flush() {
    [ ! -f "$TAIL_FILE" ] && return 1
    
    local msg_count=$(jq '.messages | length' "$TAIL_FILE" 2>/dev/null || echo "0")
    [ "$msg_count" -ge "$MAX_MESSAGES_PER_PART" ] && return 0
    
    local last_modified=$(stat -c %Y "$TAIL_FILE" 2>/dev/null || echo "0")
    local now=$(date +%s)
    local idle_time=$((now - last_modified))
    [ "$idle_time" -ge "$FLUSH_IDLE_SECONDS" ] && return 0
    
    return 1
}

# 2. 固化分片（不可变 + 去重 - 吸收 memu-engine 去重机制）
flush_tail() {
    if [ ! -f "$TAIL_FILE" ]; then
        log "ℹ️ 无需固化（tail文件不存在）"
        return 0
    fi
    
    # 生成 part 编号
    local part_num=$(ls "$MEMORY_DIR"/part*.json 2>/dev/null | wc -l)
    local part_file="$MEMORY_DIR/part$(printf '%03d' $part_num).json"
    local processed_marker="$part_file.processed"
    
    # 去重检查（吸收 memu-engine 的去重机制）
    if [ -f "$processed_marker" ]; then
        log "⚠️ 已处理过，跳过：$part_file"
        return 0
    fi
    
    # 固化分片
    mv "$TAIL_FILE" "$part_file"
    touch "$processed_marker"
    
    log "✅ 固化分片：$part_file"
    
    # 触发增强功能（吸收 memu-engine 优势）
    enhance_memory "$part_file"
}

# 3. 增强记忆（结构化提取 + 向量嵌入 - 吸收 memu-engine 核心优势）
enhance_memory() {
    local part_file="$1"
    
    log "🔄 增强记忆处理：$part_file"
    
    # A. 结构化提取（吸收 memu-engine 的结构化提取优势）
    if [ "$ENABLE_STRUCTURED_EXTRACTION" = "true" ] && check_python_available; then
        extract_structured_memory "$part_file"
    fi
    
    # B. 向量嵌入（吸收 memu-engine 的向量检索优势）
    if [ "$ENABLE_VECTOR_SEARCH" = "true" ] && [ -n "$OPENAI_API_KEY" ] && check_python_available; then
        generate_embeddings "$part_file"
    fi
    
    # C. AI 摘要（保留 session-memory 优势）
    if [ -f "$WORKSPACE/skills/session-memory-enhanced/scripts/ai-summarizer.sh" ]; then
        bash "$WORKSPACE/skills/session-memory-enhanced/scripts/ai-summarizer.sh"
    fi
    
    log "✅ 记忆增强完成"
}

# 4. 结构化记忆提取（吸收 memu-engine 优势）
extract_structured_memory() {
    local part_file="$1"
    
    log "📊 提取结构化记忆..."
    
    if [ -f "$EXTRACTOR" ]; then
        python3 "$EXTRACTOR" \
            --input "$part_file" \
            --output "$MEMORY_DIR/structured.db" \
            --agent "$AGENT_NAME" \
            --api-key "$OPENAI_API_KEY" 2>&1 | tee -a "$LOG_FILE"
        
        if [ ${PIPESTATUS[0]} -eq 0 ]; then
            log "✅ 结构化提取完成"
        else
            log "❌ 结构化提取失败"
        fi
    else
        log "⚠️ 提取器不存在：$EXTRACTOR"
    fi
}

# 5. 生成向量嵌入（吸收 memu-engine 优势）
generate_embeddings() {
    local part_file="$1"
    
    log "🔍 生成向量嵌入..."
    
    if [ -f "$EMBEDDER" ]; then
        python3 "$EMBEDDER" \
            --input "$part_file" \
            --output "$MEMORY_DIR/vectors.db" \
            --agent "$AGENT_NAME" \
            --api-key "$OPENAI_API_KEY" 2>&1 | tee -a "$LOG_FILE"
        
        if [ ${PIPESTATUS[0]} -eq 0 ]; then
            log "✅ 向量嵌入完成"
        else
            log "❌ 向量嵌入失败"
        fi
    else
        log "⚠️ 嵌入器不存在：$EMBEDDER"
    fi
}

# 6. 回顾当天聊天，查漏补缺（官家要求的智能回顾）
review_and_fill_gaps() {
    log "🔍 回顾当天聊天，查漏补缺..."
    
    local today=$(date '+%Y-%m-%d')
    local today_memory="$WORKSPACE/memory/$today.md"
    local long_term_memory="$WORKSPACE/MEMORY.md"
    local review_report="$WORKSPACE/memory/review-$today.md"
    
    # 检查今天的记忆文件是否存在
    if [ ! -f "$today_memory" ]; then
        log "ℹ️ 今天还没有记忆文件，跳过回顾"
        return 0
    fi
    
    # 统计今天的记忆行数
    local today_lines=$(wc -l < "$today_memory")
    log "📄 今天记忆：$today_lines 行"
    
    # 如果有 Python AI 组件 + API Key，进行智能分析
    if check_python_available && [ -n "$OPENAI_API_KEY" ]; then
        log "🤖 使用 AI 进行智能查漏补缺..."
        
        # 激活虚拟环境（解决子shell环境丢失问题）
        if [ -f "$VENV_DIR/bin/activate" ]; then
            source "$VENV_DIR/bin/activate"
        fi
        
        python3 "$REVIEWER" \
            --today-memory "$today_memory" \
            --long-term-memory "$long_term_memory" \
            --output "$review_report" \
            --api-key "$OPENAI_API_KEY" 2>&1 | tee -a "$LOG_FILE"
        
        if [ ${PIPESTATUS[0]} -eq 0 ]; then
            log "✅ 智能回顾完成"
            
            # 如果有审查报告，显示摘要
            if [ -f "$review_report" ]; then
                local report_lines=$(wc -l < "$review_report")
                log "📊 审查报告：$report_lines 行"
            fi
        else
            log "⚠️ 智能回顾失败，使用基础回顾"
            basic_review "$today_memory"
        fi
    else
        log "ℹ️ 使用基础回顾（无需 AI）"
        basic_review "$today_memory"
    fi
}

# 基础回顾（不使用 AI）
basic_review() {
    local today_memory="$1"
    
    log "📋 基础回顾：检查今天的记忆完整性..."
    
    # 简单检查：文件大小、关键内容
    local today_lines=$(wc -l < "$today_memory")
    local has_events=$(grep -c "事件\|决定\|决策\|教训" "$today_memory" 2>/dev/null || echo "0")
    
    log "📊 今天记忆统计："
    log "   - 总行数：$today_lines"
    log "   - 关键词出现次数：$has_events"
    
    # 如果记忆较少，提醒
    if [ "$today_lines" -lt 20 ]; then
        log "⚠️ 今天记忆较少（<20行），可能遗漏内容"
    fi
    
    log "✅ 基础回顾完成"
}

# 7. 更新 QMD 知识库（保留 session-memory 优势）
update_qmd() {
    log "📚 更新 QMD 知识库..."
    
    if command -v qmd &> /dev/null; then
        qmd update 2>&1 | tee -a "$LOG_FILE"
        log "✅ QMD 更新完成"
    else
        log "⚠️ QMD 未安装，跳过"
    fi
}

# 7. Git 自动提交（保留 session-memory 优势）
git_commit() {
    log "💾 Git 自动提交..."
    
    cd "$WORKSPACE"
    
    # 检查变更
    local changes=$(git status --porcelain 2>/dev/null | wc -l)
    
    if [ "$changes" -gt 0 ]; then
        # 统计变更
        local added=$(git status --porcelain | grep -c "^A " || echo "0")
        local modified=$(git status --porcelain | grep -c "^ M" || echo "0")
        local deleted=$(git status --porcelain | grep -c "^ D" || echo "0")
        
        # 提交
        git add -A
        git commit -m "chore: session-memory自动更新（+$added ~$modified -$deleted）" \
            --author "miliger <miliger@openclaw.ai>" 2>&1 | tee -a "$LOG_FILE"
        
        log "✅ Git 提交完成（+$added ~$modified -$deleted）"
    else
        log "ℹ️ 无变更，跳过提交"
    fi
}

# 8. 统一检索接口（吸收 memu-engine 检索优势 + 保留 QMD 后备）
search() {
    local query="$1"
    
    log "🔍 检索查询：$query"
    
    # 优先使用向量检索（吸收 memu-engine 优势）
    if [ "$ENABLE_VECTOR_SEARCH" = "true" ] && [ -n "$OPENAI_API_KEY" ] && check_python_available; then
        log "📊 使用向量检索..."
        
        if [ -f "$SEARCHER" ]; then
            python3 "$SEARCHER" \
                --query "$query" \
                --db "$MEMORY_DIR/vectors.db" \
                --agent "$AGENT_NAME" \
                --api-key "$OPENAI_API_KEY" 2>&1
            
            if [ $? -eq 0 ]; then
                return 0
            fi
        fi
    fi
    
    # 降级到 QMD 检索（保留 session-memory 优势）
    log "📊 降级到 QMD 检索..."
    
    if command -v qmd &> /dev/null; then
        qmd search "$query" -c memory
    else
        log "❌ 无可用检索方式"
        return 1
    fi
}

# 主流程
main() {
    # 1. 加载配置
    load_config
    
    # 2. 检查是否需要固化
    if should_flush; then
        # 3. 固化分片
        flush_tail
        
        # 4. 回顾当天聊天，查漏补缺（官家要求）
        review_and_fill_gaps
        
        # 5. 更新 QMD
        update_qmd
        
        # 6. Git 提交
        git_commit
    fi
    
    log "✅ Session-Memory Enhanced v4.0 完成"
    log "🎯 已吸收 memu-engine 核心优势"
    log "🔍 已添加查漏补缺功能（官家要求）"
    log "================================"
}

# 执行
main
