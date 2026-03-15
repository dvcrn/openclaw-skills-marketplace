# Research Workflows

> All tool names below omit the `mcp__alphafactoryx__` prefix for readability.
> For example, `kline(symbol="AAPL")` means `mcp__alphafactoryx__kline(symbol="AAPL")`.

---

## 1. Individual Stock Research

Comprehensive single-stock deep dive covering fundamentals, filings, sentiment, insider activity, and price action.

1. `analyst_overview(symbol="AAPL")` → analyst ratings, summary, recent articles
2. `analyst_financials(symbol="AAPL")` → financials, estimates, dividends, peer list
3. `analyst_transcripts(symbol="AAPL", limit=4)` → last 4 earnings call transcripts
4. `analyst_transcript(symbol="AAPL", transcript_id="...")` → read latest call for guidance/outlook
5. `filing_overview(symbol="AAPL")` → all SEC filings grouped by form type
6. `filing_latest(symbol="AAPL", form_type="10-K")` → latest annual report full text
7. `filing_filings(symbol="AAPL", form_type="Form 4", limit=20)` → recent insider trades
8. `news_articles(symbol="AAPL")` + `market_news_articles(symbol="AAPL")` → news sentiment from multiple sources
9. `social(symbol="AAPL", limit=30, sort="views")` → top social media posts
10. `kline(symbol="AAPL")` → daily price chart (60 bars)
11. `fred_macro()` → macro backdrop (rates, CPI, employment, VIX)

**Conditional:** If `analyst_financials` returns a peer list, repeat steps 1-2 for top peers to build a comparison view.

---

## 2. Sentiment Analysis

Cross-source sentiment triangulation using all available engines and platforms.

1. `news_articles(symbol="AAPL", limit=20)` → multi-engine AI sentiment (Grok, DeepSeek, GPT-5 nano)
2. `market_news_articles(symbol="AAPL", limit=20)` → per-ticker AI sentiment insights with reasoning
3. `social(symbol="AAPL", limit=50, sort="views")` → top tweets by engagement
4. `social_posts(symbol="AAPL", since="2026-02-01", until="2026-03-08", min_views=1000)` → recent high-visibility posts with date filter
5. `social_threads(symbol="AAPL", limit=10)` → full conversation threads with reply chains

**Cross-source comparison:**

6. Compare sentiment polarity across the 3 StockNews engines (Grok vs DeepSeek vs GPT-5) — divergence signals uncertainty
7. Compare news sentiment (steps 1-2) vs social sentiment (steps 3-5) — divergence can indicate retail vs institutional disconnect

**Temporal comparison (current vs prior period):**

8. `social_posts(symbol="AAPL", since="2025-12-01", until="2025-12-31", min_views=1000)` → prior period social sentiment
9. Compare current period (step 4) vs prior period (step 8) — detect sentiment shift direction
10. `kline(symbol="AAPL", limit=120)` → overlay price action with sentiment shift timing

---

## 3. Macro Analysis

Top-down macro context with concrete series-to-sector mappings and yield curve analysis.

1. `fred_macro()` → all 25 latest macro indicators for a full dashboard (this serves as the series discovery step — note the series IDs returned for use in step 2)
2. `fred_macro(series_id="FEDFUNDS")` → specific indicator time series (60 data points)

**Key series-to-sector pairings:**

| Series | Sector Impact |
|--------|--------------|
| `FEDFUNDS`, `DGS2`, `DGS10` | Rate-sensitive: banks (JPM, BAC), REITs (O, SPG), homebuilders (DHI, LEN) |
| `CPIAUCSL` | Consumer staples (PG, KO) vs discretionary (AMZN, TSLA) |
| `UNRATE`, `PAYEMS` | Retail (WMT, TGT), staffing, consumer spending |
| `GDP`, `INDPRO` | Industrials (CAT, DE), materials (FCX, NEM) |
| `VIXCLS` | Options-heavy names, volatility strategies |
| `DTWEXBGS` (USD index) | Multinationals (AAPL, MSFT) — strong USD = earnings headwind |
| `T10Y2Y` (10Y-2Y spread) | Yield curve slope — inversion signals recession risk |

**Yield curve analysis:**

3. `fred_macro(series_id="DGS2")` → 2-year Treasury yield
4. `fred_macro(series_id="DGS10")` → 10-year Treasury yield
5. `fred_macro(series_id="T10Y2Y")` → 10Y-2Y spread (direct inversion indicator)
6. Compare spread trend vs bank stock performance: `kline(symbol="JPM")`, `kline(symbol="BAC")`

**Conditional:** If VIX > 25, check `news_search(query="volatility spike")` for catalysts.

---

