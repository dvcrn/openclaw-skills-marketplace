---
name: hacker-news-surfer
description: "Surf Hacker News for AI and tech discussions. Get top stories, search for AI topics, and analyze trending tech news."
---

# Hacker News Surfer

Hacker News（HN）冲浪技能，获取热门技术话题和 AI 相关讨论。

## Features

- ✅ **Top Stories** - Get current top stories
- ✅ **New Stories** - Get latest submissions
- ✅ **Best Stories** - Get highest-rated stories
- ✅ **Search AI Topics** - Find AI-related discussions
- ✅ **Story Details** - Get comments and metadata

## API

**Base URL**: `https://hacker-news.firebaseio.com/v0/`

**Endpoints**:
- `/topstories.json` - Top story IDs
- `/newstories.json` - New story IDs
- `/beststories.json` - Best story IDs
- `/item/{id}.json` - Story details
- `/user/{id}.json` - User profile

## Usage

### Get Top Stories

```bash
# Get top 10 story IDs
curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" | jq -r '.[:10]'

# Get story details
curl -s "https://hacker-news.firebaseio.com/v0/item/47306655.json" | jq '{
  title: .title,
  url: .url,
  score: .score,
  by: .by,
  time: .time
}'
```

### Search AI Topics

```bash
# Get top stories and filter for AI
curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" | \
  jq -r '.[:50]' | \
  while read id; do
    curl -s "https://hacker-news.firebaseio.com/v0/item/$id.json" | \
      jq -r 'select(.title | test("AI|artificial intelligence|machine learning|ML|GPT|Claude"; "i"))'
  done
```

## Quick Test

```bash
# Test API connection
curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" | jq -r '.[0]'
```

## Examples

See `USAGE.md` for detailed examples:
- Get top AI stories
- Search specific topics
- Analyze story trends
- Get user profiles

## Installation

✅ No installation required - uses public API

## Rate Limit

- No official rate limit
- Be respectful (1 request/second recommended)

## Cost

- ✅ **Free** - No API key required
