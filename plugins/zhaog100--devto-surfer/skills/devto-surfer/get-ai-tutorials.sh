#!/bin/bash
# Dev.to AI Tutorials Surfer
# 快速获取热门 AI 教程

echo "# 🌊 Dev.to - Top AI Tutorials"
echo "Generated at: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 获取热门 AI 文章（过去 7 天）
curl -s "https://dev.to/api/articles?tag=ai&per_page=10&top=7" | jq -r '.[] | 
  "**\(.title)**\n   - Author: \(.user.username)\n   - Reactions: \(.positive_reactions_count) | Comments: \(.comments_count)\n   - Reading Time: \(.reading_time_minutes) min\n   - URL: \(.url)\n"'

echo "---"
echo "✅ Retrieved 10 AI tutorials"
