---
name: Crypto News Feed
description: "Aggregate crypto news from RSS feeds, filter by keywords, score sentiment, and generate daily digest HTML reports."
---

# Crypto News Feed 📰

> Your personalized crypto news aggregator with sentiment analysis.

## Quick Reference Card

### Commands at a Glance

| Command | Usage | Output |
|---------|-------|--------|
| `fetch` | `bash scripts/crypto-news-feed.sh fetch` | Fetch latest from all sources |
| `filter` | `bash scripts/crypto-news-feed.sh filter --keywords "bitcoin,ETF"` | Filter by keywords |
| `digest` | `bash scripts/crypto-news-feed.sh digest --date today` | Generate daily HTML digest |
| `sentiment` | `bash scripts/crypto-news-feed.sh sentiment --keyword "ethereum"` | Sentiment score for topic |
| `sources` | `bash scripts/crypto-news-feed.sh sources` | List configured RSS feeds |
| `add-source` | `bash scripts/crypto-news-feed.sh add-source --url URL --name NAME` | Add new RSS source |
| `trending` | `bash scripts/crypto-news-feed.sh trending` | Show trending topics |

### Default RSS Sources

```
📡 CoinDesk          https://www.coindesk.com/arc/outboundfeeds/rss/
📡 CoinTelegraph     https://cointelegraph.com/rss
📡 The Block         https://www.theblock.co/rss.xml
📡 Decrypt           https://decrypt.co/feed
📡 Bitcoin Magazine   https://bitcoinmagazine.com/feed
📡 Blockworks        https://blockworks.co/feed
📡 DL News           https://www.dlnews.com/rss/
```

### Sentiment Scoring System

```
Score Range    Label         Emoji    Meaning
─────────────────────────────────────────────────
 0.6 to  1.0  Very Bullish  🟢🟢    Strong positive language
 0.2 to  0.6  Bullish       🟢      Positive outlook
-0.2 to  0.2  Neutral       ⚪      Balanced/factual
-0.6 to -0.2  Bearish       🔴      Negative outlook
-1.0 to -0.6  Very Bearish  🔴🔴    Strong negative language
```

### Keyword Categories (Built-in)

- **DeFi:** defi, yield, liquidity, farming, pool, swap, AMM
- **NFT:** nft, opensea, blur, collection, mint, pfp
- **L2:** layer2, rollup, arbitrum, optimism, zksync, base
- **Regulation:** sec, regulation, lawsuit, ban, approve, etf
- **Meme:** meme, doge, shib, pepe, bonk, wif

### Filter Examples

```bash
# DeFi news only
bash scripts/crypto-news-feed.sh filter --category defi

# Multiple keywords
bash scripts/crypto-news-feed.sh filter --keywords "solana,jupiter,jito"

# Bullish news only
bash scripts/crypto-news-feed.sh filter --min-sentiment 0.2

# Last 24 hours, bearish signals
bash scripts/crypto-news-feed.sh filter --hours 24 --max-sentiment -0.2

# Combine filters
bash scripts/crypto-news-feed.sh filter --keywords "bitcoin" --min-sentiment 0.3 --hours 48
```

### Daily Digest Output

The `digest` command generates `crypto-digest-YYYY-MM-DD.html` containing:

1. **📊 Market Sentiment Overview** — Average sentiment across all articles
2. **🔥 Top Stories** — Highest-engagement articles
3. **📈 Trending Topics** — Most mentioned keywords
4. **📰 All Articles** — Full list with sentiment badges
5. **📉 Sentiment Timeline** — Hourly sentiment chart

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEWS_FEED_DIR` | `./crypto-news` | Output directory |
| `NEWS_MAX_AGE` | `72` | Max article age in hours |
| `NEWS_SOURCES_FILE` | `~/.crypto-news-sources.json` | Custom sources config |
| `NEWS_CACHE_TTL` | `1800` | Cache TTL in seconds |

### Automation

```bash
# Add to crontab for daily 8am digest
0 8 * * * cd /path/to/workspace && bash skills/crypto-news-feed/scripts/crypto-news-feed.sh digest --date today
```