## 4. Deep Search

Cross-source full-text search for themes, events, and insider activity.

1. `filing_search(query="revenue guidance", symbol="AAPL")` → search SEC filings
2. `analyst_search(query="AI chips")` → search Seeking Alpha articles
3. `analyst_transcript_search(query="margin expansion")` → search earnings calls
4. `news_search(query="tariff")` → search news articles
5. `market_news_search(query="FDA approval")` → search Polygon news

**Form 4 insider search:**

6. `filing_search(query="acquisition OR purchase", form="Form 4")` → insider buys across all tickers
7. `filing_search(query="disposition OR sale", symbol="AAPL", form="Form 4")` → insider sells for specific ticker

**Cross-source parallel search pattern** (run for any theme):

8. Pick a theme (e.g., "artificial intelligence"). Run in parallel:
   - `analyst_search(query="artificial intelligence")`
   - `analyst_transcript_search(query="artificial intelligence")`
   - `news_search(query="artificial intelligence")`
   - `market_news_search(query="artificial intelligence")`
   - `filing_search(query="artificial intelligence", form="8-K")`
9. Cross-reference which tickers appear in multiple sources → higher-conviction signals

**Transcript + financials combination:**

10. `analyst_transcript_search(query="guidance raised", symbol="AAPL")` → find where management raised guidance
11. `analyst_financials(symbol="AAPL")` → verify estimates reflect the update
12. `kline(symbol="AAPL")` → price reaction around the guidance change

---

## 5. Insider Trading Analysis

Track Form 4 insider transactions and correlate with price action and news.

1. `filing_filings(symbol="AAPL", form_type="Form 4", limit=50)` → list recent insider trades with accession numbers
2. `filing_text(symbol="AAPL", form_type="Form 4", accession="...")` → read a specific Form 4 for transaction details (shares, price, relationship)
3. `filing_search(query="acquisition OR purchase", symbol="AAPL", form="Form 4")` → find insider buys specifically
4. `filing_search(query="disposition OR sale", symbol="AAPL", form="Form 4")` → find insider sells
5. `kline(symbol="AAPL", limit=120)` → price action spanning the trade dates

**Conditional:** If a cluster of insider buys appears (3+ insiders buying within 2 weeks):

6. `news_search(query="insider buying AAPL")` → check if media has covered the pattern
7. `analyst_search(query="insider AAPL")` → analyst commentary on insider activity
8. `analyst_financials(symbol="AAPL")` → check if buys precede an earnings date

**Conditional:** For cross-company insider screening:

9. `filing_search(query="acquisition", form="Form 4")` → find insider buys across all tickers, note which companies appear

---

## 6. Earnings Call Analysis

Analyze earnings transcripts, compare with estimates, and track post-earnings reaction.

1. `analyst_transcripts(symbol="AAPL", limit=4)` → list last 4 quarterly calls with IDs and dates
2. `analyst_transcript(symbol="AAPL", transcript_id="...")` → read the latest transcript in full
3. `analyst_transcript_search(query="guidance OR outlook", symbol="AAPL")` → extract forward-looking statements
4. `analyst_transcript_search(query="margin OR profitability", symbol="AAPL")` → profitability commentary
5. `analyst_financials(symbol="AAPL")` → estimates vs actuals, revenue/EPS trends
6. `kline(symbol="AAPL", limit=60)` → post-earnings price reaction

**Post-earnings coverage:**

7. `news_articles(symbol="AAPL", limit=20)` → news coverage and AI sentiment after the call
8. `market_news_articles(symbol="AAPL", limit=20)` → additional coverage with per-ticker sentiment reasoning
9. `social(symbol="AAPL", limit=30, sort="views")` → social media reaction

**Conditional:** If guidance was raised/lowered, compare with peer calls:

10. `analyst_financials(symbol="AAPL")` → get peer list from financials
11. `analyst_transcript_search(query="guidance", symbol="PEER")` → check if peers echoed the same trend

---

## 7. Peer Comparison

Side-by-side comparison of a stock against its peers on ratings, financials, price, and sentiment.

1. `analyst_financials(symbol="AAPL")` → get financials + peer list (peers are returned in the response)
2. For each peer: `analyst_overview(symbol=PEER)` → ratings, quant score, Wall Street consensus
3. For each peer: `analyst_financials(symbol=PEER)` → revenue, EPS, estimates for comparison
4. For each peer: `kline(symbol=PEER, limit=120)` → 6-month price performance comparison
5. For each peer: `news_articles(symbol=PEER, limit=5)` → recent sentiment comparison
6. `fred_macro()` → macro context relevant to the sector

**Conditional:** If a peer significantly outperforms/underperforms:

