# Elfa API v2 — Full Endpoint Reference

Base URL: `https://api.elfa.ai`
Auth header: `x-elfa-api-key: <your-key>`
**Version:** v2 (current)

**Getting an API key:** Sign up at https://go.elfa.ai/claude-skills to get a free key
with 1,000 credits. Most endpoints are available on the free tier. The following require
a Pay-As-You-Go or Grow plan: trending narratives and AI chat.
Full plan details at https://go.elfa.ai/claude-skills.

---

## 1. API Key Status

**GET** `/v2/key-status`

Returns your key's tier, usage, limits, and remaining requests.

Response fields:
- `id`, `key`, `name`, `status` (active | revoked | expired | payment_required)
- `tier` — your plan tier
- `usage` — `{ monthly, daily }` current request counts
- `limits` — `{ monthly, daily }` maximum requests
- `remainingRequests` — `{ monthly, daily }`
- `requestsPerMinute` — rate limit (nullable)
- `isExpired` — boolean
- `expiresAt`, `createdAt`, `updatedAt`
- `allowOverage`, `maxOverage` — overage settings (nullable)

---

## 2. Trending Tokens

**GET** `/v2/aggregations/trending-tokens`

*Experimental — behavior may change without notice.*

Returns tokens ranked by mention count over a time period.

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `timeWindow` | string | No | `"7d"` | e.g., "30m", "1h", "4h", "24h", "7d", "30d" |
| `from` | number | No | — | Start date (unix timestamp). Overrides timeWindow. |
| `to` | number | No | — | End date (unix timestamp). Use with `from`. |
| `page` | number | No | 1 | Page number |
| `pageSize` | number | No | 50 | Items per page |
| `minMentions` | number | No | 5 | Minimum mentions threshold |

Response data array items:
```json
{ "token": "SOL", "current_count": 1234, "previous_count": 800, "change_percent": 54.25 }
```

---

## 3. Account Smart Stats

**GET** `/v2/account/smart-stats`

*Experimental — behavior may change without notice.*

Returns smart follower/engagement stats for a Twitter/X account.

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `username` | string | **Yes** | — | Twitter/X username |

Response:
```json
{
  "success": true,
  "data": {
    "followerCount": 50000,
    "smartFollowerCount": 1200,
    "averageReach": 25000,
    "averageEngagement": 450,
    "smartFollowingCount": 300
  }
}
```

Note: `followerCount` and `smartFollowerCount` may be absent in some responses.

---

## 4. Top Mentions

**GET** `/v2/data/top-mentions`

Returns highest-engagement mentions for a ticker symbol, ranked by relevance.

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `ticker` | string | **Yes** | — | Ticker symbol. Prefix with `$` for cashtag-only matches. |
| `timeWindow` | string | No | `"1h"` | e.g., "1h", "24h", "7d" |
| `from` | number | No | — | Start date (unix timestamp) |
| `to` | number | No | — | End date (unix timestamp) |
| `page` | number | No | 1 | Page number |
| `pageSize` | number | No | 10 | Items per page |
| `reposts` | boolean | No | — | Include reposts |

Response data is an array of Mention objects:
```json
{
  "tweetId": "1234567890",
  "link": "https://x.com/user/status/1234567890",
  "likeCount": 150,
  "repostCount": 45,
  "viewCount": 12000,
  "quoteCount": 5,
  "replyCount": 23,
  "bookmarkCount": 8,
  "mentionedAt": "2025-03-01T12:00:00Z",
  "type": "post",
  "repostBreakdown": { "ct": 30, "smart": 15 },
  "account": { "isVerified": true, "username": "cryptotrader" }
}
```

The `type` field can be: `post`, `repost`, `quote`, `reply`.

**Note:** This endpoint returns tweet IDs and engagement metrics but does **not** include
the tweet text content. To retrieve the actual tweet content, you'll need to use Twitter/X's
API (e.g., the GET `/tweets` endpoint) with your own X API key, using the `tweetId` values
from Elfa's response.

---

## 5. Keyword Mentions

**GET** `/v2/data/keyword-mentions`

Search mentions by keywords and/or account name. Uses cursor-based pagination.

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `keywords` | string | No* | — | Up to 5 keywords, comma-separated |
| `accountName` | string | No* | — | Filter by account username |
| `timeWindow` | string | No | `"7d"` | Time window |
| `from` | number | No | — | Start date (unix timestamp) |
| `to` | number | No | — | End date (unix timestamp) |
| `limit` | number | No | 20 | Results to return (max 30) |
| `searchType` | string | No | — | `"and"` or `"or"` for keyword matching |
| `cursor` | string | No | — | Cursor for pagination |
| `reposts` | boolean | No | — | Include reposts |

*At least one of `keywords` or `accountName` is required.

Response metadata includes `cursor` (for next page) and `total`.

**Note:** Like Top Mentions, this endpoint returns tweet IDs and engagement metrics but
does **not** include tweet text content. You'll need your own X API key to fetch tweet
content using the returned `tweetId` values.

---

## 6. Event Summary

**GET** `/v2/data/event-summary`

