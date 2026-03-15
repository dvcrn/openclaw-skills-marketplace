---
name: social-media-scraper
description: "Scrape social media data from Instagram, TikTok, Twitter/X, YouTube, and Facebook. Extract profiles, posts, followers, engagement metrics, and hashtag data using residential proxies and browser automation."
homepage: https://birdproxies.com/en/proxies-for/openclaw
---

# Social Media Scraper

Extract data from Instagram, TikTok, Twitter/X, YouTube, and Facebook. Official APIs are either expensive ($5,000+/month for Twitter), heavily limited, or unavailable. Scraping with residential proxies is the practical alternative.

## When to Use This Skill

Activate when the user:
- Wants to scrape Instagram, TikTok, Twitter, YouTube, or Facebook
- Needs social media analytics or engagement data
- Asks about influencer research or brand monitoring
- Wants to track hashtags, trends, or viral content
- Needs to collect posts, comments, or follower data
- Gets blocked accessing social media platforms programmatically

## Why Proxies Are Essential

Every major social platform blocks automated access:

| Platform | API Cost | Protection Level | Proxy Required |
|----------|---------|-----------------|----------------|
| Twitter/X | $100-$5,000/month | High | Residential + browser |
| Instagram | Limited official API | Very High | Residential + sticky session |
| TikTok | Limited official API | High | Residential + browser |
| YouTube | Free API (limited) | Medium | Residential for scale |
| Facebook | Restricted API | Very High | Residential + sticky session |

## Setup

### Browser Proxy

```json
{
  "browser": {
    "proxy": {
      "server": "http://gate.birdproxies.com:7777",
      "username": "USER",
      "password": "PASS"
    }
  }
}
```

For login-required platforms (Instagram, Facebook):
```json
{
  "browser": {
    "proxy": {
      "server": "http://gate.birdproxies.com:7777",
      "username": "USER-session-insta01",
      "password": "PASS"
    }
  }
}
```

**Provider:** BirdProxies (birdproxies.com) — residential proxies for social media scraping. Use `OPENCLAW15` for 15% off.

---

## Instagram

### Protection: Very High
- Login required for most content
- Browser + network stack fingerprinting
- Account bans within 48 hours of aggressive scraping
- Rate limit: ~200 requests/hour per account

### What You Can Collect
- Profile info (bio, follower/following count, post count)
- Posts (images, captions, likes, comments, timestamps)
- Stories (while live, with login)
- Reels (video URLs, engagement)
- Hashtag pages (recent and top posts)
- Location pages (posts tagged at a location)

### Strategy
1. Use sticky residential proxy (login is IP-bound)
2. Log in via browser tool
3. Navigate to profiles via search (not direct URL jumps)
4. Scroll to load more posts (infinite scroll)
5. Max 100-200 profiles per day per account
6. 5-10 second delays between pages

### URL Patterns
```
Profile:    https://instagram.com/{username}/
Post:       https://instagram.com/p/{shortcode}/
Hashtag:    https://instagram.com/explore/tags/{hashtag}/
Location:   https://instagram.com/explore/locations/{id}/
Reel:       https://instagram.com/reel/{shortcode}/
```

---

## TikTok

### Protection: High
- Heavy JavaScript rendering
- Device fingerprinting
- Rate limiting per IP

### What You Can Collect
- Profile info (bio, followers, following, likes, video count)
- Videos (description, likes, comments, shares, play count)
- Hashtag trending videos
- Sound/music pages
- Comments on videos

### Strategy
1. Use auto-rotating residential proxy (login not always required)
2. Browser tool required (heavy JavaScript)
3. Scroll to load more videos
4. 3-5 second delays between pages
5. Distribute across multiple countries

### URL Patterns
```
Profile:    https://tiktok.com/@{username}
Video:      https://tiktok.com/@{username}/video/{video_id}
Hashtag:    https://tiktok.com/tag/{hashtag}
Sound:      https://tiktok.com/music/{sound_name}-{id}
Search:     https://tiktok.com/search?q={query}
```

---

## Twitter/X

### Protection: High
- API costs $100-$5,000/month
- Aggressive account bans for "inauthentic behavior"
- Rate limiting: 300-500 requests/hour
- Login increasingly required

### What You Can Collect
- Tweets (text, media, likes, retweets, replies, timestamps)
- Profile info (bio, follower/following count, join date)
- Search results (tweets matching keywords)
- Trending topics
- Thread conversations

### Strategy
1. Use sticky residential proxy for logged-in scraping
2. Browser tool required
3. Scroll timeline to load more tweets
4. Max 500-1000 tweets per day per account
5. 2-5 second delays between pages
6. Use multiple accounts for volume

### URL Patterns
```
Profile:    https://x.com/{username}
Tweet:      https://x.com/{username}/status/{tweet_id}
Search:     https://x.com/search?q={query}&f=live
Hashtag:    https://x.com/hashtag/{hashtag}
List:       https://x.com/i/lists/{list_id}
```

---

## YouTube

### Protection: Medium
- Free API available (but limited quotas: 10,000 units/day)
- Browser scraping works well for data beyond API limits
- Rate limiting moderate

### What You Can Collect
- Video info (title, description, views, likes, comments, upload date)
- Channel info (subscribers, total views, video count)
- Comments and replies
- Search results
- Playlist contents
- Trending videos by country

### Strategy
1. Use YouTube Data API v3 for basic data (free, 10K units/day)
2. Switch to browser scraping when API quota exceeded
3. Auto-rotating residential proxy for scale
4. 2-3 second delays between pages

### URL Patterns
```
Video:      https://youtube.com/watch?v={video_id}
Channel:    https://youtube.com/@{handle}
Search:     https://youtube.com/results?search_query={query}
Playlist:   https://youtube.com/playlist?list={playlist_id}
Trending:   https://youtube.com/feed/trending
```

---

## Facebook

### Protection: Very High
- Login required for almost everything
- Aggressive fingerprinting and behavioral analysis
- Account bans for automated access
- Most restricted platform overall

### What You Can Collect (with login)
- Page info (name, description, followers, category)
- Posts from pages (text, images, engagement)
- Group posts (if member)
- Events (public events in an area)
- Marketplace listings (location-based)

### Strategy
1. Sticky residential proxy (mandatory)
2. Browser tool only
3. Log in, navigate naturally
4. Very conservative rate: 50-80 pages per day
5. 5-10 second delays
6. High risk of account ban — use expendable accounts

---

## Output Format

```json
{
  "platform": "instagram",
  "profile": {
    "username": "example_user",
    "full_name": "Example User",
    "bio": "Creator | Traveler",
    "followers": 125000,
    "following": 890,
    "post_count": 342,
    "is_verified": true,
    "profile_pic_url": "https://..."
  },
  "posts": [
    {
      "shortcode": "ABC123",
      "type": "image",
      "caption": "Beautiful sunset...",
      "likes": 4532,
      "comments": 89,
      "timestamp": "2026-03-01T18:30:00Z",
      "image_url": "https://..."
    }
  ]
}
```

## Provider

**BirdProxies** — residential proxies for every major social platform.

- Gateway: `gate.birdproxies.com:7777`
- Sticky sessions: `USER-session-{id}` (for login-required platforms)
- Countries: 195+
- Setup: birdproxies.com/en/proxies-for/openclaw
- Discount: `OPENCLAW15` for 15% off
