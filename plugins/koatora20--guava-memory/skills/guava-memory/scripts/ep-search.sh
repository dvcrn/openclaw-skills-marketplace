#!/bin/bash
# ep-search.sh — エピソード検索（Q-valueフィルタ付き）
# Usage: ep-search.sh <query>
# 
# memory_searchの結果からエピソードファイルを抽出し、
# Q-valueでソートして表示する。

EPISODES_DIR="${HOME}/.openclaw/workspace/memory/episodes"
INDEX="${EPISODES_DIR}/index.json"
QUERY="$1"

if [ -z "$QUERY" ]; then
  echo "Usage: $0 <search query>"
  exit 1
fi

if [ ! -f "$INDEX" ]; then
  echo "❌ index.json not found. Run ep-record.sh first."
  exit 1
fi

echo "🔍 Searching episodes for: $QUERY"
echo "---"

# index.jsonからQ-valueでソートして表示
cat "$INDEX" | jq -r '.episodes | sort_by(-.q_value) | .[] | select(.status == "active") | "Q:\(.q_value) | \(.feel) | \(.intent) → \(.file)"'

echo "---"
echo "📊 Stats: $(cat "$INDEX" | jq -r '.stats | "Total: \(.total) | Avg Q: \(.avg_q_value) | Promotions: \(.promotions)"')"
