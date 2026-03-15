---
name: purefeed
description: "Monitors Twitter/X feeds with AI signal detection. Searches tweets semantically, manages signal detectors, generates human-sounding posts, checks AI detection scores, and publishes/schedules content to X via Typefully. Use when the user wants to browse their Twitter feed, find tweets about a topic, set up content monitoring, draft tweets from curated content, or publish to X/Twitter. Do NOT use for general Twitter browsing without a Purefeed account."
---

# Purefeed

**API Base:** `https://www.purefeed.ai/api/v1`
**Auth:** `Authorization: Bearer $PUREFEED_API_KEY`

## Output Rules

Follow these rules for EVERY response that includes tweet data:

1. Format ALL screen names as clickable links: `[@screen_name](https://x.com/screen_name)`. Never output plain `@screen_name`.
2. Format ALL tweet references as clickable links: `[Tweet](https://x.com/screen_name/status/tweet_id)`.
3. Include view count with eye emoji: `👁 81K`.
4. Sort by views or engagement descending unless user requests otherwise.

Example output line:
```
[@CryptoAyor](https://x.com/CryptoAyor) 👁 81K — detailed thread about $JELLY manipulation
```

## Setup

1. Get API key at **purefeed.ai/profile** → **Public API Keys** → **Create Key**
2. Set it: `openclaw config set skills.purefeed.env.PUREFEED_API_KEY "pf_live_YOUR_KEY"`
3. Verify: `curl -s https://www.purefeed.ai/api/v1/auth/me -H "Authorization: Bearer $PUREFEED_API_KEY"`

## Tool Dependencies

```
list styles ──→ styleId ──→ generate post
list signals ──→ signal_id ──→ get/update/delete signal, get signal matches
list folders ──→ folder_id ──→ get/create/rename/delete folder, add/remove tweets
get feed / search / signal matches ──→ tweet_ids ──→ generate post / get signal insights
generate post ──→ draft text ──→ humanize post ──→ publish / schedule / draft / queue
```

Always list styles before generating a post. Always list signals before signal-specific calls.

## How to Find Tweets by Topic

**Follow this exact sequence when the user asks "what's new about X?" or "find tweets about Y".**

### Step 1 — Find a matching active signal
```
GET /signals?search=TOPIC&active=true
```
The `search` parameter uses semantic/vector search — `search=ai` finds "Artificial intelligence", "AI Research", etc. If empty, try broader terms or `GET /signals?active=true` to see all active signals.

### Step 2 — Get matches from that signal
```
GET /signals/{id}/matches?limit=20
```
Signal matches are the primary data source. They include AI-generated analysis (sentiment, category, insights). Do NOT skip to feed search.

### Step 3 — Fall back to feed search ONLY if no signal found
```
GET /feed?limit=20&search=TOPIC
POST /search → {"query": "topic description", "limit": 20}
```

### Step 4 — Filter feed by signal IDs (optional)
```
GET /feed?signal_ids=236,237&limit=20
```

## Workflows

### Find and share tweets
1. Find tweets using the strategy above
2. `GET /styles` — pick a writing style
3. `POST /studio/generate` — generate post from tweet IDs + styleId
4. `POST /studio/humanize` — if score ≤ 30 use as-is, if > 30 use rewrite
5. `POST /studio/publish` — publish to X

### Set up monitoring
1. `POST /signals` — create signal with name + description + tags + color + cron + timezone (auto-activates)
2. Wait up to 6 hours for processing
3. `GET /signals/{id}/matches` — check results
4. `PUT /signals/{id}` — refine description if too many irrelevant matches

### First run
1. `GET /auth/me` — verify API key
2. `GET /styles` — cache writing styles
3. `GET /signals` — see signal configurations
4. `GET /folders` — see bookmark folders

## Key Concepts

- **Signal**: AI content detector with a name + description. Active if `signals_subscriptions` is non-empty; inactive if `[]`. When creating: always set `tags` and `color`, never set `include_keywords` unless user explicitly asks (they are very restrictive).
- **Writing Style**: Named instruction set for post generation. Must call `GET /styles` to get valid `styleId` before generating.
- **Typefully**: Publishing backend. Required for publish/schedule/draft/queue. If not connected, tell user to set it up in Purefeed settings.

## Error Handling

| Error | Agent Action |
|-------|-------------|
| 401 Unauthorized | Tell user to create new key at purefeed.ai/profile |
| 429 Too Many Requests | Wait and retry. Check `Retry-After` header |
| "No Typefully connection" | Tell user to connect Typefully in Purefeed settings |
| "No LLM API keys configured" | Tell user to add LLM API keys in Studio settings |
| "Writing style not found" | Call `GET /styles` to get valid IDs |
| "Signal not found" | Call `GET /signals` to get valid IDs |

## API Reference

Read `API_REFERENCE.md` for full endpoint documentation, parameters, curl examples, and response shapes.

All endpoints return `{ "data": ..., "error": null }` on success and `{ "data": null, "error": { "message": "...", "code": "..." } }` on error. Streaming endpoints return `text/plain`.

### Endpoint Summary

| Method | Path | Purpose |
|--------|------|---------|
| GET | /auth/me | Verify API key |
| GET | /feed | Tweets ranked by signal relevance |
| POST | /search | Full-text search across matched tweets |
| GET | /feed/signals | AI signal analysis for specific tweet IDs |
| GET | /folders | List bookmark folders |
| POST | /folders | Create a folder (`{ "name": "..." }`) |
| PATCH | /folders/:id | Rename a folder (`{ "name": "..." }`) |
| DELETE | /folders/:id | Delete a folder and its items |
| GET | /folders/:id/tweets | Tweets in a folder |
| POST | /folders/:id/tweets | Add tweet to folder (`{ "tweet_id": "..." }`) |
| DELETE | /folders/:id/tweets?tweet_id=X | Remove tweet from folder |
| GET | /signals | List signals (supports semantic search) |
| POST | /signals | Create + auto-activate a signal |
| GET | /signals/:id | Signal details |
| PUT | /signals/:id | Update signal |
| DELETE | /signals/:id | Delete signal (irreversible) |
| GET | /signals/:id/matches | Tweets matching a signal |
| GET | /styles | List writing styles |
| POST | /studio/generate | Generate tweet/thread (streaming) |
| POST | /studio/humanize | AI detection score + rewrite (streaming) |
| POST | /studio/publish | Publish to X immediately |
| POST | /studio/schedule | Schedule for specific time |
| POST | /studio/draft | Save as Typefully draft |
| POST | /studio/queue | Add to next posting slot |

## Rate Limits

- 60 requests/minute per API key
- Streaming endpoints count as 1 request each
- 429 responses include `Retry-After` header
