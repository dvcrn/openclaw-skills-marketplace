---
name: skillscope
description: "Search and discover AI Agent skills via the SkillScope public API. Use when a user wants to find skills by keyword, browse categories, check leaderboards, view skill details, or explore starter kits."
homepage: https://skillscope.cn
---

# SkillScope

Search, discover, and explore 18,000+ AI Agent skills via the SkillScope public API. Covers skill search, category browsing, leaderboards, author profiles, similar skill recommendations, starter kits, and guide articles.

## Setup

No API key required for basic usage (20 req/min, 200 req/day).

For higher limits, request a free API key and pass it via header:

```bash
curl -H "X-API-Key: sk-your-key-here" https://skillscope.cn/api/v1/skills
```

API key limits: 60 req/min, 5,000 req/day.

## Base URL

```
https://skillscope.cn/api/v1
```

## Search Skills

Find skills by keyword or natural language description. Uses hybrid search (full-text + semantic + reranker).

```bash
curl "https://skillscope.cn/api/v1/search?q=web+search"
```

Response includes `results[]` with `id`, `name`, `author`, `description`, `description_zh`, `description_en`, `categories`, `security_grade`, `quality_score`, `downloads`, `stars`.

## List Skills

Paginated skill listing sorted by quality score.

```bash
curl "https://skillscope.cn/api/v1/skills?page=1&page_size=20"
```

Parameters:
- `page`: page number (default 1)
- `page_size`: items per page (1-50, default 50)

## Featured Skills

Daily-rotating featured skills selected from top-rated popular skills.

```bash
curl "https://skillscope.cn/api/v1/skills/featured?limit=6"
```

## Skill Detail

Get full details for a specific skill by its ID (`author/name` format).

```bash
curl "https://skillscope.cn/api/v1/skills/steipete/weather"
```

Response includes full analysis, security scan results, community stats, and ClawHub data.

## Categories

List all categories with skill counts.

```bash
curl "https://skillscope.cn/api/v1/categories"
```

Get skills in a specific category:

```bash
curl "https://skillscope.cn/api/v1/categories/security?page=1&page_size=20"
```

## Leaderboard

Rank skills by downloads, stars, or installs. Optionally filter by category.

```bash
curl "https://skillscope.cn/api/v1/leaderboard?sort=downloads&page=1&page_size=30"
curl "https://skillscope.cn/api/v1/leaderboard?sort=stars&c=coding-ide"
```

Parameters:
- `sort`: `downloads` (default), `stars`, or `installs`
- `c`: category filter (optional)
- `page`, `page_size`: pagination

## Author Profile

Get author info and all their published skills.

```bash
curl "https://skillscope.cn/api/v1/authors/steipete"
```

## Similar Skills

Find skills similar to a given skill (vector similarity).

```bash
curl "https://skillscope.cn/api/v1/similar/steipete/weather?top_k=5"
```

## Starter Kits

Curated skill bundles for common scenarios (30 kits across 6 categories).

List all kits:

```bash
curl "https://skillscope.cn/api/v1/starter-kits"
```

Get a specific kit with full skill details:

```bash
curl "https://skillscope.cn/api/v1/starter-kits/essential"
```

Available kits include: `essential`, `daily-efficiency`, `meeting-notes`, `email-master`, `fullstack-dev`, `security-audit`, and more.

## Guide Articles

Browse curated guide articles and category top-lists.

```bash
curl "https://skillscope.cn/api/v1/articles?category=top-list&page=1"
curl "https://skillscope.cn/api/v1/articles/top-security"
```

## Response Format

All endpoints return JSON. Example search response:

```json
{
  "query": "web search",
  "results": [
    {
      "id": "arun-8687/tavily-search",
      "name": "tavily",
      "author": "arun-8687",
      "description_zh": "AI优化的网络搜索，返回精准摘要结果。",
      "description_en": "AI-optimized web search via Tavily API.",
      "categories": ["search-research", "ai-llm"],
      "security_grade": "B",
      "quality_score": 8.5,
      "downloads": 12580,
      "stars": 45
    }
  ],
  "total": 1
}
```

## Rate Limits

| Tier | Per Minute | Per Day |
|------|-----------|---------|
| Anonymous (no key) | 20 | 200 |
| Free API Key | 60 | 5,000 |

Rate limit info is included in the `X-RateLimit-Policy` response header. When limited, the API returns HTTP 429 with a `Retry-After` header.

## Notes

- All data is read-only; there are no write endpoints
- Security grades: A (safe) / B (limited external access) / C (review needed) / D (risky)
- Quality scores range from 0 to 10
- Skill IDs use `author/name` format (e.g. `steipete/weather`)
- Chat and deep-research endpoints are not available via the public API
