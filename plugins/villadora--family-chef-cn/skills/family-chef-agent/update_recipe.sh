#!/bin/bash

# 更新菜谱脚本
# 使用 OpenClaw 搜索并保存结果到 data/recipes/

SCRIPT_DIR="$(dirname "$0")"
DATA_DIR="$SCRIPT_DIR/../data"
RECIPES_DIR="$DATA_DIR/recipes"

mkdir -p "$RECIPES_DIR"

KEYWORD="${1:-红烧肉}"

echo "=== 更新菜谱: $KEYWORD ==="
echo ""

# 检查 SearXNG 是否可用
SearXNG_URL="${SEARXNG_URL:-http://host.docker.internal:18888}"
QUERY=$(echo "$KEYWORD 菜谱 下厨房" | sed 's/ /+/g')

RESPONSE=$(curl -s --max-time 10 "$SearXNG_URL/search?q=$QUERY&format=json&limit=10&language=zh-CN" 2>/dev/null)

if [ -n "$RESPONSE" ] && echo "$RESPONSE" | grep -q '"title"'; then
  # 提取结果
  TIMESTAMP=$(date -Iseconds)

  # 保存原始 JSON
  echo "$RESPONSE" | jq "{query: \"$KEYWORD\", results: [.results[] | {title: .title, url: .url, snippet: (.content // .snippet)}], timestamp: \"$TIMESTAMP\"}" 2>/dev/null > "$RECIPES_DIR/${KEYWORD}.json"

  echo "已保存到: $RECIPES_DIR/${KEYWORD}.json"
  echo ""

  # 显示结果
  echo "=== 搜索结果 ==="
  cat "$RECIPES_DIR/${KEYWORD}.json" | jq -r '.results[] | "标题: \(.title)\n链接: \(.url)\n---\n"'
else
  echo "SearXNG 不可用，请使用 OpenClaw 内置搜索功能"
  echo "搜索: $KEYWORD 菜谱 下厨房"
  exit 1
fi
