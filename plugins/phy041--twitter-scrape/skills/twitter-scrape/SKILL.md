---
name: twitter-scrape
description: "Scrape Twitter profiles and tweets via GraphQL, export to JSON or database"
---

# Twitter/X Scraper Skill

Scrape Twitter profiles and tweets using the `rnet_twitter.py` GraphQL client. Bypasses Cloudflare via TLS fingerprint emulation. Saves to local JSON and optionally imports to a database.

---

## Prerequisites

```bash
# Install rnet (Rust HTTP client with Chrome TLS emulation)
pip install "rnet>=3.0.0rc20" --pre

# Required:
# 1. rnet_twitter.py — async Twitter GraphQL client
#    Get it: https://github.com/PHY041/rnet-twitter-client
# 2. Twitter cookies file (set TWITTER_COOKIES_PATH env var)
#    Format: [{"name": "auth_token", "value": "..."}, {"name": "ct0", "value": "..."}]
```

### Getting Cookies

1. Open Chrome -> go to `x.com` -> log in
2. DevTools (F12) -> Application -> Cookies -> `https://x.com`
3. Copy `auth_token` and `ct0` values
4. Save to JSON file. Cookies expire ~2 weeks.

---

## Quick Usage

### Scrape a Twitter User

```python
import asyncio, json, os
from rnet_twitter import RnetTwitterClient

async def scrape_user(username: str, limit: int = 200):
    client = RnetTwitterClient()
    cookies_path = os.environ.get("TWITTER_COOKIES_PATH", "twitter_cookies.json")
    client.load_cookies(cookies_path)

    # Get user profile
    user = await client.get_user_by_screen_name(username)

    # Get tweets
    tweets = await client.get_user_tweets(user["rest_id"], count=limit)

    # Save to JSON
    output = {
        "scraped_at": datetime.now().isoformat(),
        "profile": {
            "id": user["rest_id"],
            "username": username,
            "name": user.get("name", ""),
            "bio": user.get("description", ""),
            "followers_count": user.get("followers_count", 0),
            "following_count": user.get("friends_count", 0),
        },
        "tweets": tweets,
        "tweets_count": len(tweets),
    }

    output_path = f"storage/twitter/{username}.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    return output_path

# Usage
asyncio.run(scrape_user("elonmusk", limit=200))
```

---

## Output Format

```json
{
  "scraped_at": "2026-01-22T10:30:00",
  "profile": {
    "id": "123456789",
    "username": "example",
    "name": "Example User",
    "bio": "...",
    "followers_count": 1234567,
    "following_count": 1234
  },
  "tweets": [
    {
      "id": "1234567890123456789",
      "text": "Tweet content...",
      "created_at": "Thu Jan 22 16:45:03 +0000 2026",
      "likes": 12345,
      "retweets": 1234,
      "replies": 567,
      "views": 1234567,
      "url": "https://x.com/example/status/1234567890123456789",
      "is_retweet": false
    }
  ],
  "tweets_count": 200
}
```

---

## Optional: Database Import

To import scraped tweets into a PostgreSQL/Supabase database:

```sql
CREATE TABLE twitter_content (
  id TEXT PRIMARY KEY,
  username TEXT NOT NULL,
  text TEXT,
  created_at TIMESTAMPTZ,
  likes INTEGER DEFAULT 0,
  retweets INTEGER DEFAULT 0,
  replies INTEGER DEFAULT 0,
  views BIGINT,
  url TEXT,
  is_retweet BOOLEAN DEFAULT FALSE,
  imported_at TIMESTAMPTZ DEFAULT NOW()
);
```

```python
from supabase import create_client
import os

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

# Import from scraped JSON
import json
data = json.load(open("storage/twitter/example.json"))
for tweet in data["tweets"]:
    supabase.table("twitter_content").upsert({
        "id": tweet["id"],
        "username": data["profile"]["username"],
        "text": tweet["text"],
        "likes": tweet.get("likes", 0),
        "retweets": tweet.get("retweets", 0),
        "replies": tweet.get("replies", 0),
        "views": tweet.get("views"),
        "url": tweet.get("url"),
        "is_retweet": tweet.get("is_retweet", False),
    }).execute()
```

---

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| 403 Forbidden | Cookies expired | Refresh auth_token + ct0 from Chrome |
| 404 Not Found | GraphQL ID rotated | Re-extract from `abs.twimg.com/.../main.*.js` |
| User not found | Username wrong/suspended | Check on x.com |
| Rate limited | Too many requests | Wait 15 minutes |

---

## Technical Notes

- **SearchTimeline requires POST** (GET returns 404)
- **GraphQL endpoint IDs may rotate** — re-extract from Twitter's JS bundle
- **Rate limits**: ~300 requests/15min window
- Uses `Emulation.Chrome133` to bypass Cloudflare detection
