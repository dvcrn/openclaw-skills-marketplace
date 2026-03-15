#!/bin/bash
# Session Window Truncation (Token-based) - v9
# Supports multiple strategies: token-only, time-decay, priority-first
# Enhanced with fact extraction and priority-based preservation
# v7: Added preserveUserMessages option to always keep user messages
# v8: Fixed priority-first strategy to call fact extraction before truncating
# v9: Extract facts from active sessions too (even when skipActive=true)
# v8: Fixed priority-first strategy to call fact extraction before truncating
# This script runs OUTSIDE of OpenClaw agent context

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
CONFIG_FILE="$WORKSPACE/.context-compression-config.json"
SESSIONS_DIR="${SESSIONS_DIR:-$HOME/.openclaw/agents/main/sessions}"
LOG_FILE="${LOG_FILE:-$HOME/.openclaw/logs/truncation.log}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default values
MAX_TOKENS=60000
MAX_LINE_CHARS=4000
MAX_HISTORY_LINES=200
SKIP_ACTIVE=true
TOKENS_PER_CHAR=2  # Conservative estimate: 1 token ≈ 2 chars (Chinese-heavy content)
STRATEGY="priority-first"  # "token-only", "time-decay", or "priority-first"
ENABLE_FACT_EXTRACTION=true  # P0 optimization: extract facts before truncation
ENABLE_PRIORITY_PRESERVATION=true  # P0 optimization: preserve high-priority content
PRESERVE_USER_MESSAGES=true  # v7: Always preserve user messages

# Default priority keywords (can be overridden by config)
# v8: Bilingual support for global users (case-insensitive via extended patterns)
# Note: bash regex is case-sensitive, so include common case variants
PRIORITY_KEYWORDS="重要|决定|记住|别忘了|TODO|待办|偏好|我喜欢|我讨厌|千万|务必|关键|明天|下周|约会|会议|截止|同事|老板|客户|朋友|important|Important|IMPORTANT|remember|Remember|REMEMBER|must|MUST|deadline|Deadline|DEADLINE|decision|Decision|DECISION|prefer|Prefer|critical|Critical|CRITICAL|urgent|Urgent|URGENT|note|Note|NOTE"

