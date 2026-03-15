#!/bin/bash
# AI 摘要系统 v1.0
# 功能：从对话中提取关键信息，自动生成摘要
# 借鉴：memu-engine 的提取链路
# 创建时间：2026-03-07 22:09
# 作者：米粒儿

WORKSPACE="/root/.openclaw/workspace"
AGENT_NAME="${AGENT_NAME:-main}"
MEMORY_DIR="$WORKSPACE/memory/agents/$AGENT_NAME"
LOG_FILE="$WORKSPACE/logs/ai-summarizer.log"
SUMMARY_FILE="$MEMORY_DIR/.summary.json"

# 确保目录存在
mkdir -p "$MEMORY_DIR" "$(dirname "$LOG_FILE")"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$AGENT_NAME] $1" >> "$LOG_FILE"
}

log "================================"
log "🤖 AI 摘要系统 v1.0 启动（代理：$AGENT_NAME）"
log "================================"

# 1. 提取关键信息
extract_insights() {
    log "📊 提取关键信息..."

    # 检查是否有固化的分片
    local part_files=$(ls "$MEMORY_DIR"/part*.json 2>/dev/null | wc -l)

    if [ "$part_files" -eq 0 ]; then
        log "ℹ️ 没有固化分片，无需提取"
        return 0
    fi

    log "📝 找到 $part_files 个固化分片，开始提取..."

    # 提取最近3个分片的关键信息
    local recent_parts=$(ls -t "$MEMORY_DIR"/part*.json 2>/dev/null | head -3)

    # 初始化摘要结构
    cat > "$SUMMARY_FILE" << 'EOF'
{
  "timestamp": "",
  "agent": "",
  "insights": {
    "profile": [],
    "events": [],
    "knowledge": [],
    "decisions": [],
    "lessons": []
  },
  "keywords": [],
  "importance": "medium"
}
EOF

    # 更新时间戳和代理名
    jq --arg time "$(date -Iseconds)" --arg agent "$AGENT_NAME" \
        '.timestamp = $time | .agent = $agent' "$SUMMARY_FILE" > "${SUMMARY_FILE}.tmp"
    mv "${SUMMARY_FILE}.tmp" "$SUMMARY_FILE"

    log "✅ 摘要结构初始化完成"
}

# 2. 简单关键词提取（基于频率）
extract_keywords() {
    log "🔍 提取关键词..."

    if [ ! -f "$SUMMARY_FILE" ]; then
        log "⚠️ 摘要文件不存在"
        return 1
    fi

    # 检查是否有分片文件
    local has_parts=$(ls "$MEMORY_DIR"/part*.json 2>/dev/null | wc -l)
    if [ "$has_parts" -eq 0 ]; then
        log "ℹ️ 没有分片文件，跳过关键词提取"
        return 0
    fi

    # 提取关键词（简单版：提取中文词汇）
    local keywords=$(cat "$MEMORY_DIR"/part*.json 2>/dev/null | \
        jq -r '.messages[].content' 2>/dev/null | \
        grep -oP '[\x{4e00}-\x{9fa5}]{2,10}' | \
        sort | uniq -c | sort -rn | head -10 | \
        awk '{print $2}' | tr '\n' ',' | sed 's/,$//')

    if [ -n "$keywords" ]; then
        jq --arg kw "$keywords" '.keywords = ($kw | split(","))' "$SUMMARY_FILE" > "${SUMMARY_FILE}.tmp"
        mv "${SUMMARY_FILE}.tmp" "$SUMMARY_FILE"
        log "✅ 关键词提取完成：$keywords"
    else
        log "ℹ️ 未提取到关键词"
    fi
}

# 3. 评估重要性
assess_importance() {
    log "📊 评估重要性..."

    if [ ! -f "$SUMMARY_FILE" ]; then
        return 1
    fi

    # 检查关键词数量
    local keyword_count=$(jq '.keywords | length' "$SUMMARY_FILE" 2>/dev/null || echo "0")

    local importance="low"
    if [ "$keyword_count" -ge 8 ]; then
        importance="high"
    elif [ "$keyword_count" -ge 5 ]; then
        importance="medium"
    fi

    jq --arg imp "$importance" '.importance = $imp' "$SUMMARY_FILE" > "${SUMMARY_FILE}.tmp"
    mv "${SUMMARY_FILE}.tmp" "$SUMMARY_FILE"

    log "✅ 重要性评估完成：$importance"
}

# 4. 生成精简摘要
generate_summary() {
    log "📝 生成精简摘要..."

    if [ ! -f "$SUMMARY_FILE" ]; then
        return 1
    fi

    # 读取摘要
    local timestamp=$(jq -r '.timestamp' "$SUMMARY_FILE")
    local importance=$(jq -r '.importance' "$SUMMARY_FILE")
    local keywords=$(jq -r '.keywords | join(", ")' "$SUMMARY_FILE")

    # 生成摘要文件
    local summary_md="$MEMORY_DIR/SUMMARY.md"

    cat > "$summary_md" << EOF
# 代理记忆摘要（$AGENT_NAME）

**生成时间**：$timestamp
**重要性**：$importance
**关键词**：$keywords

## 📊 最近活动

- 固化分片：$(ls "$MEMORY_DIR"/part*.json 2>/dev/null | wc -l) 个
- 最后更新：$(date '+%Y-%m-%d %H:%M:%S')

## 💡 关键洞察

（待 AI 提取）

---

**说明**：这是自动生成的摘要，仅供参考。
完整记忆请查看 partNNN.json 文件。
EOF

    log "✅ 精简摘要生成完成：$summary_md"
}

# 主流程
main() {
    # 1. 提取关键信息
    extract_insights

    # 2. 提取关键词
    extract_keywords

    # 3. 评估重要性
    assess_importance

    # 4. 生成精简摘要
    generate_summary

    log "✅ AI 摘要系统 v1.0 完成（代理：$AGENT_NAME）"
    log "================================"
}

# 执行
main
