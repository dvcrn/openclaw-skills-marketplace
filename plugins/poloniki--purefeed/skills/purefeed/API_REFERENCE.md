# Purefeed API Reference

**Base URL:** `https://www.purefeed.ai/api/v1`
**Auth header:** `Authorization: Bearer $PUREFEED_API_KEY`

All endpoints return `{ "data": ..., "error": null }` on success. Streaming endpoints return `text/plain`.

## Table of Contents

- [Account](#account)
- [Feed & Discovery](#feed--discovery)
- [Folders](#folders)
- [Signals](#signals)
- [Content Studio](#content-studio)
- [Response Shapes](#response-shapes)

---

## Account

**GET /auth/me** — verify API key. Returns `id`, `email`, `created_at`.

```bash
curl -s https://www.purefeed.ai/api/v1/auth/me \
  -H "Authorization: Bearer $PUREFEED_API_KEY"
```

---

## Feed & Discovery

**GET /feed** — tweets ranked by signal relevance.

| Param | Type | Description |
|-------|------|-------------|
| limit | int | Max tweets to return |
| search | string | Full-text search filter |
| signal_ids | string | Comma-separated signal IDs |

```bash
curl -s "https://www.purefeed.ai/api/v1/feed?limit=10&search=AI&signal_ids=1,2" \
  -H "Authorization: Bearer $PUREFEED_API_KEY"
```

Per-tweet fields: `tweet_id`, `creation_date`, `views`, `replies`, `retweets`, `screen_name`, `profile_image_url`, `rest_id`, `notification_date`, `text_similarity`, `semantic_similarity`, `combined_rank`, `tags`, `signals[]` (each with `signal_name`, `content`, `sentiment`, `industry_category`, `content_type`, `color`).

---

**POST /search** — full-text search across signal-matched tweets.

Body: `{ "query": string, "limit"?: int }`

```bash
curl -s https://www.purefeed.ai/api/v1/search \
  -X POST \
  -H "Authorization: Bearer $PUREFEED_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "AI breakthroughs this week", "limit": 10}'
```

---

**GET /feed/signals** — AI signal analysis for specific tweets.

| Param | Type | Description |
|-------|------|-------------|
| tweet_ids | string (required) | Comma-separated tweet IDs |

Returns: `tweet_id`, `signal_name`, `content`, `sentiment`, `industry_category`.

```bash
curl -s "https://www.purefeed.ai/api/v1/feed/signals?tweet_ids=123,456,789" \
  -H "Authorization: Bearer $PUREFEED_API_KEY"
```

---

## Folders

**GET /folders** — list bookmark folders. Returns `id`, `name`, `created_at`.

```bash
curl -s https://www.purefeed.ai/api/v1/folders \
  -H "Authorization: Bearer $PUREFEED_API_KEY"
```

---

**GET /folders/:id/tweets** — tweets in a folder.

| Param | Type | Description |
|-------|------|-------------|
| limit | int | Max tweets to return |

Returns `tweet_id` and nested `tweets` object with `tweet_id`, `full_text`, `creation_date`, `favorites`, `retweets`, `views`.

Note: Folder tweets use `favorites` instead of `replies`.

```bash
curl -s "https://www.purefeed.ai/api/v1/folders/FOLDER_ID/tweets?limit=20" \
  -H "Authorization: Bearer $PUREFEED_API_KEY"
```

---

## Signals

**GET /signals** — list signals.

| Param | Type | Description |
|-------|------|-------------|
| search | string | Semantic search on names/descriptions (vector embeddings) |
| active | string | `"true"` to return only active signals |

Active signal: `signals_subscriptions` is non-empty. Inactive: `signals_subscriptions` is `[]`.

```bash
curl -s "https://www.purefeed.ai/api/v1/signals?search=artificial+intelligence&active=true" \
  -H "Authorization: Bearer $PUREFEED_API_KEY"
```

---

**POST /signals** — create and auto-activate a signal.

Body:
```json
{
  "name": "AI Research",
  "description": "Papers and breakthroughs in artificial intelligence",
  "tags": ["ai", "research"],
  "color": "Blue",
  "cron": "0 9 * * *",
  "timezone": "America/New_York"
}
```

- `color` — one of: `Gray`, `Red`, `Green`, `Blue`, `Yellow`, `Orange`, `Purple`, `Pink`. Default `"Blue"`. Pick a thematic color (Green for sustainability, Red for alerts, Purple for creative, etc.).
- `tags` — organizational tags. Always include 1-3 relevant tags.
- `cron` — default `"0 */6 * * *"`. Use `"* * * * *"` for realtime.
- `timezone` — IANA format, default `"UTC"`.
- `include_keywords` — **Do NOT set unless the user explicitly asks.** Keywords are very restrictive — they require exact word matches and will miss relevant tweets. Default to omitting this field.
- `exclude_keywords` — terms to filter out noise. Only set if user specifies.
- Signal auto-activates. Takes up to 6 hours to process existing tweets.

Response: `{ "data": { "id": 42, "active": true, "schedule_id": "sched_..." } }`

---

**GET /signals/:id** — signal details including `notifications_settings` (color, cron, timezone, keywords).

```bash
curl -s https://www.purefeed.ai/api/v1/signals/SIGNAL_ID \
  -H "Authorization: Bearer $PUREFEED_API_KEY"
```

---

**PUT /signals/:id** — update signal.

Body: `{ "name"?: string, "description"?: string, "cron"?: string, "timezone"?: string }`

If the signal is active, the schedule updates automatically.

```bash
curl -s https://www.purefeed.ai/api/v1/signals/SIGNAL_ID \
  -X PUT \
  -H "Authorization: Bearer $PUREFEED_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name", "cron": "0 5 * * 4", "timezone": "Europe/Madrid"}'
```

---

**DELETE /signals/:id** — permanently delete (irreversible).

```bash
curl -s https://www.purefeed.ai/api/v1/signals/SIGNAL_ID \
  -X DELETE \
  -H "Authorization: Bearer $PUREFEED_API_KEY"
```

---

**GET /signals/:id/matches** — tweets matching a signal.

| Param | Type | Description |
|-------|------|-------------|
| limit | int | Max matches to return |

```bash
curl -s "https://www.purefeed.ai/api/v1/signals/SIGNAL_ID/matches?limit=10" \
  -H "Authorization: Bearer $PUREFEED_API_KEY"
```

---

## Content Studio

**GET /styles** — list writing styles. Returns `id`, `name`, `instructions`, `is_default`. Call before generating.

```bash
curl -s https://www.purefeed.ai/api/v1/styles \
  -H "Authorization: Bearer $PUREFEED_API_KEY"
```

---

**POST /studio/generate** — generate tweet/thread (streaming). Requires `styleId` + `tweetIds` or `ideaPrompt` (or both).

Body: `{ "styleId": int, "tweetIds"?: string[], "ideaPrompt"?: string, "includeOriginal"?: boolean }`

```bash
curl -s https://www.purefeed.ai/api/v1/studio/generate \
  -X POST \
  -H "Authorization: Bearer $PUREFEED_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"tweetIds": ["123", "456"], "styleId": 3}'
```

---

**POST /studio/humanize** — AI detection score + rewrite (streaming).

Body: `{ "posts": string[] }`

Response: First line is JSON `{"score": N, "reasons": "..."}`. If score > 30, remaining lines are the rewrite.

```bash
curl -s https://www.purefeed.ai/api/v1/studio/humanize \
  -X POST \
  -H "Authorization: Bearer $PUREFEED_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"posts": ["Your draft tweet text here"]}'
```

---

**POST /studio/publish** — publish to X immediately (requires Typefully).

Body: `{ "posts": string[] }` — multiple strings = thread.

```bash
curl -s https://www.purefeed.ai/api/v1/studio/publish \
  -X POST \
  -H "Authorization: Bearer $PUREFEED_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"posts": ["Final tweet text"]}'
```

---

**POST /studio/schedule** — schedule for specific time (requires Typefully).

Body: `{ "posts": string[], "scheduled_at": "ISO 8601 datetime" }`

```bash
curl -s https://www.purefeed.ai/api/v1/studio/schedule \
  -X POST \
  -H "Authorization: Bearer $PUREFEED_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"posts": ["Scheduled tweet"], "scheduled_at": "2026-03-15T14:00:00Z"}'
```

---

**POST /studio/draft** — save as Typefully draft.

Body: `{ "posts": string[] }`

```bash
curl -s https://www.purefeed.ai/api/v1/studio/draft \
  -X POST \
  -H "Authorization: Bearer $PUREFEED_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"posts": ["Draft tweet"]}'
```

---

**POST /studio/queue** — add to next posting slot. Works without Typefully (falls back to 1 hour from now).

Body: `{ "posts": string[] }`

```bash
curl -s https://www.purefeed.ai/api/v1/studio/queue \
  -X POST \
  -H "Authorization: Bearer $PUREFEED_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"posts": ["Queued tweet"]}'
```

---

## Response Shapes

### Feed / Search
```json
{
  "data": {
    "data": [
      {
        "tweet_id": "1234567890",
        "creation_date": "2026-03-10T14:30:00",
        "views": 5200,
        "replies": 12,
        "retweets": 45,
        "screen_name": "elonmusk",
        "profile_image_url": "https://...",
        "rest_id": "1234567890",
        "tags": ["ai"],
        "signals": [
          {
            "notification_id": 12345,
            "signal_id": 236,
            "signal_name": "Tech Announcements",
            "content": "Tweet text content...",
            "color": "Green",
            "sentiment": "Positive",
            "industry_category": "Technology & Software",
            "content_type": "News"
          }
        ]
      }
    ],
    "pagination": {
      "pageSize": 20,
      "hasMore": true,
      "nextCursor": { "creation_date": "...", "tweet_id": "...", "combined_rank": 0 }
    }
  }
}
```

Note: Feed/search responses are wrapped in `data.data` (outer from API envelope, inner from pagination).

### Signal List
```json
{
  "data": [
    {
      "id": 42,
      "user_signal_name": "AI Research",
      "signal_description": "Papers and breakthroughs in AI",
      "creation_date": "2026-03-01T10:00:00Z",
      "signals_subscriptions": [{ "id": 1, "schedule_id": "sched_abc123" }],
      "notifications_settings": {
        "color": "#6366f1",
        "cron": "0 9 * * *",
        "timezone": "America/New_York",
        "include_keywords": ["paper"],
        "exclude_keywords": ["crypto"]
      }
    }
  ]
}
```

### Humanize Response (score > 30)
```
{"score":68,"reasons":"Repetitive structure, formal tone"}
Here's a more natural version...
```

### Humanize Response (score ≤ 30)
```json
{ "data": { "score": 22, "reasons": "Natural phrasing", "rewrite": null } }
```
