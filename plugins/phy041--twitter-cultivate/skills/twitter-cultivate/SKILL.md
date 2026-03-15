---
name: twitter-cultivate
description: "Twitter account health check, growth strategy, and engagement optimization"
---

# Twitter Account Cultivation Skill

Systematic approach to growing Twitter presence based on the open-source algorithm analysis. Check account health, find engagement opportunities, optimize content strategy.

---

## Prerequisites

- **rnet** installed (`pip install "rnet>=3.0.0rc20" --pre`)
- **rnet_twitter.py** — lightweight GraphQL client (https://github.com/PHY041/rnet-twitter-client)
- **Twitter cookies** exported to path specified by `TWITTER_COOKIES_PATH` env var
  Format: `[{"name": "auth_token", "value": "..."}, {"name": "ct0", "value": "..."}]`

### Getting Cookies

1. Open Chrome -> go to `x.com` -> log in
2. DevTools -> Application -> Cookies -> `https://x.com`
3. Copy `auth_token` and `ct0` values
4. Save as JSON. Cookies last ~2 weeks. Refresh when you get 403 errors.

---

## Core Metrics to Track

| Metric | Healthy Range | Impact |
|--------|---------------|--------|
| Following/Follower Ratio | **< 0.6** | TweepCred score |
| Avg Views/Tweet | 20-40% of followers | Algorithm favor |
| Media Tweet % | **> 50%** | 10x engagement |
| Link Tweet % | **< 20%** | Avoid algorithm penalty |
| Reply Rate | Reply to 100% of comments | +75 weight boost |

---

## Workflow: Full Health Check

### Step 1: Analyze Account

```python
import asyncio, os
from rnet_twitter import RnetTwitterClient

async def analyze(username: str):
    client = RnetTwitterClient()
    cookies_path = os.environ.get("TWITTER_COOKIES_PATH", "twitter_cookies.json")
    client.load_cookies(cookies_path)

    user = await client.get_user_by_screen_name(username)
    followers = user.get("followers_count", 0)
    following = user.get("friends_count", 0)
    ratio = following / max(followers, 1)

    tweets = await client.get_user_tweets(user["rest_id"], count=20)

    return {
        "username": username,
        "followers": followers,
        "following": following,
        "ratio": round(ratio, 2),
        "tweet_count": user.get("statuses_count", 0),
        "recent_tweets": len(tweets),
    }
```

### Step 2: Check Shadowban Status

Manual check: [shadowban.yuzurisa.com](https://shadowban.yuzurisa.com)

### Step 3: Analyze Following List

Recommends accounts to unfollow based on:
- No tweets in 90+ days (inactive)
- Never interacted with you (no value)
- Low follower count + high following (likely bots)
- No mutual engagement

### Step 4: Find Engagement Opportunities

```python
async def find_opportunities(niche_keywords: list[str]):
    client = RnetTwitterClient()
    cookies_path = os.environ.get("TWITTER_COOKIES_PATH", "twitter_cookies.json")
    client.load_cookies(cookies_path)

    opportunities = []
    for keyword in niche_keywords:
        tweets = await client.search_tweets(
            f"{keyword} lang:en -filter:replies",
            count=50, product="Top"
        )
        for t in tweets:
            if t["favorite_count"] >= 50 and t["reply_count"] < 20:
                opportunities.append(t)

    return sorted(opportunities, key=lambda t: t["favorite_count"], reverse=True)
```

---

## Account Health Scoring (TweepCred)

Based on Twitter's open-source algorithm:

```
Score = PageRank x (1 / max(1, following/followers))
```

| Ratio | Estimated TweepCred | Algorithm Treatment |
|-------|---------------------|---------------------|
| < 0.6 | 65+ (healthy) | All tweets considered |
| 0.6 - 2.0 | 40-65 | Limited consideration |
| 2.0 - 5.0 | 20-40 | Severe penalty |
| > 5.0 | < 20 | **Only 3 tweets max** |

---

## Unfollow Strategy

### Priority Order
1. **Inactive Accounts** — No tweets in 90+ days
2. **Non-Engagers** — Never liked/replied to your tweets
3. **Low-Value Follows** — High following/low followers (bot-like)

### Execution Plan
```
Week 1: Unfollow 30 inactive accounts
Week 2: Unfollow 30 non-engagers
Week 3: Unfollow 30 low-value follows
Week 4: Evaluate ratio improvement
```

---

## Content Strategy (Algorithm-Optimized)

### Tweet Types by Algorithm Weight

| Type | Weight | Recommendation |
|------|--------|----------------|
| Tweet that gets author reply | **+75** | ALWAYS reply to comments |
| Tweet with replies | +13.5 | Ask questions |
| Tweet with profile clicks | +12.0 | Be intriguing |
| Tweet with long dwell time | +10.0 | Use threads |
| Retweet | +1.0 | Low value |
| Like | +0.5 | Lowest value |

### Content Mix
- **40%** Value content (insights, tips, frameworks)
- **30%** Engagement bait (questions, polls, hot takes)
- **20%** Build-in-public (progress updates, wins, losses)
- **10%** Promotion (with value attached)

### Media Requirements
Every tweet should have ONE of: Image, Video (< 2:20), Poll, or Thread (7-10 tweets).

---

## Weekly Routine

### Daily (15 min)
- [ ] Post 1-3 tweets with media
- [ ] Reply to ALL comments on your tweets
- [ ] Engage with 5-10 tweets in your niche
- [ ] Check notifications and respond

### Weekly (Saturday)
- [ ] Run full health check
- [ ] Review what content performed best
- [ ] Unfollow 10-20 low-value accounts
- [ ] Plan next week's content themes

### Monthly
- [ ] Full ratio review (target < 2.0)
- [ ] Shadowban check
- [ ] Content audit (media %, link %)
- [ ] Milestone check (follower goals)