AI-generated event summaries from keyword mentions. **Costs 5 credits.**

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `keywords` | string | **Yes** | — | Keywords, comma-separated |
| `from` | number | No | — | Start date (unix timestamp) |
| `to` | number | No | — | End date (unix timestamp) |
| `timeWindow` | string | No | `"7d"` | e.g., "30m", "1h", "4h", "24h", "7d", "30d" |
| `searchType` | string | No | `"or"` | `"and"` or `"or"` |

Response data is an array of summaries:
```json
{
  "summary": "Major developments in Solana ecosystem...",
  "tweetIds": ["123", "456"],
  "sourceLinks": ["https://x.com/..."]
}
```

Response metadata: `summaries` (count), `total_summarized`, `total`.

---

## 7. Trending Narratives

**GET** `/v2/data/trending-narratives`

Trending narrative clusters from Twitter/X analysis. **Costs 5 credits.**

*Requires Pay-As-You-Go or Grow plan (not available on free tier).*

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `timeFrame` | string | No | `"day"` | `"day"` or `"week"` |
| `maxNarratives` | number | No | 7 | Max narratives to return (1–20) |
| `maxTweetsPerNarrative` | number | No | 5 | Max tweets per narrative (1–20) |

Response:
```json
{
  "success": true,
  "data": {
    "metadata": { "total_tweets": 5000, "total_narratives": 12 },
    "trending_narratives": [
      {
        "narrative": "Bitcoin ETF inflows reach record highs...",
        "tweet_ids": ["123", "456"],
        "source_links": ["https://x.com/..."]
      }
    ]
  }
}
```

---

## 8. Token News

**GET** `/v2/data/token-news`

Token-related news mentions.

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `timeWindow` | string | No | `"7d"` | Time window |
| `from` | number | No | — | Start date (unix timestamp) |
| `to` | number | No | — | End date (unix timestamp) |
| `page` | number | No | 1 | Page number |
| `pageSize` | number | No | 20 | Items per page |
| `coinIds` | string | No | — | CoinGecko Coin IDs, comma-separated |
| `reposts` | boolean | No | — | Include reposts |

Response data is an array of Mention objects (same schema as Top Mentions).

---

## 9. Trending Contract Addresses — Twitter

**GET** `/v2/aggregations/trending-cas/twitter`

Trending contract addresses mentioned on Twitter/X.

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `timeWindow` | string | No | `"7d"` | e.g., "30m", "1h", "4h", "24h", "7d", "30d" |
| `from` | number | No | — | Start date (unix timestamp) |
| `to` | number | No | — | End date (unix timestamp) |
| `page` | number | No | 1 | Page number |
| `pageSize` | number | No | 50 | Items per page |
| `minMentions` | number | No | 5 | Minimum mentions |

Response data array items:
```json
{ "contractAddress": "0xabc...", "chain": "ethereum", "mentionCount": 234 }
```

`chain` is either `"ethereum"` or `"solana"`.

---

## 10. Trending Contract Addresses — Telegram

**GET** `/v2/aggregations/trending-cas/telegram`

Same parameters and response schema as the Twitter version (endpoint 10), but for Telegram mentions.

---

## 11. AI Chat

**POST** `/v2/chat`

Send a message to Elfa AI for market analysis. Supports multiple analysis types and multi-turn sessions.

*Requires Pay-As-You-Go or Grow plan (not available on free tier).*

**Request body (JSON):**

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `message` | string | Conditional | — | User message. Required for `chat` type. |
| `sessionId` | string | No | — | Omit for new conversation. Pass from previous response to continue. |
| `analysisType` | string | No | `"chat"` | See analysis types below. |
| `speed` | string | No | `"expert"` | `"fast"` or `"expert"` |
| `assetMetadata` | object | Conditional | — | Required for token/account analysis types. |

**Analysis types and their requirements:**

| Type | `message` | `assetMetadata` | Description |
|---|---|---|---|
| `chat` | Required | — | General conversational AI |
| `macro` | Optional | — | Macro market overview |
| `summary` | Optional | — | Quick market summary |
| `tokenIntro` | — | `symbol` OR `chain`+`contractAddress` | Token introduction |
| `tokenAnalysis` | — | `symbol` OR `chain`+`contractAddress` | In-depth token trade setup |
| `accountAnalysis` | — | `username` | Twitter/X account analysis |

**`assetMetadata` fields:**

| Field | Type | Description |
|---|---|---|
| `symbol` | string | Token ticker, e.g., `"BTC"`, `"$ETH"` |
| `chain` | string | Blockchain name, e.g., `"ethereum"`, `"solana"` |
| `contractAddress` | string | Token contract address |
| `username` | string | Twitter/X username (for accountAnalysis) |

**Response:**
```json
{
  "success": true,
  "data": {
    "creditsConsumed": 1,
    "sessionId": "abc-123",
    "message": "Here is the market analysis..."
  }
}
```

Save `sessionId` to continue the conversation in subsequent requests.

---

## Token Insights (v1 — Legacy)

**GET** `/v1/token-insights`

| Param | Type | Required | Default | Description |
|---|---|---|---|---|
| `coinId` | string | No | — | CoinGecko coin ID |
| `limit` | number | No | 10 | Results limit |
| `offset` | number | No | 0 | Pagination offset |

Response includes insights with `title`, `description`, `sentiment`, `timestamp`, `link`,
and `supportingTweets` array.

*Note: v1 endpoints are legacy. Prefer v2 endpoints for new integrations.*
