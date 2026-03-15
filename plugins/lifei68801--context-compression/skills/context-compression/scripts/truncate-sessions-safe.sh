#!/bin/bash
# Session Window Truncation (Token-based) - v6
# Supports multiple strategies: token-only, time-decay
# Enhanced with fact extraction and priority-based preservation
# This script runs OUTSIDE of OpenClaw agent context

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
CONFIG_FILE="$WORKSPACE/.context-compression-config.json"
SESSIONS_DIR="${SESSIONS_DIR:-$HOME/.openclaw/agents/main/sessions}"
LOG_FILE="${LOG_FILE:-$HOME/.openclaw/logs/truncation.log}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default values
MAX_TOKENS=40000
MAX_LINE_CHARS=4000
SKIP_ACTIVE=true
TOKENS_PER_CHAR=2  # Conservative estimate: 1 token ≈ 2 chars (Chinese-heavy content)
STRATEGY="time-decay"  # "token-only" or "time-decay"
ENABLE_FACT_EXTRACTION=true  # P0 optimization: extract facts before truncation
ENABLE_PRIORITY_PRESERVATION=true  # P0 optimization: preserve high-priority content

# Load configuration from JSON file if exists
if [ -f "$CONFIG_FILE" ]; then
    # Use Python or jq if available, otherwise fall back to grep
    if command -v jq &> /dev/null; then
        MAX_TOKENS=$(jq -r '.maxTokens // empty' "$CONFIG_FILE" 2>/dev/null || echo "$MAX_TOKENS")
        SKIP_ACTIVE=$(jq -r '.skipActive // empty' "$CONFIG_FILE" 2>/dev/null || echo "$SKIP_ACTIVE")
        STRATEGY=$(jq -r '.strategy // empty' "$CONFIG_FILE" 2>/dev/null || echo "$STRATEGY")
    else
        # Fallback: use sed for simple JSON parsing
        config_max_tokens=$(sed -n 's/.*"maxTokens"[[:space:]]*:[[:space:]]*\([0-9]*\).*/\1/p' "$CONFIG_FILE" 2>/dev/null)
        config_skip_active=$(sed -n 's/.*"skipActive"[[:space:]]*:[[:space:]]*\([a-z]*\).*/\1/p' "$CONFIG_FILE" 2>/dev/null)
        config_strategy=$(sed -n 's/.*"strategy"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$CONFIG_FILE" 2>/dev/null)
        
        [ -n "$config_max_tokens" ] && MAX_TOKENS="$config_max_tokens"
        [ -n "$config_skip_active" ] && SKIP_ACTIVE="$config_skip_active"
        [ -n "$config_strategy" ] && STRATEGY="$config_strategy"
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
    
    local extract_script="$SCRIPT_DIR/extract-facts.sh"
    [ ! -x "$extract_script" ] && return 0
    
    # Extract the portion that will be truncated
    local content_to_truncate=$(head -n $((end_line - start_line)) "$file" 2>/dev/null | head -n $((start_line)))
    
    if [ -n "$content_to_truncate" ]; then
        # Call extract-facts.sh
        echo "$content_to_truncate" | "$extract_script" "$file" 2>/dev/null
        return $?
    fi
}

# ===== P0 Optimization: Priority-Based Preservation =====
# Score content and identify high-priority lines
score_line_priority() {
    local line=$1
    local score=50
    
    # High priority keywords
    [[ "$line" =~ (用户偏好|喜欢|讨厌|偏好|习惯|风格) ]] && score=$((score + 40))
    [[ "$line" =~ (重要|关键|记住|别忘|必须|一定要) ]] && score=$((score + 45))
    [[ "$line" =~ (决定|确定|选择|方案|定下|决策) ]] && score=$((score + 35))
    [[ "$line" =~ (API|Token|key|secret|密钥|配置|endpoint|密码) ]] && score=$((score + 30))
    [[ "$line" =~ (任务|TODO|待办|进度|完成|进行中) ]] && score=$((score + 25))
    [[ "$line" =~ (明天|下周|周[一二三四五六日]|[0-9]+月[0-9]+日|截止) ]] && score=$((score + 20))
    
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

log "=== Session Window Truncation (v6 - Strategy: $STRATEGY) ==="
log "Config: $CONFIG_FILE"
log "Max tokens: $MAX_TOKENS (~$((MAX_TOKENS * TOKENS_PER_CHAR)) chars)"
log "Skip active: $SKIP_ACTIVE"
log "Strategy: $STRATEGY"
log "Fact extraction: $ENABLE_FACT_EXTRACTION"
log "Priority preservation: $ENABLE_PRIORITY_PRESERVATION"

truncated_count=0
trimmed_count=0
skipped_count=0
error_count=0

for f in "$SESSIONS_DIR"/*.jsonl; do
    [ -e "$f" ] || continue
    filename=$(basename "$f")
    
    if [ -f "${f}.lock" ] && [ "$SKIP_ACTIVE" = "true" ]; then
        log "⏭️  Skip active: $filename"
        ((skipped_count++))
        continue
    fi
    
    [[ "$f" == *.deleted.* ]] && continue
    
    # Calculate current token count
    total_chars=$(count_chars "$f")
    total_tokens=$(estimate_tokens "$total_chars")
    
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
        if [ "$STRATEGY" = "time-decay" ]; then
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
