# Hacker News Surfer 使用指南

## 🚀 快速开始

### **1. 获取热门故事**

```bash
# 获取前 10 个热门故事 ID
curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" | jq -r '.[:10]'
```

### **2. 获取故事详情**

```bash
# 获取故事详情（以 ID 47306655 为例）
curl -s "https://hacker-news.firebaseio.com/v0/item/47306655.json" | jq '{
  id: .id,
  title: .title,
  url: .url,
  score: .score,
  by: .by,
  time: (.time | strftime("%Y-%m-%d %H:%M:%S")),
  descendants: .descendants
}'
```

---

## 🎯 实际用例

### **用例 1：获取前 10 个 AI 相关热门故事**

```bash
#!/bin/bash

# 获取前 50 个热门故事
STORY_IDS=$(curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" | jq -r '.[:50][]')

echo "# Top AI Stories on Hacker News"
echo ""

COUNT=0

for ID in $STORY_IDS; do
  # 获取故事详情
  STORY=$(curl -s "https://hacker-news.firebaseio.com/v0/item/$ID.json")
  
  # 检查是否包含 AI 关键词
  TITLE=$(echo "$STORY" | jq -r '.title')
  
  if echo "$TITLE" | grep -qiE "AI|artificial intelligence|machine learning|ML|GPT|Claude|LLM|neural"; then
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
  
  sleep 0.5
done

echo "---"
echo "Found $COUNT AI-related stories"
```

---

### **用例 2：获取最新 AI 故事**

```bash
#!/bin/bash

# 获取最新 100 个故事
STORY_IDS=$(curl -s "https://hacker-news.firebaseio.com/v0/newstories.json" | jq -r '.[:100][]')

echo "# Latest AI Stories on Hacker News"
echo ""

COUNT=0

for ID in $STORY_IDS; do
  STORY=$(curl -s "https://hacker-news.firebaseio.com/v0/item/$ID.json")
  TITLE=$(echo "$STORY" | jq -r '.title')
  
  if echo "$TITLE" | grep -qiE "AI|artificial intelligence|machine learning|ML|GPT|Claude"; then
    COUNT=$((COUNT + 1))
    
    TIME=$(echo "$STORY" | jq -r '.time')
    SCORE=$(echo "$STORY" | jq -r '.score')
    URL=$(echo "$STORY" | jq -r '.url // "https://news.ycombinator.com/item?id=$ID"')
    
    echo "$COUNT. **$TITLE**"
    echo "   - Time: $(date -d @$TIME '+%Y-%m-%d %H:%M:%S')"
    echo "   - Score: $SCORE"
    echo "   - URL: $URL"
    echo ""
    
    if [ $COUNT -eq 5 ]; then
      break
    fi
  fi
  
  sleep 0.5
done
```

---

### **用例 3：获取故事评论**

```bash
#!/bin/bash

STORY_ID="47306655"

# 获取故事详情
STORY=$(curl -s "https://hacker-news.firebaseio.com/v0/item/$STORY_ID.json")

TITLE=$(echo "$STORY" | jq -r '.title')
KIDS=$(echo "$STORY" | jq -r '.kids // [] | .[:5][]')

echo "# Story: $TITLE"
echo ""
echo "## Top Comments:"
echo ""

COUNT=0

for KID in $KIDS; do
  COMMENT=$(curl -s "https://hacker-news.firebaseio.com/v0/item/$KID.json")
  
  BY=$(echo "$COMMENT" | jq -r '.by')
  TEXT=$(echo "$COMMENT" | jq -r '.text' | sed 's/<[^>]*>//g' | head -c 200)
  
  COUNT=$((COUNT + 1))
  echo "**$COUNT. $BY said:**"
  echo "$TEXT..."
  echo ""
  
  sleep 0.3
done
```

---

### **用例 4：搜索特定主题**

```bash
#!/bin/bash

TOPIC="Claude"

echo "# Stories about $TOPIC"
echo ""

# 搜索最新 500 个故事
STORY_IDS=$(curl -s "https://hacker-news.firebaseio.com/v0/newstories.json" | jq -r '.[:500][]')

COUNT=0

for ID in $STORY_IDS; do
  STORY=$(curl -s "https://hacker-news.firebaseio.com/v0/item/$ID.json")
  TITLE=$(echo "$STORY" | jq -r '.title')
  
  if echo "$TITLE" | grep -qi "$TOPIC"; then
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
  
  sleep 0.2
done

echo "---"
echo "Found $COUNT stories about $TOPIC"
```

---

### **用例 5：获取用户信息**

```bash
#!/bin/bash

USER="pg"

# 获取用户信息
USER_DATA=$(curl -s "https://hacker-news.firebaseio.com/v0/user/$USER.json")

KARMA=$(echo "$USER_DATA" | jq -r '.karma')
CREATED=$(echo "$USER_DATA" | jq -r '.created')
ABOUT=$(echo "$USER_DATA" | jq -r '.about // "No bio"')

echo "# User: $USER"
echo ""
echo "- **Karma**: $KARMA"
echo "- **Created**: $(date -d @$CREATED '+%Y-%m-%d')"
echo "- **About**: $ABOUT"
```

---

## 📊 API 端点总结

| 端点 | 说明 | 示例 |
|------|------|------|
| `/topstories.json` | 热门故事 ID | `curl .../topstories.json` |
| `/newstories.json` | 最新故事 ID | `curl .../newstories.json` |
| `/beststories.json` | 最佳故事 ID | `curl .../beststories.json` |
| `/item/{id}.json` | 故事详情 | `curl .../item/123.json` |
| `/user/{id}.json` | 用户信息 | `curl .../user/pg.json` |

---

## ⚠️ 注意事项

1. **速率限制**：
   - 无官方限制
   - 建议间隔：0.5-1 秒/请求

2. **数据格式**：
   - JSON 格式
   - 需要使用 `jq` 解析

3. **URL 处理**：
   - 部分 story 没有 URL（Ask HN 等）
   - 使用 `//` 运算符提供默认值

4. **时间戳**：
   - Unix timestamp（秒）
   - 需要 `date -d @timestamp` 转换

---

## 🎯 推荐冲浪策略

### **每日冲浪清单**

```bash
# 早上：快速查看热门 AI 故事（前 10 个）
bash get-top-ai-stories.sh

# 中午：搜索特定主题（如 Claude、GPT）
bash search-topic.sh Claude

# 晚上：查看最新 AI 故事（前 5 个）
bash get-latest-ai-stories.sh
```

---

**官家，Hacker News 冲浪技能已配置完成！** 🌾
