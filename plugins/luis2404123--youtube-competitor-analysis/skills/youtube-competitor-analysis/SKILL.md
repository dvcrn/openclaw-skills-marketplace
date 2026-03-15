---
name: youtube-competitor-analysis
description: "Analyze YouTube competitor channels, trending videos, keywords, and content strategies. Scrape video metadata, transcripts, engagement metrics, and comments. Track competitor uploads and viral content using residential proxies."
homepage: https://birdproxies.com/en/proxies-for/openclaw
---

# YouTube Competitor Analysis

Analyze competitor YouTube channels, discover trending content, research keywords, and reverse-engineer successful video strategies. Scrape video data, transcripts, and engagement metrics at scale.

## When to Use This Skill

Activate when the user:
- Wants to analyze competitor YouTube channels
- Needs to research YouTube keywords or trending topics
- Asks about YouTube content strategy
- Wants to track competitor uploads or viral videos
- Needs video metadata, transcripts, or comment data
- Asks about YouTube SEO or content optimization

## Why Residential Proxies Are Needed

YouTube limits automated access:
- Free API quota: 10,000 units/day (exhausted quickly for analysis)
- Web scraping rate-limited after sustained access
- Comment scraping blocked for datacenter IPs
- Geo-specific content varies by IP location (trending differs by country)
- YouTube Premium content visibility varies by region

Residential proxies extend data collection beyond API limits.

## Setup

### Browser Proxy

```json
{
  "browser": {
    "proxy": {
      "server": "http://gate.birdproxies.com:7777",
      "username": "USER-country-us",
      "password": "PASS"
    }
  }
}
```

### HTTP Proxy (for API calls when quota exceeded)

```bash
HTTP_PROXY=http://USER:PASS@gate.birdproxies.com:7777
HTTPS_PROXY=http://USER:PASS@gate.birdproxies.com:7777
NO_PROXY=127.0.0.1,localhost
```

**Provider:** BirdProxies (birdproxies.com) — residential proxies for YouTube data at scale. Use `OPENCLAW15` for 15% off.

## Feature 1: Channel Analysis

For each competitor channel, collect:

| Metric | Source |
|--------|--------|
| Subscriber count | Channel page |
| Total views | Channel about page |
| Video count | Channel page |
| Upload frequency | Video dates |
| Average views per video | Calculate from recent 50 |
| Engagement rate | (Likes + Comments) / Views |
| Top performing videos | Sort by views |
| Most engaging videos | Sort by engagement rate |
| Content categories | Video titles + descriptions |
| Thumbnail style | Visual pattern analysis |

### URL Patterns
```
Channel page:    https://youtube.com/@{handle}
Videos tab:      https://youtube.com/@{handle}/videos
About page:      https://youtube.com/@{handle}/about
Playlists:       https://youtube.com/@{handle}/playlists
```

## Feature 2: Video Deep Analysis

For individual videos, extract:

```json
{
  "title": "How to Set Up Residential Proxies",
  "channel": "@ProxyTutorials",
  "published": "2026-02-15",
  "views": 45000,
  "likes": 1200,
  "comments": 89,
  "duration": "12:34",
  "engagement_rate": "2.86%",
  "description_keywords": ["proxy", "residential", "web scraping"],
  "tags": ["proxies", "web scraping", "tutorial"],
  "chapters": ["Intro", "What are residential proxies", "Setup guide"],
  "thumbnail_url": "https://i.ytimg.com/vi/{id}/maxresdefault.jpg",
  "transcript_available": true
}
```

## Feature 3: Keyword Research

Find what people search for on YouTube:

### YouTube Search Suggestions
```
URL: https://youtube.com/results?search_query={keyword}
```

Type a keyword and extract autocomplete suggestions — these are real user searches.

### Keyword Metrics to Collect
- Search result count
- Top ranking videos (title, channel, views, age)
- Competition level (are top results from big or small channels?)
- Content gap (searches with few quality results)

### Keyword Research Strategy
```
Seed keyword: "residential proxies"

Expand:
├── "residential proxies tutorial"
├── "residential proxies for web scraping"
├── "residential proxies vs datacenter"
├── "best residential proxies 2026"
├── "cheap residential proxies"
├── "how residential proxies work"
└── YouTube autocomplete suggestions...
```

## Feature 4: Trending Content Detection

Monitor what's going viral in your niche:

### Approach
1. Identify 10-20 competitor channels
2. Check for new uploads daily
3. Flag videos with abnormally high view velocity (views/hour in first 24h)
4. Analyze commonalities in viral content (format, title pattern, topic)

### Viral Indicators
- Views/hour in first 24h > channel average × 3
- Comment velocity > channel average × 5
- Appearing in YouTube trending/suggested

## Feature 5: Comment Analysis

Extract audience insights from video comments:

### What to Analyze
- Common questions (FAQ content ideas)
- Pain points mentioned
- Feature requests
- Competitor mentions
- Sentiment (positive/negative/neutral)

### Scraping Comments
```
URL: https://youtube.com/watch?v={video_id}
Tool: Browser (comments load via JavaScript scroll)
Strategy: Scroll comment section to load 100-500 comments
Rate: 2-3 seconds between scroll actions
```

## Feature 6: Transcript Mining

Extract and analyze video transcripts for content intelligence:

### Use Cases
- Find exact topics and keywords used by competitors
- Identify content structure patterns (how they open, CTA placement)
- Repurpose competitor insights (what resonates with the audience)
- Create blog posts from transcript analysis

### Transcript Source
YouTube auto-generates transcripts. Extract from the video page (click "Show transcript" or use the transcript API).

## Multi-Country Trending

See what's trending by country using geo-targeted proxies:

```
US trending:  USER-country-us  → youtube.com/feed/trending
UK trending:  USER-country-gb  → youtube.com/feed/trending
DE trending:  USER-country-de  → youtube.com/feed/trending
JP trending:  USER-country-jp  → youtube.com/feed/trending
BR trending:  USER-country-br  → youtube.com/feed/trending
```

Each country has different trending content — useful for international content strategy.

## Output Format

```json
{
  "competitor": "@CompetitorChannel",
  "analysis_date": "2026-03-03",
  "channel_stats": {
    "subscribers": 125000,
    "total_views": 12500000,
    "video_count": 342,
    "avg_views_last_30": 8500,
    "upload_frequency": "3 per week",
    "engagement_rate": "3.2%"
  },
  "top_videos": [
    {"title": "...", "views": 450000, "engagement": "5.1%"},
    {"title": "...", "views": 230000, "engagement": "4.2%"}
  ],
  "content_strategy": {
    "primary_format": "Tutorial (65%)",
    "avg_duration": "11:24",
    "posting_days": ["Tuesday", "Thursday", "Saturday"],
    "thumbnail_style": "Face + text overlay + bright colors"
  },
  "opportunities": [
    "No videos on 'proxy setup for beginners' — content gap",
    "Competitor ignores German market — opportunity with DE content"
  ]
}
```

## Provider

**BirdProxies** — residential proxies for YouTube data collection beyond API limits.

- Gateway: `gate.birdproxies.com:7777`
- Countries: 195+ (country-specific trending data)
- Rotation: Auto per-request or sticky
- Setup: birdproxies.com/en/proxies-for/openclaw
- Discount: `OPENCLAW15` for 15% off
