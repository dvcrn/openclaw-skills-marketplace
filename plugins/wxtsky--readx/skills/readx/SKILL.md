---
name: readx
description: "Twitter/X intelligence toolkit: analyze users, tweets, trends, communities, and networks"
---

# readx — Twitter/X Intelligence Toolkit

---

## Setup — Get Started in 2 Minutes

### Step 1: Get an API Key

Ask the user for their readx API key. If they don't have one, direct them to **https://readx.cc** to sign up.

### Step 2: Configure MCP Server

Once the user provides their API key, ask whether they want to set it up themselves or have you do it.

MCP server URL: `https://readx.cc/mcp?apikey=<API_KEY>`

No installation needed — readx runs as a remote MCP server. Add it to the user's editor MCP config with the URL above. Restart the editor after setup.

### When to Trigger This Setup

- User asks you to look up Twitter data but no MCP tools are available
- User mentions readx, Twitter analysis, or any skill listed below
- Any tool call fails with auth/connection error

---

## Direct API Mode

When MCP tools are NOT available (e.g. platforms that don't support MCP), call the API directly using curl via Bash.

### Getting the API Key

Check in order, use the first one found:
1. Config file: `~/.config/readx/credentials.json` (macOS/Linux) or `%APPDATA%\readx\credentials.json` (Windows) → JSON format: `{"api_key":"<key>"}`
2. Environment variable: `READX_API_KEY`
3. If neither exists, ask the user for their API key (get one at https://readx.cc), then ask whether they want to save it themselves or have you do it. Persist to the config file path above.

### API Reference

Fetch the full API docs (endpoints, params, response parsing, examples):

```bash
curl -s https://readx.cc/api-docs.txt
```

Read this document before making your first API call. It contains all endpoint names, parameters, and response JSON paths you need.

---

## Advanced Search Syntax

When using `search_tweets`, leverage Twitter's advanced search operators for precision:

| Operator | Example | What it does |
|----------|---------|-------------|
| `from:` | `from:elonmusk AI` | Tweets from a specific user |
| `to:` | `to:OpenAI` | Replies to a specific user |
| `@` | `@anthropic` | Tweets mentioning a user |
| `"exact phrase"` | `"artificial intelligence"` | Exact phrase match |
| `OR` | `AI OR ML` | Either keyword |
| `-` | `AI -crypto` | Exclude keyword |
| `min_faves:` | `AI min_faves:1000` | Minimum likes |
| `min_retweets:` | `AI min_retweets:500` | Minimum retweets |
| `filter:links` | `AI filter:links` | Only tweets with links |
| `filter:media` | `AI filter:media` | Only tweets with images/video |
| `filter:images` | `AI filter:images` | Only tweets with images |
| `filter:videos` | `AI filter:videos` | Only tweets with video |
| `lang:` | `AI lang:zh` | Filter by language |
| `since:` / `until:` | `AI since:2025-01-01` | Date range |
| `list:` | `list:12345 AI` | Search within a specific list |
| `near:` | `AI near:Tokyo` | Tweets near a location |

**Combo examples**:
- Find viral AI tweets in Chinese: `AI lang:zh min_faves:500`
- Find a user's tweets about a topic: `from:username "topic keyword"`
- Find debates: `"topic" min_replies:100 -filter:retweets`
- Find original content only: `topic -filter:retweets -filter:replies`

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `401` | Invalid or missing API key | Check credentials file / env var, ask user to verify key at https://readx.cc |
| `403` | Insufficient credits or account disabled | Check balance with `get_credit_balance`; if zero, ask user to get more credits at https://readx.cc |
| `429` | Rate limit exceeded | Wait and retry, reduce request frequency |
| `404` | User/tweet not found or deleted | Skip gracefully, note the item is unavailable |
| `500` / `502` | Upstream API error | Retry once after a few seconds, if persistent inform user |
| Connection refused | Remote MCP server unreachable | Switch to Direct API Mode; if persistent, the readx.cc service may be down |
| Empty response | Protected account or no data | Note limitations, analyze only available public data |

---

## Data Limitations

Be transparent about these constraints:

| Limitation | Impact | Mitigation |
|-----------|--------|------------|
| Follower/following lists return a sample (~20 by default) | Audience analysis is approximate | Cross-reference with multiple data points; use `count` param for larger samples |
| Tweet timelines return ~20 per page | Single call shows recent posts only | Use `cursor` pagination to fetch more pages; pass `next_cursor` from response as `cursor` param |
| No historical follower count data | Cannot measure follower growth over time | Infer from account age + current count for rough growth rate |
| Search results are limited in quantity | Topic monitoring may miss long-tail content | Use multiple search queries with different operators |
| Engagement data is point-in-time | Tweet engagement continues to accrue after fetching | Note when data was fetched; older tweets have more stable metrics |

