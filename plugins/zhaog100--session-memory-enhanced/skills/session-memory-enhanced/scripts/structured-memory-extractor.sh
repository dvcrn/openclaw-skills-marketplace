#!/bin/bash
# 结构化记忆提取脚本 v1.0
# 功能：从对话中提取 5 大类别记忆
# 借鉴：memu-engine 的 MemU 引擎思路
# 创建时间：2026-03-07 22:27
# 作者：米粒儿

WORKSPACE="/root/.openclaw/workspace"
AGENT_NAME="${AGENT_NAME:-main}"
MEMORY_DIR="$WORKSPACE/memory/agents/$AGENT_NAME"
LOG_FILE="$WORKSPACE/logs/structured-extractor.log"
OUTPUT_FILE="$MEMORY_DIR/.structured-memory.json"

mkdir -p "$MEMORY_DIR" "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$AGENT_NAME] $1" >> "$LOG_FILE"
}

log "================================"
log "🧠 结构化记忆提取器 v1.0 启动（代理：$AGENT_NAME）"
log "================================"

# 检查是否有固化的分片
part_files=$(ls "$MEMORY_DIR"/part*.json 2>/dev/null | wc -l)

if [ "$part_files" -eq 0 ]; then
    log "ℹ️ 没有固化分片，无需提取"
    exit 0
fi

log "📝 找到 $part_files 个固化分片，开始提取..."

# 初始化结构化记忆
cat > "$OUTPUT_FILE" << 'EOF'
{
  "timestamp": "",
  "agent": "",
  "categories": {
    "profile": {
      "description": "用户画像（偏好、习惯、特征）",
      "items": []
    },
    "events": {
      "description": "重要事件、里程碑",
      "items": []
    },
    "knowledge": {
      "description": "学到的知识、技能",
      "items": []
    },
    "skills": {
      "description": "掌握的技能、能力",
      "items": []
    },
    "behavior_preferences": {
      "description": "决策模式、工作风格",
      "items": []
    }
  },
  "summary": {
    "total_items": 0,
    "importance": "medium"
  }
}
EOF

# 更新时间戳和代理名
jq --arg time "$(date -Iseconds)" --arg agent "$AGENT_NAME" \
    '.timestamp = $time | .agent = $agent' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp"
mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"

# 简化版：基于关键词匹配分类（未来可用 AI 模型）
classify_messages() {
    log "🔍 分类消息..."

    # 读取最近3个分片
    recent_parts=$(ls -t "$MEMORY_DIR"/part*.json 2>/dev/null | head -3)

    for part_file in $recent_parts; do
        # 提取用户消息
        user_messages=$(jq -r '.messages[] | select(.role == "user") | .content' "$part_file" 2>/dev/null)

        # 简单关键词匹配（未来可用 AI 模型）
        while IFS= read -r message; do
            # Profile（画像）：喜欢、偏好、习惯
            if echo "$message" | grep -qE '喜欢|偏好|习惯|常用|推荐|建议'; then
                jq --arg msg "$message" '.categories.profile.items += [$msg]' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp"
                mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
            fi

            # Events（事件）：完成、发布、里程碑
            if echo "$message" | grep -qE '完成|发布|里程碑|首次|成功|发布到'; then
                jq --arg msg "$message" '.categories.events.items += [$msg]' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp"
                mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
            fi

            # Knowledge（知识）：学习、理解、掌握
            if echo "$message" | grep -qE '学习|理解|掌握|知识|技能|实现'; then
                jq --arg msg "$message" '.categories.knowledge.items += [$msg]' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp"
                mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
            fi

            # Skills（技能）：实现、开发、优化
            if echo "$message" | grep -qE '实现|开发|优化|改进|创建'; then
                jq --arg msg "$message" '.categories.skills.items += [$msg]' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp"
                mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
            fi

            # Behavior Preferences（行为偏好）：策略、方案、决策
            if echo "$message" | grep -qE '策略|方案|决策|选择|优先级'; then
                jq --arg msg "$message" '.categories.behavior_preferences.items += [$msg]' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp"
                mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
            fi
        done <<< "$user_messages"
    done

    log "✅ 分类完成"
}

# 统计总数
calculate_summary() {
    log "📊 计算统计..."

    total=$(jq '[.categories[].items | length] | add' "$OUTPUT_FILE")

    # 更新统计
    jq --arg total "$total" '.summary.total_items = ($total | tonumber)' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp"
    mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"

    # 评估重要性
    importance="low"
    if [ "$total" -ge 20 ]; then
        importance="high"
    elif [ "$total" -ge 10 ]; then
        importance="medium"
    fi

    jq --arg imp "$importance" '.summary.importance = $imp' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp"
    mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"

    log "✅ 统计完成：$total 条记录，重要性：$importance"
}

# 生成可读性文档
generate_readme() {
    log "📝 生成可读性文档..."

    readme_file="$MEMORY_DIR/STRUCTURED_MEMORY.md"

    # 读取数据
    timestamp=$(jq -r '.timestamp' "$OUTPUT_FILE")
    total=$(jq -r '.summary.total_items' "$OUTPUT_FILE")
    importance=$(jq -r '.summary.importance' "$OUTPUT_FILE")

    # 生成文档
    cat > "$readme_file" << EOF
# 结构化记忆（$AGENT_NAME）

**生成时间**：$timestamp
**总记录**：$total 条
**重要性**：$importance

---

## 1️⃣ Profile（用户画像）

偏好、习惯、特征

$(jq -r '.categories.profile.items[] | "- \(.)"' "$OUTPUT_FILE" 2>/dev/null || echo "暂无记录")

---

## 2️⃣ Events（重要事件）

里程碑、成就

$(jq -r '.categories.events.items[] | "- \(.)"' "$OUTPUT_FILE" 2>/dev/null || echo "暂无记录")

---

## 3️⃣ Knowledge（知识）

学到的知识、技能

$(jq -r '.categories.knowledge.items[] | "- \(.)"' "$OUTPUT_FILE" 2>/dev/null || echo "暂无记录")

---

## 4️⃣ Skills（技能）

掌握的技能、能力

$(jq -r '.categories.skills.items[] | "- \(.)"' "$OUTPUT_FILE" 2>/dev/null || echo "暂无记录")

---

## 5️⃣ Behavior Preferences（行为偏好）

决策模式、工作风格

$(jq -r '.categories.behavior_preferences.items[] | "- \(.)"' "$OUTPUT_FILE" 2>/dev/null || echo "暂无记录")

---

**说明**：基于关键词匹配自动分类（简化版）
**未来**：使用 AI 模型进行智能分类（v3.5.1）
EOF

    log "✅ 可读性文档生成完成：$readme_file"
}

# 主流程
main() {
    classify_messages
    calculate_summary
    generate_readme

    log "✅ 结构化记忆提取完成（代理：$AGENT_NAME）"
    log "================================"
}

main
