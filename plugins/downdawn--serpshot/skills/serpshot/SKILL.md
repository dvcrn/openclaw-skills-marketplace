---
name: serpshot
description: "Use Serpshot Google Search API to perform web searches and image searches. Use when user needs to search Google for information, research topics, or get search results. Supports up to 100 queries per request, various locations and languages."
---

# Skill: Serpshot Google Search API

Perform Google searches using Serpshot API.

## When to Use

- User asks to "search", "google", "查一下", "调研" something
- Need to get web search results for a topic
- Need image search results

## Tools

- `exec` - Run Python to call Serpshot API

## How to Use

### Basic Search

```python
import requests
import json
import os

# Get API key - YOU MUST ASK USER FOR API KEY
api_key = os.environ.get("SERPSHOT_API_KEY", "YOUR_API_KEY")

url = "https://api.serpshot.com/api/search/google"

headers = {
    "X-API-Key": api_key,
    "Content-Type": "application/json"
}

payload = {
    "queries": ["your search query here"],
    "type": "search",  # or "image"
    "num": 10,  # results per page (1-100)
    "page": 1,
    "location": "US",  # US, CN, JP, GB, DE, etc.
    "lr": "en",  # language restriction
    "gl": "us"  # geolocation
}

response = requests.post(url, headers=headers, json=payload)
data = response.json()

# Parse results
for result in data.get("data", {}).get("results", []):
    print(f"{result['position']}. {result['title']}")
    print(f"   {result['link']}")
    print(f"   {result['snippet']}")
    print()
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| queries | array[string] | Yes | Search queries (max 100) |
| type | string | No | "search" or "image", default: "search" |
| num | integer | No | Results per page (1-100), default: 10 |
| page | integer | No | Page number, default: 1 |
| location | string | No | Country code (US, CN, JP, GB, DE, etc.), default: US |
| lr | string | No | Language restriction (en, zh-Hans, etc.), default: en |
| gl | string | No | Geolocation (us, cn, etc.), default: us |

### Response Format

```json
{
  "code": 200,
  "msg": "Success",
  "data": {
    "results": [
      {
        "title": "Result Title",
        "link": "https://example.com",
        "snippet": "Result description...",
        "position": 1
      }
    ],
    "total_results": "About 12,300,000 results",
    "search_time": 0.45,
    "credits_used": 1
  }
}
```

## Example Tasks

### Task 1: Search for AI news
```
queries: ["AI news 2026"]
location: "US"
num: 5
```

### Task 2: Search Chinese results
```
queries: ["人工智能 最新消息"]
location: "CN"
lr: "zh-Hans"
gl: "cn"
num: 10
```

### Task 3: Image search
```
queries: ["cute cats"]
type: "image"
num: 10
```

## Important Notes

1. **API Key Required**: You MUST ask the user for their Serpshot API key before using this skill
2. **Credits**: Each search uses credits (check with /api/credit/available-credits)
3. **Rate Limit**: Contact Serpshot for rate limits
4. **Locations**: Available locations include US, CN, JP, GB, DE, CA, FR, ID, MX, SG, etc.

## Error Handling

Common error codes:
- 400: Bad request (invalid parameters)
- 401: Invalid API key
- 402: Insufficient credits
- 429: Rate limit exceeded

Check `data["code"]` and `data["msg"]` in response.
