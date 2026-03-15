#!/bin/bash

# 城市菜价搜索脚本
# 主要用于读取缓存或备用搜索

SCRIPT_DIR="$(dirname "$0")"
DATA_DIR="$SCRIPT_DIR/../data"
PRICES_DIR="$DATA_DIR/prices"

mkdir -p "$PRICES_DIR"

CITY="${1:-上海}"
INGREDIENT="${2:-鸡腿}"
SAVE="${3:-false}"

PRICE_FILE="$PRICES_DIR/${CITY}_${INGREDIENT}.json"

echo "城市: $CITY"
echo "食材: $INGREDIENT"
echo ""

# 方法1: 优先读取历史数据
if [ -f "$PRICE_FILE" ]; then
  TIMESTAMP=$(cat "$PRICE_FILE" | jq -r '.timestamp' 2>/dev/null)
  echo "=== 已保存的菜价 (更新时间: $TIMESTAMP) ==="
  echo ""
  cat "$PRICE_FILE" | jq -r '.results[:5][] | "标题: \(.title)\n链接: \(.url)\n---\n"'
  exit 0
fi

# 方法2: 尝试搜索
SearXNG_URL="${SEARXNG_URL:-http://host.docker.internal:18888}"
QUERY=$(echo "$CITY $INGREDIENT 价格" | sed 's/ /+/g')

RESPONSE=$(curl -s --max-time 10 "$SearXNG_URL/search?q=$QUERY&format=json&limit=10&language=zh-CN" 2>/dev/null)

if [ -n "$RESPONSE" ] && echo "$RESPONSE" | grep -q '"title"'; then
  # 保存结果（如果需要）
  if [ "$SAVE" = "true" ]; then
    TIMESTAMP=$(date -Iseconds)
    echo "$RESPONSE" | jq "{query: \"$CITY $INGREDIENT\", results: [.results[] | {title: .title, url: .url, snippet: (.content // .snippet)}], timestamp: \"$TIMESTAMP\"}" 2>/dev/null > "$PRICE_FILE"
    echo "结果已保存到: $PRICE_FILE"
    echo ""
  fi

  echo "=== 搜索结果 ==="
  echo "$RESPONSE" | grep -o '"title":"[^"]*"' | sed 's/"title":"//g' | sed 's/"$//g' | head -10 | nl
  exit 0
fi

# 方法3: 无数据
echo "=== 暂无菜价信息 ==="
echo "请使用 OpenClaw 搜索功能：search(query=\"$CITY $INGREDIENT 价格 盒马 叮咚\")"
