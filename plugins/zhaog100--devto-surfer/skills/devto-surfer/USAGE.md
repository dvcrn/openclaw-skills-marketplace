# Dev.to Surfer 使用指南

## 🚀 快速开始

### **1. 获取最新文章**

```bash
# 获取最新 10 篇文章
curl -s "https://dev.to/api/articles?per_page=10" | jq '.[] | {
  title: .title,
  url: .url,
  user: .user.username,
  reactions: .positive_reactions_count,
  comments: .comments_count
}'
```

### **2. 获取 AI 标签文章**

```bash
# 获取 AI 标签的最新文章
curl -s "https://dev.to/api/articles?tag=ai&per_page=10" | jq '.[] | {
  title: .title,
  url: .url,
  user: .user.username,
  reactions: .positive_reactions_count
}'
```

---

## 🎯 实际用例

### **用例 1：获取热门 AI 教程（前 10 篇）**

```bash
#!/bin/bash

echo "# Top AI Tutorials on Dev.to"
echo ""

curl -s "https://dev.to/api/articles?tag=ai&per_page=10&top=7" | jq -r '.[] | 
  "**\(.title)**\n   - Author: \(.user.username)\n   - Reactions: \(.positive_reactions_count)\n   - Comments: \(.comments_count)\n   - URL: \(.url)\n"'
```

---

### **用例 2：搜索多个标签（AI + Python）**

```bash
#!/bin/bash

echo "# Latest AI + Python Articles"
echo ""

curl -s "https://dev.to/api/articles?tag=ai,python&per_page=10" | jq -r '.[] | 
  "**\(.title)**\n   - Author: \(.user.username)\n   - Reactions: \(.positive_reactions_count)\n   - URL: \(.url)\n"'
```

---

### **用例 3：获取文章详情**

```bash
#!/bin/bash

ARTICLE_ID="123456"

# 获取文章详情
curl -s "https://dev.to/api/articles/$ARTICLE_ID" | jq '{
  title: .title,
  description: .description,
  user: .user.username,
  published_at: .published_at,
  reading_time: .reading_time_minutes,
  tags: .tag_list,
  url: .url,
  body: .body_markdown
}'
```

---

### **用例 4：获取用户文章**

```bash
#!/bin/bash

USERNAME="ben"

echo "# Articles by $USERNAME"
echo ""

curl -s "https://dev.to/api/articles?username=$USERNAME&per_page=10" | jq -r '.[] | 
  "**\(.title)**\n   - Reactions: \(.positive_reactions_count)\n   - URL: \(.url)\n"'
```

---

### **用例 5：分析热门标签**

```bash
#!/bin/bash

echo "# Trending AI Articles Analysis"
echo ""

# 获取最近 30 篇 AI 文章
ARTICLES=$(curl -s "https://dev.to/api/articles?tag=ai&per_page=30")

# 统计平均反应数
AVG_REACTIONS=$(echo "$ARTICLES" | jq -r '[.[] | .positive_reactions_count] | add / length')

# 统计平均评论数
AVG_COMMENTS=$(echo "$ARTICLES" | jq -r '[.[] | .comments_count] | add / length')

# 获取最高反应文章
TOP_ARTICLE=$(echo "$ARTICLES" | jq -r 'max_by(.positive_reactions_count) | 
  "**\(.title)**\n   - Reactions: \(.positive_reactions_count)\n   - URL: \(.url)"')

echo "**Average Reactions**: $AVG_REACTIONS"
echo "**Average Comments**: $AVG_COMMENTS"
echo ""
echo "**Most Popular Article**:"
echo "$TOP_ARTICLE"
```

---

## 📊 API 参数总结

| 参数 | 说明 | 示例 |
|------|------|------|
| `per_page` | 每页数量 | `per_page=10` |
| `tag` | 标签过滤 | `tag=ai` |
| `username` | 用户过滤 | `username=ben` |
| `top` | 热门时间范围（天） | `top=7` |
| `state` | 文章状态 | `state=rising` |

---

## 🏷️ 推荐 AI 标签

**主要标签**：
- `ai` - 人工智能
- `machinelearning` - 机器学习
- `python` - Python
- `javascript` - JavaScript
- `datascience` - 数据科学

**组合标签**：
- `ai,python` - AI + Python
- `machinelearning,python` - ML + Python
- `ai,javascript` - AI + JS

---

## ⚠️ 注意事项

1. **速率限制**：
   - 1000 请求/10 分钟（每个 IP）
   - 建议：1 请求/秒

2. **分页**：
   - 最大 `per_page=1000`
   - 默认 30 篇

3. **Markdown**：
   - 文章内容为 Markdown 格式
   - 需要渲染器显示

4. **图片**：
   - 封面图：`.cover_image`
   - 社交图：`.social_image`

---

## 🎯 推荐冲浪策略

### **每日冲浪清单**

```bash
# 早上：快速查看热门 AI 教程（前 10 篇）
bash get-top-ai-tutorials.sh

# 中午：搜索特定技术栈（AI + Python）
bash search-multi-tags.sh ai,python

# 晚上：查看最新 AI 文章（前 10 篇）
bash get-latest-ai-articles.sh
```

---

## 📊 实用脚本集合

### **脚本 1：获取热门 AI 教程**

```bash
#!/bin/bash
# File: get-top-ai-tutorials.sh

curl -s "https://dev.to/api/articles?tag=ai&per_page=10&top=7" | \
  jq -r '.[] | "**\(.title)**\n   - Author: \(.user.username)\n   - Reactions: \(.positive_reactions_count)\n   - URL: \(.url)\n"'
```

### **脚本 2：搜索多个标签**

```bash
#!/bin/bash
# File: search-multi-tags.sh

TAGS="${1:-ai,python}"

curl -s "https://dev.to/api/articles?tag=$TAGS&per_page=10" | \
  jq -r '.[] | "**\(.title)**\n   - Author: \(.user.username)\n   - Reactions: \(.positive_reactions_count)\n   - URL: \(.url)\n"'
```

### **脚本 3：分析趋势**

```bash
#!/bin/bash
# File: analyze-trends.sh

ARTICLES=$(curl -s "https://dev.to/api/articles?tag=ai&per_page=30")

echo "# AI Articles Trend Analysis"
echo ""

AVG_REACTIONS=$(echo "$ARTICLES" | jq -r '[.[] | .positive_reactions_count] | add / length')
AVG_COMMENTS=$(echo "$ARTICLES" | jq -r '[.[] | .comments_count] | add / length')

echo "**Average Reactions**: $AVG_REACTIONS"
echo "**Average Comments**: $AVG_COMMENTS"
```

---

**官家，Dev.to 冲浪技能已配置完成！** 🌾