# Load configuration from JSON file if exists
if [ -f "$CONFIG_FILE" ]; then
    # Use Python or jq if available, otherwise fall back to grep
    if command -v jq &> /dev/null; then
        MAX_TOKENS=$(jq -r '.maxTokens // empty' "$CONFIG_FILE" 2>/dev/null || echo "$MAX_TOKENS")
        SKIP_ACTIVE=$(jq -r '.skipActive // empty' "$CONFIG_FILE" 2>/dev/null || echo "$SKIP_ACTIVE")
        STRATEGY=$(jq -r '.strategy // empty' "$CONFIG_FILE" 2>/dev/null || echo "$STRATEGY")
        PRESERVE_USER_MESSAGES=$(jq -r '.preserveUserMessages // empty' "$CONFIG_FILE" 2>/dev/null || echo "$PRESERVE_USER_MESSAGES")
        MAX_HISTORY_LINES=$(jq -r '.maxHistoryLines // empty' "$CONFIG_FILE" 2>/dev/null || echo "$MAX_HISTORY_LINES")
        # v8: Load priority keywords from config
        CONFIG_KEYWORDS=$(jq -r '.priorityKeywords | join("|") // empty' "$CONFIG_FILE" 2>/dev/null)
        [ -n "$CONFIG_KEYWORDS" ] && PRIORITY_KEYWORDS="$CONFIG_KEYWORDS"
    else
        # Fallback: use sed for simple JSON parsing
        config_max_tokens=$(sed -n 's/.*"maxTokens"[[:space:]]*:[[:space:]]*\([0-9]*\).*/\1/p' "$CONFIG_FILE" 2>/dev/null)
        config_skip_active=$(sed -n 's/.*"skipActive"[[:space:]]*:[[:space:]]*\([a-z]*\).*/\1/p' "$CONFIG_FILE" 2>/dev/null)
        config_strategy=$(sed -n 's/.*"strategy"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$CONFIG_FILE" 2>/dev/null)
        config_preserve=$(sed -n 's/.*"preserveUserMessages"[[:space:]]*:[[:space:]]*\([a-z]*\).*/\1/p' "$CONFIG_FILE" 2>/dev/null)
        config_max_lines=$(sed -n 's/.*"maxHistoryLines"[[:space:]]*:[[:space:]]*\([0-9]*\).*/\1/p' "$CONFIG_FILE" 2>/dev/null)
        
        [ -n "$config_max_tokens" ] && MAX_TOKENS="$config_max_tokens"
        [ -n "$config_skip_active" ] && SKIP_ACTIVE="$config_skip_active"
        [ -n "$config_strategy" ] && STRATEGY="$config_strategy"
        [ -n "$config_preserve" ] && PRESERVE_USER_MESSAGES="$config_preserve"
        [ -n "$config_max_lines" ] && MAX_HISTORY_LINES="$config_max_lines"
    fi
fi

# Override with environment variables
[ -n "${MAX_TOKENS:-}" ] && MAX_TOKENS="$MAX_TOKENS"
[ -n "${SKIP_ACTIVE:-}" ] && SKIP_ACTIVE="$SKIP_ACTIVE"
[ -n "${STRATEGY:-}" ] && STRATEGY="$STRATEGY"

mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# ===== P0 Optimization: Fact Extraction =====
# Extract high-value facts from content before it gets truncated
extract_facts_from_content() {
    local file=$1
    local start_line=$2
    local end_line=$3
    
    [ "$ENABLE_FACT_EXTRACTION" != "true" ] && return 0
    
    # 优先使用增强版提取脚本（使用 AI 提取）
    local extract_script="$SCRIPT_DIR/extract-facts-enhanced.sh"
    [ ! -x "$extract_script" ] && extract_script="$SCRIPT_DIR/extract-facts.sh"
    [ ! -x "$extract_script" ] && return 0
    
    # Extract the portion that will be truncated (lines from start_line to end_line)
    local content_to_truncate
    if [ "$start_line" -eq 1 ]; then
        content_to_truncate=$(head -n "$end_line" "$file" 2>/dev/null)
    else
        content_to_truncate=$(sed -n "${start_line},${end_line}p" "$file" 2>/dev/null)
    fi
    
    if [ -n "$content_to_truncate" ]; then
        log "  🤖 Calling fact extraction agent..."
        # Call extract-facts script via stdin
        echo "$content_to_truncate" | "$extract_script" "$file" 2>&1 | while read -r line; do
            log "    $line"
        done
        return 0
    fi
}

# ===== P0 Optimization: Priority-Based Preservation =====
# Score content and identify high-priority lines
# v8: Use configurable priority keywords
score_line_priority() {
    local line=$1
    local score=50
    
    # High priority keywords from config (v8: dynamic)
    # Pattern: 重要|决定|记住|... etc
    if [ -n "$PRIORITY_KEYWORDS" ]; then
        [[ "$line" =~ ($PRIORITY_KEYWORDS) ]] && score=$((score + 40))
    fi
    
    # Additional high priority patterns (always checked)
    [[ "$line" =~ (用户偏好|喜欢|讨厌|偏好|习惯|风格) ]] && score=$((score + 40))
    [[ "$line" =~ (关键|必须|一定要) ]] && score=$((score + 45))
    [[ "$line" =~ (确定|选择|方案|定下|决策) ]] && score=$((score + 35))
    [[ "$line" =~ (任务|进度|完成|进行中) ]] && score=$((score + 25))
    [[ "$line" =~ (周[一二三四五六日]|[0-9]+月[0-9]+日) ]] && score=$((score + 20))
    
    # Low priority
    [[ "$line" =~ (哈哈|呵呵|嗯嗯|好的|收到|OK) ]] && score=$((score - 10))
    [[ "$line" =~ (HEARTBEAT|heartbeat|system) ]] && score=$((score - 20))
    
    [ $score -lt 0 ] && score=0
    [ $score -gt 100 ] && score=100
    
    echo $score
}

# Check if a line is high priority (should be preserved or extracted)
is_high_priority() {
    local line=$1
    local threshold=${2:-70}
    local score=$(score_line_priority "$line")
    [ "$score" -ge "$threshold" ]
}

# Estimate token count from character count
# Conservative: 1 token ≈ 3 chars (handles mixed Chinese/English)
estimate_tokens() {
    local char_count=$1
    echo $((char_count / TOKENS_PER_CHAR))
}

# Count total characters in a file
count_chars() {
    local file=$1
    wc -c < "$file" 2>/dev/null || echo 0
}

# Find how many lines from the end fit within token budget
find_truncate_point() {
    local file=$1
    local max_tokens=$2
    local max_chars=$((max_tokens * TOKENS_PER_CHAR))
    
    local total_chars=$(count_chars "$file")
    if [ "$total_chars" -le "$max_chars" ]; then
        echo 0  # No truncation needed
        return
    fi
    
    # Binary search for the right number of lines
    local total_lines=$(wc -l < "$file" 2>/dev/null || echo 0)
    local low=1
    local high=$total_lines
    local result=$total_lines
    
    while [ $low -le $high ]; do
        local mid=$(( (low + high) / 2 ))
        local char_count=$(tail -n $mid "$file" | wc -c 2>/dev/null || echo 0)
        
        if [ "$char_count" -le "$max_chars" ]; then
            result=$mid
            high=$((mid - 1))
        else
            low=$((mid + 1))
        fi
    done
    
    echo $result
}

log "=== Session Window Truncation (v9 - Strategy: $STRATEGY) ==="
log "Config: $CONFIG_FILE"
log "Max tokens: $MAX_TOKENS (~$((MAX_TOKENS * TOKENS_PER_CHAR)) chars)"
log "Skip active: $SKIP_ACTIVE"
log "Strategy: $STRATEGY"
log "Preserve user messages: $PRESERVE_USER_MESSAGES"
log "Max history lines: $MAX_HISTORY_LINES"
log "Fact extraction: $ENABLE_FACT_EXTRACTION"
log "Priority preservation: $ENABLE_PRIORITY_PRESERVATION"

truncated_count=0
trimmed_count=0
skipped_count=0
error_count=0
facts_extracted=0

for f in "$SESSIONS_DIR"/*.jsonl; do
    [ -e "$f" ] || continue
    filename=$(basename "$f")
    
    [[ "$f" == *.deleted.* ]] && continue
    
    # Calculate current token count
    total_chars=$(count_chars "$f")
    total_tokens=$(estimate_tokens "$total_chars")
    
    # v9: Even active sessions need fact extraction if over threshold
    if [ -f "${f}.lock" ] && [ "$SKIP_ACTIVE" = "true" ]; then
        if [ "$total_tokens" -gt "$MAX_TOKENS" ] && [ "$ENABLE_FACT_EXTRACTION" = "true" ]; then
            log "📋 Active session over threshold (~${total_tokens}t), extracting facts..."
            
            # Scan for high-priority content in the session
            lines=$(wc -l < "$f" 2>/dev/null || echo 0)
            high_priority_count=0
            
            while IFS= read -r line; do
                if is_high_priority "$line" 70; then
                    ((high_priority_count++))
                fi
            done < "$f"
            
            if [ "$high_priority_count" -gt 0 ]; then
                log "  💎 Found $high_priority_count high-priority lines, extracting..."
                extract_facts_from_content "$f" 1 "$lines"
                ((facts_extracted++))
            else
                log "  ✅ No high-priority content found"
            fi
        fi
        
        log "⏭️  Skip active: $filename"
        ((skipped_count++))
        continue
    fi
    
    [ "$total_tokens" -le "$MAX_TOKENS" ] && continue
    
    lines=$(wc -l < "$f" 2>/dev/null)
    log "Processing: $filename (~${total_tokens} tokens, ${lines}L)"
    
    # Step 1: Trim oversized lines first
    temp_file="${f}.trim.$$"
    oversized=0
    
    while IFS= read -r line; do
        len=${#line}
        if [ "$len" -gt "$MAX_LINE_CHARS" ]; then
            # Truncate line content
            prefix="${line:0:3000}"
            suffix="${line: -500}"
            echo "${prefix}...[TRUNCATED ${len}b]...${suffix}" >> "$temp_file"
            ((oversized++))
        else
            echo "$line" >> "$temp_file"
        fi
    done < "$f"
    
    if [ "$oversized" -gt 0 ]; then
        mv "$temp_file" "$f"
        log "  Trimmed $oversized oversized lines"
        ((trimmed_count+=oversized))
    else
        rm -f "$temp_file"
    fi
    
    # Step 2: Apply truncation strategy
    total_chars=$(count_chars "$f")
    total_tokens=$(estimate_tokens "$total_chars")
    
    if [ "$total_tokens" -gt "$MAX_TOKENS" ]; then
        if [ "$STRATEGY" = "priority-first" ]; then
            # v8: Priority-first truncation - preserve user messages and high-priority content
            # v8 FIX: Extract facts BEFORE truncating (was missing in v7)
            log "  🎯 Applying priority-first strategy..."
            
            # Create temp files
            temp_file="${f}.priority.$$"
            user_msgs_file="${f}.user.$$"
            
            # Extract user messages (role: "user")
            grep '"role":"user"' "$f" 2>/dev/null > "$user_msgs_file" || true
            user_count=$(wc -l < "$user_msgs_file" 2>/dev/null || echo 0)
            log "  👤 Found $user_count user messages to preserve"
            
            # Calculate how much space user messages take
            user_chars=$(wc -c < "$user_msgs_file" 2>/dev/null || echo 0)
            user_tokens=$(estimate_tokens "$user_chars")
            
            # Remaining budget for other content
            remaining_tokens=$((MAX_TOKENS - user_tokens - 5000))  # 5k buffer
            remaining_chars=$((remaining_tokens * TOKENS_PER_CHAR))
            
            # Get non-user lines (excluding first line which is session metadata)
            tail -n +2 "$f" | grep -v '"role":"user"' > "${temp_file}.other" 2>/dev/null || true
            
            # Keep the most recent non-user lines that fit in remaining budget
            other_lines=$(wc -l < "${temp_file}.other" 2>/dev/null || echo 0)
            keep_other_lines=$((remaining_chars / 5000))  # rough estimate: 5000 chars per line average
            [ "$keep_other_lines" -gt "$other_lines" ] && keep_other_lines=$other_lines
            
            # v8 FIX: Extract facts from content that will be discarded
            if [ "$ENABLE_FACT_EXTRACTION" = "true" ] && [ "$other_lines" -gt "$keep_other_lines" ]; then
                discard_count=$((other_lines - keep_other_lines))
                log "  📋 v8: Scanning $discard_count lines for high-priority content to extract..."
                
                # Get lines that will be discarded
                head -n "$discard_count" "${temp_file}.other" > "${temp_file}.discard" 2>/dev/null || true
                
                high_priority_count=0
                while IFS= read -r line; do
                    if is_high_priority "$line" 70; then
                        ((high_priority_count++))
                    fi
                done < "${temp_file}.discard"
                
                if [ "$high_priority_count" -gt 0 ]; then
                    log "  💎 v8: Found $high_priority_count high-priority lines, extracting facts..."
                    extract_facts_from_content "$f" 1 "$discard_count"
                    facts_extracted=$((facts_extracted + 1))
                else
                    log "  ✅ v8: No high-priority content in discarded portion"
                fi
                
                rm -f "${temp_file}.discard"
            fi
            
            # Build new session file
            # 1. Keep the first line (session metadata)
            head -1 "$f" > "$temp_file"
            
            # 2. Add user messages (they must be preserved)
            cat "$user_msgs_file" >> "$temp_file"
            
            # 3. Add recent non-user lines
            if [ "$keep_other_lines" -gt 0 ]; then
                tail -n "$keep_other_lines" "${temp_file}.other" >> "$temp_file"
            fi
            
            # Calculate new stats
            new_chars=$(wc -c < "$temp_file")
            new_tokens=$(estimate_tokens "$new_chars")
            new_lines=$(wc -l < "$temp_file")
            
            # Only apply if we're actually reducing size
            if [ "$new_tokens" -lt "$total_tokens" ]; then
                if mv "$temp_file" "$f" 2>/dev/null; then
                    log "  ✅ Preserved: $user_count user messages, ~${new_tokens}t total"
                    log "  ✂️ Truncated: ~${total_tokens}t ${lines}L → ~${new_tokens}t ${new_lines}L"
                    ((truncated_count++))
                else
                    rm -f "$temp_file"
                    log "  ❌ Failed to apply priority-first truncation"
                    ((error_count++))
                fi
            else
                rm -f "$temp_file"
                log "  ⚠️ Priority-first didn't reduce size"
            fi
            
            # Cleanup
            rm -f "$user_msgs_file" "${temp_file}.other"
        elif [ "$STRATEGY" = "time-decay" ]; then
            # Use time-decay truncation
            log "  🕐 Applying time-decay strategy..."
            "$SCRIPT_DIR/time-decay-truncate.sh" --file "$f" 2>/dev/null
            ((truncated_count++))
        else
            # Default: token-only truncation with fact extraction
            keep_lines=$(find_truncate_point "$f" "$MAX_TOKENS")
            
            if [ "$keep_lines" -gt 0 ] && [ "$keep_lines" -lt "$lines" ]; then
                # Extract facts BEFORE truncating
                if [ "$ENABLE_FACT_EXTRACTION" = "true" ]; then
                    truncate_end=$((lines - keep_lines))
                    high_priority_count=0
                    
                    log "  📋 Scanning lines 1-$truncate_end for high-priority content..."
                    
                    while IFS= read -r line; do
                        if is_high_priority "$line" 70; then
                            ((high_priority_count++))
                        fi
                    done < <(head -n "$truncate_end" "$f")
                    
                    if [ "$high_priority_count" -gt 0 ]; then
                        log "  💎 Found $high_priority_count high-priority lines to extract"
                        extract_facts_from_content "$f" 1 "$truncate_end"
                    else
                        log "  ✅ No high-priority content in truncated portion"
                    fi
                fi
                
                # Perform truncation
                temp_file="${f}.trunc.$$"
                tail -n "$keep_lines" "$f" > "$temp_file" 2>/dev/null
                
                if mv "$temp_file" "$f" 2>/dev/null; then
                    final_chars=$(count_chars "$f")
                    final_tokens=$(estimate_tokens "$final_chars")
                    final_lines=$(wc -l < "$f")
                    log "  ✂️ Truncated: ~${total_tokens}t ${lines}L → ~${final_tokens}t ${final_lines}L"
                    ((truncated_count++))
                else
                    rm -f "$temp_file"
                    log "  ❌ Failed to truncate"
                    ((error_count++))
                fi
            else
                log "  ⚠️ Cannot truncate further (already at minimum)"
            fi
        fi
    else
        log "  ✅ Size OK after trim: ~${total_tokens}t"
    fi
done

log ""
log "=== Summary ==="
log "Truncated: $truncated_count"
log "Lines trimmed: $trimmed_count"
log "Skipped: $skipped_count"
log "Errors: $error_count"
log "Facts extracted: ${facts_extracted:-0}"
log ""

[ "$error_count" -eq 0 ]