7. `analyst_transcript_search(query="competitive advantage", symbol=PEER)` → what drives the divergence
8. `filing_latest(symbol=PEER, form_type="10-Q")` → latest quarterly filing for detail

---

## 8. News Event Tracking

Track a specific event (FDA approval, M&A, regulation) across tickers and data sources.

1. `news_search(query="FDA approval")` → find event mentions across all tickers
2. `market_news_search(query="FDA approval")` → cross-reference with Polygon news
3. `analyst_search(query="FDA approval")` → analyst coverage of the event
4. `filing_search(query="FDA", form="8-K")` → material event filings (8-K) referencing FDA

**For each affected ticker identified above:**

5. `kline(symbol=TICKER, limit=60)` → price reaction around the event date
6. `social(symbol=TICKER, limit=30, sort="views")` → social media reaction
7. `news_articles(symbol=TICKER, limit=10)` → ongoing news sentiment

**Conditional:** If the event impacts an entire sector:

8. `news_search(query="FDA sector impact")` → broader sector coverage
9. For sector peers: `kline(symbol=PEER)` → check for sympathy moves

---

## 9. Sector Screening

Discover and compare stocks within a sector using search and fundamentals.

1. `analyst_search(query="semiconductor")` → find sector-related articles, note which tickers appear most
2. `news_search(query="semiconductor sector")` → sector news coverage
3. `market_news_search(query="semiconductor")` → additional sector coverage

**For top tickers identified above:**

4. `analyst_overview(symbol=TICKER)` → quant rating, Wall Street rating, SA author rating
5. `analyst_financials(symbol=TICKER)` → revenue growth, margins, estimates
6. `kline(symbol=TICKER, limit=120)` → relative price performance

**Sector macro context:**

7. `fred_macro(series_id="INDPRO")` → industrial production (relevant for manufacturing sectors)
8. `fred_macro(series_id="CPIAUCSL")` → CPI (relevant for consumer sectors)
9. `fred_macro(series_id="FEDFUNDS")` → fed funds rate (relevant for financials, REITs)

**Conditional:** If screening for value plays, sort by lowest quant rating with positive earnings revisions in `analyst_financials`.

---

## 10. Historical Sentiment Trend

Compare social and news sentiment across time periods to detect shifts.

1. `social_posts(symbol="TSLA", since="2026-01-01", until="2026-03-08", min_views=1000)` → current period social sentiment
2. `social_posts(symbol="TSLA", since="2025-10-01", until="2025-12-31", min_views=1000)` → prior period social sentiment
3. `social_threads(symbol="TSLA", limit=20)` → current high-engagement discussion threads
4. `news_articles(symbol="TSLA", limit=20)` → current news sentiment (Grok, DeepSeek, GPT-5)
5. `kline(symbol="TSLA", limit=200)` → extended price history to correlate sentiment shifts with price

**Analysis steps:**

6. Compare sentiment polarity distribution between step 1 (current) vs step 2 (prior) — is sentiment improving or deteriorating?
7. Compare social sentiment (steps 1-3) vs news sentiment (step 4) — divergence signals emerging narrative shifts
8. Overlay sentiment shift timing with price inflection points from step 5

**Conditional:** If a sharp sentiment shift is detected:

9. `analyst_search(query="TSLA", symbol="TSLA")` → check for catalyst articles
10. `filing_search(query="material", symbol="TSLA", form="8-K")` → check for material event filings around the shift date

---

## 11. X/Twitter Social Deep Dive

Deep analysis of social media activity, influential voices, and viral discussions for a ticker.

1. `social(symbol="GME", limit=50, sort="views")` → top viral tweets by view count
2. `social_posts(symbol="GME", min_followers=10000, sort="views")` → posts from influential accounts only
3. `social_posts(symbol="GME", min_views=5000, sort="favorites")` → most-liked high-visibility posts
4. `social_threads(symbol="GME", limit=20)` → full conversation threads with reply chains
5. `news_articles(symbol="GME", limit=20)` → compare social narrative vs mainstream media coverage
6. `kline(symbol="GME", timeframe="hourly", limit=200)` → intraday price action to correlate with social spikes

**Analysis steps:**

7. Identify dominant narratives from step 1-2 — what are the most-viewed posts about?
8. Check if influential accounts (step 2) are leading or following retail sentiment (step 1)
9. Compare social sentiment tone (steps 1-4) vs news sentiment tone (step 5) — divergence may indicate ahead-of-news social signals

**Conditional:** If social volume is spiking:

10. `market_news_articles(symbol="GME")` → check for breaking news driving the spike
11. `filing_search(query="GME", form="8-K")` → check for unreported material events
