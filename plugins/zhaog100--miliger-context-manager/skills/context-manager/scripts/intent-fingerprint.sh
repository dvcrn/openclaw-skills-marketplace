#!/bin/bash
# 意图指纹识别器（v1.0）
# 创建时间：2026-03-07 16:12
# 功能：快速识别用户意图，决定是否加载历史上下文
# 参考：Moltbook - Tiered Context Bucketing策略

# 配置
LOG_FILE="$HOME/.openclaw/workspace/logs/intent-fingerprint.log"
INTENT_CACHE="/tmp/intent-fingerprint-cache"
WARM_LAYER_DB="/tmp/warm-layer-index"
INTENT_KEYWORDS="/root/.openclaw/workspace/config/intent-keywords.txt"

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$(dirname "$INTENT_CACHE")"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# ============================================
# 意图关键词库
# ============================================

# 预定义意图类别
declare -A INTENT_CATEGORIES=(
    ["context"]="记忆 记得 之前 上次 历史 回忆"
    ["task"]="任务 待办 做什么 完成 进度"
    ["knowledge"]="学习 知道 了解 怎么 如何"
    ["system"]="状态 检查 配置 设置 更新"
    ["creative"]="写 创建 生成 设计 想法"
    ["analysis"]="分析 比较 评估 统计 报告"
)

# ============================================
# 意图提取
# ============================================

extract_intent() {
    local message="$1"
    local intent_score=0
    local detected_intents=()
    
    log "🔍 分析消息：${message:0:50}..."
    
    # 提取关键词（3个字母以上的英文单词 + 中文词）
    local keywords=$(echo "$message" | grep -oE '[a-zA-Z]{3,}|[^\x00-\xff]{2,4}' | head -5)
    log "📋 提取关键词：$keywords"
    
    # 匹配意图类别
    for category in "${!INTENT_CATEGORIES[@]}"; do
        local category_keywords="${INTENT_CATEGORIES[$category]}"
        local match_count=0
        
        for keyword in $keywords; do
            if echo "$category_keywords" | grep -qi "$keyword"; then
                ((match_count++))
            fi
        done
        
        # 如果匹配2个以上关键词，认为属于该意图
        if [ $match_count -ge 2 ]; then
            detected_intents+=("$category")
            log "✅ 检测到意图：$category (匹配${match_count}个关键词)"
        fi
    done
    
    # 返回检测到的意图
    echo "${detected_intents[@]}"
}

# ============================================
# Warm层加载决策
# ============================================

should_load_warm() {
    local intents="$1"
    
    log "🤔 判断是否需要加载Warm层..."
    
    # 高优先级意图（需要历史上下文）
    local high_priority="context task knowledge"
    
    for intent in $intents; do
        if echo "$high_priority" | grep -q "$intent"; then
            log "✅ 高优先级意图：$intent（需要加载Warm层）"
            return 0
        fi
    done
    
    log "⏭️ 低优先级意图（无需加载Warm层）"
    return 1
}

# ============================================
# Warm层检索
# ============================================

search_warm_layer() {
    local intents="$1"
    
    log "🔍 检索Warm层..."
    
    # 使用QMD检索相关内容
    if command -v qmd &> /dev/null; then
        for intent in $intents; do
            log "📚 检索意图：$intent"
            qmd search "$intent" -c memory -n 2 2>/dev/null | head -10 >> "$LOG_FILE"
        done
    fi
}

# ============================================
# 缓存管理
# ============================================

cache_intent() {
    local message="$1"
    local intents="$2"
    
    # 缓存意图指纹（1小时有效）
    local cache_key=$(echo "$message" | md5sum | awk '{print $1}')
    local cache_file="$INTENT_CACHE/$cache_key"
    
    echo "$(date '+%s'):$intents" > "$cache_file"
    log "💾 缓存意图指纹：$cache_key"
}

check_cached_intent() {
    local message="$1"
    local cache_key=$(echo "$message" | md5sum | awk '{print $1}')
    local cache_file="$INTENT_CACHE/$cache_key"
    
    if [ -f "$cache_file" ]; then
        local cached=$(cat "$cache_file")
        local timestamp=$(echo "$cached" | cut -d: -f1)
        local now=$(date '+%s')
        local age=$((now - timestamp))
        
        # 缓存1小时有效
        if [ $age -lt 3600 ]; then
            local intents=$(echo "$cached" | cut -d: -f2-)
            log "✅ 命中缓存：$intents（${age}秒前）"
            echo "$intents"
            return 0
        fi
    fi
    
    return 1
}

# ============================================
# 主函数
# ============================================

main() {
    log "================================"
    log "🚀 意图指纹识别启动（v1.0）"
    log "================================"
    
    # 获取最近消息（模拟，实际应从OpenClaw日志提取）
    local last_message="${1:-检查系统状态}"  # 默认测试消息
    
    log "📨 分析消息：$last_message"
    
    # 检查缓存
    local cached_intent=$(check_cached_intent "$last_message")
    if [ $? -eq 0 ]; then
        intents="$cached_intent"
    else
        # 提取意图
        intents=$(extract_intent "$last_message")
        
        # 缓存意图
        cache_intent "$last_message" "$intents"
    fi
    
    # 判断是否加载Warm层
    if [ -n "$intents" ]; then
        if should_load_warm "$intents"; then
            search_warm_layer "$intents"
        fi
    else
        log "ℹ️ 未检测到明确意图"
    fi
    
    log "✅ 意图指纹识别完成"
    log "================================"
}

# 执行（支持参数传递）
main "$@"
