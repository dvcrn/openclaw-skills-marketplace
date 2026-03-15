---
name: tweetclaw
description: "OpenClaw plugin for X/Twitter automation. Post tweets, reply, like, retweet, follow, DM, search, extract data, run giveaways, monitor accounts via Xquik. 40+ endpoints, 2 tools (explore + tweetclaw), 2 commands (/xstatus, /xtrends), background event poller."
homepage: https://xquik.com
---

# TweetClaw

OpenClaw plugin for X/Twitter automation powered by Xquik. Install via:

```bash
openclaw plugins install @xquik/tweetclaw
```

## Configuration

Set your Xquik API key (get one at [xquik.com/account-manager](https://xquik.com/account-manager)):

```bash
openclaw config set plugins.entries.tweetclaw.config.apiKey 'xq_YOUR_KEY'
```

## Tools

TweetClaw registers 2 tools that cover the entire Xquik API (40+ endpoints):

### `explore` (free, no network)

Search the API spec to find endpoints. No API calls are made.

Example: "What endpoints are available for tweet composition?"

The agent writes an async arrow function that filters the in-memory endpoint catalog:

```javascript
async () => spec.endpoints.filter(e => e.category === 'composition')
```

### `tweetclaw` (execute API calls)

Execute authenticated API calls. Auth is injected automatically.

Example: "Search tweets about AI agents"

```javascript
async () => {
  const results = await xquik.request('/api/v1/x/tweets/search', { query: { q: 'AI agents' } });
  return results;
}
```

## Commands

| Command | Description |
|---------|-------------|
| `/xstatus` | Account info, subscription status, usage |
| `/xtrends` | Trending topics from curated sources |
| `/xtrends tech` | Trending topics filtered by category |

## Event Notifications

When polling is enabled (default), TweetClaw checks for new events every 60 seconds:

- Monitor alerts: new tweets, replies, quotes, retweets from monitored accounts
- Follower changes: gained or lost followers on monitored accounts

## Common Workflows

### Post a tweet

```
You: "Post a tweet saying 'Hello from TweetClaw!'"
Agent uses explore -> finds POST /api/v1/x/tweets
Agent uses tweetclaw -> posts the tweet with auth
```

### Search tweets

```
You: "Search tweets about AI agents"
Agent uses explore -> finds GET /api/v1/x/tweets/search
Agent uses tweetclaw -> calls the endpoint
```

### Run a giveaway draw

```
You: "Pick 3 random winners from replies to this tweet: https://x.com/..."
Agent uses tweetclaw -> creates draw with filters
```

### Monitor an account

```
You: "Monitor @elonmusk for new tweets and follower changes"
Agent uses tweetclaw -> creates monitor with event types
```

### Compose an optimized tweet

```
You: "Compose a tweet about our product launch"
Agent uses tweetclaw -> 3-step compose/refine/score workflow (free)
```

## API Categories

| Category | Examples | Free |
|----------|---------|------|
| Write Actions | Post tweets, reply, like, retweet, follow, DM, update profile | No |
| Media | Upload media, download tweet media | No |
| Twitter | Search tweets, look up users, check follows | No |
| Composition | Compose, refine, score tweets; manage drafts | Yes |
| Styles | Analyze tweet styles, compare, performance | Mixed |
| Extraction | Reply/follower/community extraction (20 tools) | No |
| Draws | Giveaway draws, export results | No |
| Monitoring | Create monitors, view events, webhooks | No |
| Account | API keys, subscription, connected X accounts | Yes |
| Trends | X trending topics, curated radar from 7 sources | Mixed |

## Pricing

Free tier (no subscription): tweet composition, style analysis, drafts, curated radar, account management, integrations.

Subscription ($20/month): write actions, search, media, extractions, draws, monitors, X trending.

When a paid endpoint returns 402, TweetClaw provides a checkout URL.

## When NOT to Use

- Reading tweets in a browser or basic browsing (use a browser skill instead)
- X/Twitter analytics dashboards (TweetClaw returns raw data, not visualizations)
- Scheduling tweets for future posting (Xquik posts immediately)
- Managing X/Twitter ads or promoted content (not supported)
