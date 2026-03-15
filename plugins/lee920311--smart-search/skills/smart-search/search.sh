#!/bin/bash
# Smart Search - 智能搜索引擎切换执行脚本

QUERY="$1"
MAX_RESULTS="${2:-5}"

# 加载环境变量
if [ -f ~/.openclaw/.env ]; then
    export $(grep -v '^#' ~/.openclaw/.env | xargs)
fi

# 决策逻辑：判断用哪个引擎
decide_engine() {
    local query="$1"
    
    # 用户指定优先
    if [[ "$query" == *"用 sear"* ]] || [[ "$query" == *"用 SearXNG"* ]]; then
        echo "searxng"
        return
    fi
    
    # AI 内容生成 → Tavily
    if [[ "$query" == *"小红书"* ]] || [[ "$query" == *"写文案"* ]] || [[ "$query" == *"公众号"* ]] || [[ "$query" == *"生成"* ]]; then
        echo "tavily"
        return
    fi
    
    # 默认用 SearXNG（免费）
    echo "searxng"
}

ENGINE=$(decide_engine "$QUERY")

echo "🔍 Smart Search: 使用 $ENGINE"
echo ""

# 调用对应的搜索工具
case "$ENGINE" in
  "tavily")
    if [ -z "$TAVILY_API_KEY" ]; then
      echo "❌ Tavily API Key 未配置"
      exit 1
    fi
    python3 ~/.openclaw/workspace/skills/openclaw-tavily-search/scripts/tavily_search.py \
      --query "$QUERY" \
      --max-results "$MAX_RESULTS" \
      --format md
    ;;
  
  "searxng")
    if [ -z "$SEARXNG_URL" ]; then
      SEARXNG_URL="https://searx.be"
    fi
    echo "📊 SearXNG 搜索结果："
    echo "查询：$QUERY"
    echo "实例：$SEARXNG_URL"
    echo ""
    
    # 尝试 JSON 格式
    RESPONSE=$(curl -s -A "Mozilla/5.0" "$SEARXNG_URL/search?q=$QUERY&format=json" 2>/dev/null)
    
    # 检查是否返回 JSON
    if echo "$RESPONSE" | grep -q "^{"; then
      echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    results = data.get('results', [])[:$MAX_RESULTS]
    for i, r in enumerate(results, 1):
        print(f\"{i}. {r.get('title', '无标题')}\")
        print(f\"   {r.get('url', '无链接')}\")
        content = r.get('content', '')[:200]
        print(f\"   {content}...\")
        print()
except Exception as e:
    print(f'解析失败：{e}')
"
    else
      echo "⚠️  SearXNG 实例返回非 JSON 格式，切换到 Tavily..."
      echo ""
      # 降级到 Tavily
      python3 ~/.openclaw/workspace/skills/openclaw-tavily-search/scripts/tavily_search.py \
        --query "$QUERY" \
        --max-results "$MAX_RESULTS" \
        --format md
    fi
    ;;
  
  *)
    echo "⚠️  未知引擎：$ENGINE"
    exit 1
    ;;
esac
