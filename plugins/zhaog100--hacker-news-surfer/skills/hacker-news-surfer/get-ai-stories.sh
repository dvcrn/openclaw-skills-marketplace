#!/bin/bash
# Hacker News AI Stories Surfer
# 快速获取 AI 相关热门故事

echo "# 🌊 Hacker News - Top AI Stories"
echo "Generated at: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 获取前 50 个热门故事
STORY_IDS=$(curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" | jq -r '.[:50][]')

COUNT=0

for ID in $STORY_IDS; do
  # 获取故事详情
  STORY=$(curl -s "https://hacker-news.firebaseio.com/v0/item/$ID.json")
  
  # 检查是否包含 AI 关键词
  TITLE=$(echo "$STORY" | jq -r '.title')
  
  if echo "$TITLE" | grep -qiE "AI|artificial intelligence|machine learning|ML|GPT|Claude|LLM|neural|OpenAI|Anthropic"; then
    COUNT=$((COUNT + 1))
    
    SCORE=$(echo "$STORY" | jq -r '.score')
    URL=$(echo "$STORY" | jq -r '.url // "https://news.ycombinator.com/item?id=$ID"')
    
    echo "$COUNT. **$TITLE**"
    echo "   - Score: $SCORE"
    echo "   - URL: $URL"
    echo ""
    
    if [ $COUNT -eq 10 ]; then
      break
    fi
  fi
  
  sleep 0.3
done

echo "---"
echo "✅ Found $COUNT AI-related stories"
