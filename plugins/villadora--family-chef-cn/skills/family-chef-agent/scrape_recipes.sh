#!/bin/bash

# 菜谱搜索脚本
# 主要用于读取缓存或备用搜索

SCRIPT_DIR="$(dirname "$0")"
DATA_DIR="$SCRIPT_DIR/../data"
RECIPES_DIR="$DATA_DIR/recipes"

mkdir -p "$RECIPES_DIR"

KEYWORD="${1:-红烧肉}"
SAVE="${2:-false}"  # 是否保存结果

# 清理关键词作为文件名
FILENAME=$(echo "$KEYWORD" | sed 's/[/\\]/_/g')
RECIPE_FILE="$RECIPES_DIR/${FILENAME}.json"

echo "搜索关键词: $KEYWORD"
echo ""

# 方法1: 优先读取历史数据
if [ -f "$RECIPE_FILE" ]; then
  TIMESTAMP=$(cat "$RECIPE_FILE" | jq -r '.timestamp' 2>/dev/null)
  echo "=== 已保存的菜谱 (更新时间: $TIMESTAMP) ==="
  echo ""
  cat "$RECIPE_FILE" | jq -r '.results[] | "标题: \(.title)\n链接: \(.url)\n---\n"'
  exit 0
fi

# 方法2: 尝试搜索
SearXNG_URL="${SEARXNG_URL:-http://host.docker.internal:18888}"
QUERY=$(echo "$KEYWORD 菜谱 下厨房" | sed 's/ /+/g')

RESPONSE=$(curl -s --max-time 10 "$SearXNG_URL/search?q=$QUERY&format=json&limit=10&language=zh-CN" 2>/dev/null)

if [ -n "$RESPONSE" ] && echo "$RESPONSE" | grep -q '"title"'; then
  # 保存结果（如果需要）
  if [ "$SAVE" = "true" ]; then
    TIMESTAMP=$(date -Iseconds)
    echo "$RESPONSE" | jq "{query: \"$KEYWORD\", results: [.results[] | {title: .title, url: .url, snippet: (.content // .snippet)}], timestamp: \"$TIMESTAMP\"}" 2>/dev/null > "$RECIPE_FILE"
    echo "结果已保存到: $RECIPE_FILE"
    echo ""
  fi

  echo "=== 搜索结果 ==="
  echo "$RESPONSE" | grep -o '"title":"[^"]*"' | sed 's/"title":"//g' | sed 's/"$//g' | head -10 | nl
  exit 0
fi

# 方法3: 无数据
echo "=== 暂无菜谱信息 ==="
echo "请使用 OpenClaw 搜索功能：search(query=\"$KEYWORD 菜谱 下厨房\")"
