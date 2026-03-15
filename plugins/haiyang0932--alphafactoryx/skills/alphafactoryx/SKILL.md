---
name: alphafactoryx
description: "Financial data API for US equity research: SEC EDGAR filings, Seeking Alpha articles/ratings/financials, Stock News sentiment, Polygon News AI insights, X/Twitter sentiment, FRED macro indicators, and OHLCV price data for ~2000 stocks."
---

# AlphaFactoryX

Financial data for US equity research via MCP (Model Context Protocol). Covers SEC EDGAR filings, Seeking Alpha articles/ratings/financials, Stock News sentiment, Polygon News AI insights, X/Twitter sentiment, FRED macro indicators, and OHLCV price data for ~2000 US equities.

## Getting Your MCP Token

Register for a free token (instant, no approval needed) at http://ictree.com — click "GET FREE API KEY".

Or register via API:

```
POST http://data.ictree.com/api/register
Content-Type: application/json
{"name":"Your Name","email":"you@example.com"}
```

The response contains your token. Set it as an environment variable:

```
export ALPHAFACTORYX_MCP_TOKEN="your_token_here"
```

## MCP Server Configuration

Add the AlphaFactoryX MCP server to your `openclaw.json` (or Claude Code `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "alphafactoryx": {
      "type": "streamable-http",
      "url": "http://mcp.ictree.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN"
      }
    }
  }
}
```

Replace `YOUR_TOKEN` with your `ALPHAFACTORYX_MCP_TOKEN` value. Once configured, you have access to 18 financial data tools prefixed with `mcp__alphafactoryx__`.

## How to Use

Call MCP tools directly by name. No curl, no URL construction, no `?format=text`. Parameters have schema validation.

**Check data coverage:**
```
mcp__alphafactoryx__get_archive_stats()
```

**Get SEC filings for a stock:**
```
mcp__alphafactoryx__edgar_overview(symbol="AAPL")
```

**Search across all SEC filings:**
```
mcp__alphafactoryx__edgar_search(query="revenue guidance", symbol="AAPL")
```

**Get macro data:**
```
mcp__alphafactoryx__fred_macro()
```

## MCP Tool Reference

18 tools available:

### Overview

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_archive_stats` | _(none)_ | Database statistics: article/filing counts, symbol counts, date ranges |

### SEC EDGAR

| Tool | Parameters | Description |
|------|-----------|-------------|
| `edgar_overview` | `symbol` | List all filings grouped by form type (10-K, 10-Q, 8-K, Form 4) |
| `edgar_filing` | `symbol`, `form_type`, `accession` | Full text of a specific filing by accession number (50K char limit) |
| `edgar_search` | `query`, `symbol?`, `form?` | Full-text search across filings (up to 25 results) |
| `edgar_latest` | `symbol`, `form_type` | Most recent filing of a given form type (50K char limit) |

### Seeking Alpha

| Tool | Parameters | Description |
|------|-----------|-------------|
| `sa_overview` | `symbol` | Overview: summary, ratings, financials, recent articles |
| `sa_article` | `symbol`, `article_id` | Full article text (10K char limit) |
| `sa_search` | `query`, `symbol?` | Full-text search across articles (up to 25 results) |
| `sa_transcript` | `symbol`, `transcript_id` | Earnings call transcript full text (30K char limit) |
| `sa_financials` | `symbol` | Financials + dividends + estimates + peer companies |
| `sa_transcript_search` | `query`, `symbol?` | Full-text search across earnings call transcripts (up to 25 results) |

### News & Sentiment

| Tool | Parameters | Description |
|------|-----------|-------------|
| `stocknews_articles` | `symbol`, `limit?` (default 20) | Recent news with multi-engine AI sentiment (Grok, DeepSeek, GPT-5) |
| `stocknews_search` | `query`, `symbol?` | Full-text search across news articles |
| `polygon_news_articles` | `symbol`, `limit?` (default 20) | Polygon news with per-ticker AI sentiment insights and reasoning |
| `polygon_news_search` | `query`, `symbol?` | Full-text search across Polygon news |
| `x_sentiment` | `symbol`, `limit?` (default 20), `sort?` (views/date/favorites) | X/Twitter tweets sorted by engagement (max 50) |

### Macro & Price

| Tool | Parameters | Description |
|------|-----------|-------------|
| `fred_macro` | `series_id?` | Without series_id: all 25 latest macro indicators. With series_id: time series (60 points) |
| `kline` | `symbol`, `timeframe?` (daily/hourly/1min), `limit?` (default 60, max 200) | OHLCV price bars |

Parameters marked with `?` are optional.

## Research Workflows

### Individual Stock Research

1. `get_archive_stats` -- check data coverage
2. `edgar_overview(symbol="AAPL")` -- SEC filings list
3. `edgar_latest(symbol="AAPL", form_type="10-K")` -- latest annual report
4. `sa_overview(symbol="AAPL")` -- analyst ratings and financials
5. `stocknews_articles(symbol="AAPL")` + `polygon_news_articles(symbol="AAPL")` -- news sentiment
6. `kline(symbol="AAPL")` -- price chart

### Sentiment Analysis

1. `stocknews_articles(symbol="AAPL")` -- multi-engine AI sentiment (Grok, DeepSeek, GPT-5)
2. `polygon_news_articles(symbol="AAPL")` -- per-ticker AI sentiment insights + reasoning
3. `x_sentiment(symbol="AAPL")` -- social media sentiment
4. Cross-reference multiple sources for higher confidence

### Macro Analysis

1. `fred_macro()` -- all 25 latest indicators (rates, CPI, employment, GDP, VIX)
2. `fred_macro(series_id="FEDFUNDS")` -- specific indicator time series
3. Combine macro context with stock-level data for top-down analysis

### Deep Search

1. `edgar_search(query="revenue guidance", symbol="AAPL")` -- search SEC filings
2. `sa_search(query="AI chips")` -- search Seeking Alpha articles
3. `sa_transcript_search(query="margin expansion")` -- search earnings calls
4. `stocknews_search(query="tariff")` -- search news
5. `polygon_news_search(query="FDA approval")` -- search Polygon news

## Rate Limits

| Limit | Value |
|-------|-------|
| Daily requests | 500 per token |
| Per-second requests | 2 per token |

Exceeding limits returns an error response with details. Contact support for higher limits.

## Error Handling

MCP tool errors return descriptive text messages:

| Error | Meaning | Action |
|-------|---------|--------|
| "No EDGAR filings found for {symbol}" | Symbol not in database | Check symbol spelling; use `get_archive_stats` for coverage |
| "No data available" | Empty result | Data may not be archived yet for this symbol |
| Authentication error | Invalid or missing token | Check `ALPHAFACTORYX_MCP_TOKEN` and MCP server config |
| Rate limit error | Too many requests | Wait and retry; stay within 500/day, 2/sec |

## Best Practices

- **Start with `get_archive_stats`** to understand data coverage before querying specific symbols
- **Cross-reference multiple sources** -- combine EDGAR, SA, news, and price data for comprehensive analysis
- **Use search tools for discovery** -- find content across the entire archive by keyword
- **Check sentiment from multiple engines** -- Stock News includes Grok, DeepSeek, and GPT-5
- **Macro context first** -- check `fred_macro()` before stock-level analysis
- **Use `edgar_latest` for quick reads** -- gets the most recent filing without needing an accession number

## Data Coverage

- ~2,000 US equities (stocks + ETFs)
- SEC EDGAR: 10-K, 10-Q, 8-K filings and Form 4 insider trades (full text)
- Seeking Alpha: articles, earnings call transcripts, ratings, financials, dividends, estimates
- Stock News: articles with Grok + DeepSeek + GPT-5 sentiment
- Polygon News: articles with per-ticker AI sentiment insights and reasoning
- X/Twitter: tweets with engagement metrics for ~50 top stocks
- FRED: 25 macro series (Fed Funds, CPI, GDP, unemployment, VIX, yield curve, etc.)
- OHLCV: daily, hourly, 1-minute bars + 6 futures (ES, NQ, YM, RTY, GC, CL)
