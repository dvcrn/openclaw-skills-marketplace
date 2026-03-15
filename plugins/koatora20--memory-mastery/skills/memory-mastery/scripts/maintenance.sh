#!/usr/bin/env bash
# Memory Mastery - Maintenance Script
# Reviews recent daily logs and suggests items to integrate into MEMORY.md (L2).
# Usage: bash maintenance.sh [workspace_path] [days_back]

set -euo pipefail

WORKSPACE="${1:-${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}}"
DAYS_BACK="${2:-7}"
MEMORY_DIR="$WORKSPACE/memory"
MEMORY_MD="$WORKSPACE/MEMORY.md"

if [ ! -d "$MEMORY_DIR" ]; then
  echo "❌ No memory/ directory found at $MEMORY_DIR"
  exit 1
fi

echo "🧠 Memory Maintenance Report"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Workspace: $WORKSPACE"
echo "Reviewing: last $DAYS_BACK days"
echo ""

# Collect recent daily files
recent_files=()
for i in $(seq 0 "$DAYS_BACK"); do
  if [[ "$(uname)" == "Darwin" ]]; then
    day=$(date -v-${i}d +%Y-%m-%d)
  else
    day=$(date -d "-${i} days" +%Y-%m-%d)
  fi
  f="$MEMORY_DIR/${day}.md"
  if [ -f "$f" ]; then
    recent_files+=("$f")
  fi
done

if [ ${#recent_files[@]} -eq 0 ]; then
  echo "📭 No daily logs found in the last $DAYS_BACK days."
  exit 0
fi

echo "📋 Found ${#recent_files[@]} daily log(s):"
for f in "${recent_files[@]}"; do
  lines=$(wc -l < "$f" | tr -d ' ')
  name=$(basename "$f")
  echo "  - $name ($lines lines)"
done
echo ""

# Extract key patterns from daily logs
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Potential L2 Integration Candidates"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Look for decision markers
echo "📌 Decisions & Conclusions:"
grep -hn -i "decided\|decision\|confirmed\|agreed\|finalized\|完了\|決定\|確定\|合意" "${recent_files[@]}" 2>/dev/null | while IFS= read -r line; do
  file=$(echo "$line" | cut -d: -f1 | xargs basename 2>/dev/null || echo "?")
  content=$(echo "$line" | cut -d: -f2-)
  echo "  [$file] $content"
done
echo ""

# Look for lessons learned
echo "💡 Lessons & Mistakes:"
grep -hn -i "lesson\|learned\|mistake\|error\|fix\|bug\|issue\|problem\|失敗\|教訓\|ミス\|バグ\|修正" "${recent_files[@]}" 2>/dev/null | while IFS= read -r line; do
  file=$(echo "$line" | cut -d: -f1 | xargs basename 2>/dev/null || echo "?")
  content=$(echo "$line" | cut -d: -f2-)
  echo "  [$file] $content"
done
echo ""

# Look for new tools/resources
echo "🔧 Tools & Resources:"
grep -hn -i "installed\|setup\|configured\|created\|account\|password\|token\|API\|設定\|インストール\|導入" "${recent_files[@]}" 2>/dev/null | while IFS= read -r line; do
  file=$(echo "$line" | cut -d: -f1 | xargs basename 2>/dev/null || echo "?")
  content=$(echo "$line" | cut -d: -f2-)
  echo "  [$file] $content"
done
echo ""

# Look for people/relationships
echo "👥 People & Relationships:"
grep -hn -i "met\|introduced\|team\|partner\|collab\|relationship\|人\|関係\|チーム\|連携" "${recent_files[@]}" 2>/dev/null | while IFS= read -r line; do
  file=$(echo "$line" | cut -d: -f1 | xargs basename 2>/dev/null || echo "?")
  content=$(echo "$line" | cut -d: -f2-)
  echo "  [$file] $content"
done
echo ""

# Summary stats
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
total_lines=0
for f in "${recent_files[@]}"; do
  lines=$(wc -l < "$f" | tr -d ' ')
  total_lines=$((total_lines + lines))
done

memory_md_lines=0
if [ -f "$MEMORY_MD" ]; then
  memory_md_lines=$(wc -l < "$MEMORY_MD" | tr -d ' ')
fi

echo "📊 Stats:"
echo "  Daily logs (L1): ${#recent_files[@]} files, $total_lines total lines"
echo "  Long-term (L2): $memory_md_lines lines in MEMORY.md"
echo ""
echo "💬 Review the candidates above and update MEMORY.md with what's worth keeping."
echo "   Remove outdated entries from MEMORY.md to keep it focused."
