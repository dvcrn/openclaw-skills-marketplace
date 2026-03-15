#!/bin/bash
# Session Window Truncation Script
# Truncates session files to keep only recent N tokens

SESSIONS_DIR="${SESSIONS_DIR:-$HOME/.openclaw/agents/main/sessions}"
WINDOW_TOKENS="${WINDOW_TOKENS:-100000}"
KEEP_TURNS="${KEEP_TURNS:-10}"
DRY_RUN="${DRY_RUN:-false}"

# Approximate tokens per byte (rough estimate: 1 token ≈ 4 bytes for English, 2 bytes for Chinese)
BYTES_PER_TOKEN=3
WINDOW_BYTES=$((WINDOW_TOKENS * BYTES_PER_TOKEN))

echo "=== Session Window Truncation ==="
echo "Sessions dir: $SESSIONS_DIR"
echo "Window size: $WINDOW_TOKENS tokens (~$WINDOW_BYTES bytes)"
echo "Keep turns: $KEEP_TURNS"
echo "Dry run: $DRY_RUN"
echo ""

truncated_count=0
skipped_count=0
total_saved=0

# Find all session files
for file in "$SESSIONS_DIR"/*.jsonl; do
    # Skip if no files match
    [ -e "$file" ] || continue
    
    # Skip locked files (active sessions)
    if [ -f "${file}.lock" ]; then
        echo "⏭️  Skipping active session: $(basename "$file")"
        ((skipped_count++))
        continue
    fi
    
    # Skip deleted files
    if [[ "$file" == *.deleted.* ]]; then
        continue
    fi
    
    # Get file size
    file_size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
    
    # Skip if file is smaller than window
    if [ "$file_size" -le "$WINDOW_BYTES" ]; then
        continue
    fi
    
    # Calculate saved bytes
    saved_bytes=$((file_size - WINDOW_BYTES))
    
    if [ "$DRY_RUN" = "true" ]; then
        echo "🔍 Would truncate: $(basename "$file") ($((file_size / 1024))KB → $((WINDOW_BYTES / 1024))KB, save $((saved_bytes / 1024))KB)"
    else
        # Read file and keep last N bytes
        # For jsonl files, we need to keep complete lines
        temp_file="${file}.truncating"
        
        # Use tail to get the last portion of the file
        # Calculate approximate bytes to keep (add buffer for line alignment)
        keep_bytes=$((WINDOW_BYTES + 10000))
        
        # Get the last portion
        tail -c "$keep_bytes" "$file" > "$temp_file"
        
        # Replace original file
        mv "$temp_file" "$file"
        
        new_size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        echo "✂️  Truncated: $(basename "$file") ($((file_size / 1024))KB → $((new_size / 1024))KB, saved $((saved_bytes / 1024))KB)"
    fi
    
    ((truncated_count++))
    total_saved=$((total_saved + saved_bytes))
done

echo ""
echo "=== Summary ==="
echo "Files truncated: $truncated_count"
echo "Files skipped (active): $skipped_count"
echo "Total saved: $((total_saved / 1024))KB"
