#!/bin/bash

# 更新菜价脚本
# 使用 OpenClaw 搜索并保存结果到 data/prices/

SCRIPT_DIR="$(dirname "$0")"
DATA_DIR="$SCRIPT_DIR/../data"
PRICES_DIR="$DATA_DIR/prices"

mkdir -p "$PRICES_DIR"

CITY="${1:-上海}"
INGREDIENT="${2:-鸡腿}"

echo "=== 更新菜价: $CITY $INGREDIENT ==="
echo ""

# 检查 SearXNG 是否可用
SearXNG_URL="${SEARXNG_URL:-http://host.docker.internal:18888}"
QUERY=$(echo "$CITY $INGREDIENT 价格" | sed 's/ /+/g')

RESPONSE=$(curl -s --max-time 10 "$SearXNG_URL/search?q=$QUERY&format=json&limit=10&language=zh-CN" 2>/dev/null)

if [ -n "$RESPONSE" ] && echo "$RESPONSE" | grep -q '"title"'; then
  # 提取结果
  TIMESTAMP=$(date -Iseconds)

  # 保存原始 JSON
  echo "$RESPONSE" | jq "{query: \"$CITY $INGREDIENT\", results: [.results[] | {title: .title, url: .url, snippet: (.content // .snippet)}], timestamp: \"$TIMESTAMP\"}" 2>/dev/null > "$PRICES_DIR/${CITY}_${INGREDIENT}.json"

  echo "已保存到: $PRICES_DIR/${CITY}_${INGREDIENT}.json"
  echo ""

  # 显示结果
  echo "=== 搜索结果 ==="
  cat "$PRICES_DIR/${CITY}_${INGREDIENT}.json" | jq -r '.results[:5][] | "标题: \(.title)\n链接: \(.url)\n---\n"'
else
  echo "SearXNG 不可用，请使用 OpenClaw 内置搜索功能"
  echo "搜索: $CITY $INGREDIENT 价格"
  exit 1
fi
