#!/usr/bin/env bash
# review.sh — Quick health check on your learnings
# Usage: ./review.sh [workspace_path]

set -uo pipefail

WORKSPACE="${1:-.}"
LEARNINGS_DIR="${WORKSPACE}/.learnings"

if [[ ! -d "$LEARNINGS_DIR" ]]; then
  echo "No .learnings/ directory found at ${WORKSPACE}"
  exit 1
fi

echo "🧠 Agent Memory Loop — Review"
echo ""

# Count entries per file
for file in errors.md learnings.md wishes.md; do
  if [[ -f "${LEARNINGS_DIR}/${file}" ]]; then
    count=$(grep -c "^\[" "${LEARNINGS_DIR}/${file}" 2>/dev/null || echo "0")
    echo "  📄 ${file}: ${count} entries"
  fi
done

echo ""

# Find entries needing promotion (count:3+)
echo "  🔺 Ready for promotion (count:3+):"
needs_promotion=false
for file in errors.md learnings.md wishes.md; do
  if [[ -f "${LEARNINGS_DIR}/${file}" ]]; then
    while IFS= read -r line; do
      if [[ -n "$line" ]]; then
        echo "     ${file}: ${line}"
        needs_promotion=true
      fi
    done < <(grep -E "count:[3-9][0-9]*" "${LEARNINGS_DIR}/${file}" 2>/dev/null | grep -v "PROMOTED" || true)
  fi
done
if [[ "$needs_promotion" == "false" ]]; then
  echo "     (none)"
fi

echo ""

# Check file sizes
echo "  📏 File sizes:"
over_limit=false
for file in errors.md learnings.md wishes.md; do
  if [[ -f "${LEARNINGS_DIR}/${file}" ]]; then
    lines=$(wc -l < "${LEARNINGS_DIR}/${file}" 2>/dev/null || echo "0")
    lines=$(echo "$lines" | tr -d ' ')
    status="✅"
    if (( lines > 100 )); then
      status="⚠️  OVER LIMIT"
      over_limit=true
    fi
    echo "     ${file}: ${lines} lines ${status}"
  fi
done

if [[ "$over_limit" == "true" ]]; then
  echo ""
  echo "  ⚠️  Files over 100 lines need trimming:"
  echo "     1. Promote all count:3+ entries"
  echo "     2. Archive old entries to .learnings/archive/"
  echo "     3. Delete count:1 entries older than 90 days"
fi

echo ""

# Recent activity (last 7 days)
echo "  📅 Last 7 days of activity:"
week_ago=$(date -v-7d '+%Y-%m-%d' 2>/dev/null || date -d '7 days ago' '+%Y-%m-%d' 2>/dev/null || echo "")
if [[ -n "$week_ago" ]]; then
  recent=$(grep -h "^\[" "${LEARNINGS_DIR}"/*.md 2>/dev/null | awk -v d="$week_ago" '$0 >= "["d' | wc -l || echo "0")
  recent=$(echo "$recent" | tr -d ' ')
  echo "     ${recent} entries logged"
else
  echo "     (date calculation not available)"
fi
