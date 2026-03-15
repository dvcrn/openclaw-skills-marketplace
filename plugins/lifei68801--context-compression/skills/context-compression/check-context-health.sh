#!/bin/bash
# Check Context Health
# Reports current context status and recommendations

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
SESSIONS_DIR="$HOME/.openclaw/agents/main/sessions"
MEMORY_DIR="$WORKSPACE/memory"
SUMMARIES_DIR="$MEMORY_DIR/summaries"

echo "=== Context Health Check ==="
echo ""

# Token estimation (rough: 1 token ≈ 3 bytes for mixed content)
estimate_tokens() {
    local bytes=$1
    echo $((bytes / 3))
}

# Check session files
echo "📊 Session Files:"
echo "----------------"
total_session_bytes=0
total_session_lines=0
large_sessions=0

for f in "$SESSIONS_DIR"/*.jsonl; do
    [ -f "$f" ] || continue
    [ -f "${f}.lock" ] && continue
    [ "$f" == *".deleted."* ] && continue
    
    lines=$(wc -l < "$f" 2>/dev/null || echo 0)
    bytes=$(stat -c%s "$f" 2>/dev/null || stat -f%z "$f" 2>/dev/null || echo 0)
    total_session_bytes=$((total_session_bytes + bytes))
    total_session_lines=$((total_session_lines + lines))
    
    if [ "$bytes" -gt 307200 ]; then
        ((large_sessions++))
        echo "  ⚠️  $(basename "$f"): $lines lines, $((bytes / 1024))KB (needs truncation)"
    fi
done

session_tokens=$(estimate_tokens $total_session_bytes)
echo ""
echo "  Total: $total_session_lines lines, ~$session_tokens tokens"
echo "  Large files: $large_sessions"
echo ""

# Check memory files
echo "📝 Memory Files:"
echo "----------------"

# MEMORY.md
if [ -f "$MEMORY_DIR/../MEMORY.md" ]; then
    memory_bytes=$(stat -c%s "$MEMORY_DIR/../MEMORY.md" 2>/dev/null || stat -f%z "$MEMORY_DIR/../MEMORY.md" 2>/dev/null || echo 0)
    memory_tokens=$(estimate_tokens $memory_bytes)
    echo "  MEMORY.md: ~$memory_tokens tokens"
else
    echo "  MEMORY.md: ❌ Not found"
fi

# Daily notes
echo ""
echo "  Daily Notes:"
today=$(date '+%Y-%m-%d')
yesterday=$(date -d "yesterday" '+%Y-%m-%d' 2>/dev/null || date -v-1d '+%Y-%m-%d' 2>/dev/null)

for date in "$today" "$yesterday"; do
    note="$MEMORY_DIR/$date.md"
    if [ -f "$note" ]; then
        bytes=$(stat -c%s "$note" 2>/dev/null || stat -f%z "$note" 2>/dev/null || echo 0)
        tokens=$(estimate_tokens $bytes)
        echo "    $date.md: ~$tokens tokens ✅"
    else
        echo "    $date.md: Not found"
    fi
done

# Summaries
echo ""
echo "  Summaries:"
if [ -d "$SUMMARIES_DIR" ]; then
    summary_count=$(find "$SUMMARIES_DIR" -name "*.md" | wc -l)
    summary_bytes=$(find "$SUMMARIES_DIR" -name "*.md" -exec cat {} \; 2>/dev/null | wc -c)
    summary_tokens=$(estimate_tokens $summary_bytes)
    echo "    $summary_count summaries, ~$summary_tokens tokens total"
else
    echo "    No summaries directory"
fi

echo ""

# Context budget calculation
echo "📈 Context Budget:"
echo "-----------------"
echo "  Model limit: 80,000 tokens"
echo ""

# Estimate each layer
l4_tokens=0
l3_tokens=0
l2_tokens=0

# L4: MEMORY.md
if [ -f "$MEMORY_DIR/../MEMORY.md" ]; then
    bytes=$(stat -c%s "$MEMORY_DIR/../MEMORY.md" 2>/dev/null || stat -f%z "$MEMORY_DIR/../MEMORY.md" 2>/dev/null || echo 0)
    l4_tokens=$(estimate_tokens $bytes)
fi

# L3: Summaries
if [ -d "$SUMMARIES_DIR" ]; then
    summary_bytes=$(find "$SUMMARIES_DIR" -name "*.md" -exec cat {} \; 2>/dev/null | wc -c)
    l3_tokens=$(estimate_tokens $summary_bytes)
fi

# L2: Session files (limited to window)
l2_tokens=$session_tokens
if [ "$l2_tokens" -gt 25000 ]; then
    l2_tokens=25000
fi

echo "  L4 (Long-term memory): ~$l4_tokens tokens"
echo "  L3 (Summaries):        ~$l3_tokens tokens"
echo "  L2 (Recent sessions):  ~$l2_tokens tokens"
echo "  L1 (Current session):  ~30,000 tokens (estimated)"
echo "  System messages:       ~10,000 tokens"
echo ""
total_estimated=$((l4_tokens + l3_tokens + l2_tokens + 30000 + 10000))
echo "  Estimated total:       ~$total_estimated tokens"

if [ "$total_estimated" -gt 80000 ]; then
    echo ""
    echo "  ⚠️  WARNING: Estimated context exceeds limit!"
    echo "  Recommendations:"
    echo "    1. Run truncation: truncate-sessions-safe.sh"
    echo "    2. Reduce L3 summaries: delete older summaries"
    echo "    3. Compress MEMORY.md"
else
    echo ""
    echo "  ✅ Context within budget"
fi

echo ""

# Check crontab
echo "⚙️  System Configuration:"
echo "-----------------------"
if crontab -l 2>/dev/null | grep -q "truncate-sessions"; then
    echo "  Truncation cron: ✅ Installed"
else
    echo "  Truncation cron: ❌ Not installed"
    echo "    Run: crontab -e and add:"
    echo "    */10 * * * * $WORKSPACE/skills/context-compression/scripts/truncate-sessions-safe.sh"
fi

if crontab -l 2>/dev/null | grep -q "generate-daily-summary"; then
    echo "  Summary cron: ✅ Installed"
else
    echo "  Summary cron: ⚠️  Not installed (optional)"
fi

echo ""
echo "=== End of Health Check ==="
