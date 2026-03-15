---
name: moltstreet
description: "Daily AI signals for 52 ETFs — direction, confidence, target price, reasoning chain. Free, no API key."
homepage: https://moltstreet.com
---

# MoltStreet — AI ETF Market Signals

Daily AI-generated market signals for 52 ETFs. Free, no API key needed.

## When to use this skill

Activate when the user:
- Asks about ETF market outlook, direction, or trading signals
- Mentions any of the 52 covered ETFs by ticker (SPY, QQQ, XLK, GLD, etc.)
- Asks "should I buy/sell [ETF]" or "what's the market doing today"
- Wants sector comparison, portfolio analysis, or market sentiment
- Asks about bullish/bearish signals or price targets

## How to fetch signals

Single ETF signal:
```bash
curl -s https://moltstreet.com/api/v1/etf/SPY
```

List all available symbols (returns catalog, not signal data):
```bash
curl -s https://moltstreet.com/api/v1/etf/
```
This returns `{"symbols": ["ASHR","DBA","DIA",...], "count": 52, ...}`. To get actual signals, fetch each symbol individually.

Multiple ETFs — fetch each one:
```bash
for sym in SPY QQQ DIA IWM; do
  curl -s "https://moltstreet.com/api/v1/etf/$sym"
done
```

## How to interpret and present

1. **Fetch** the signal for the requested ETF(s)
2. **Interpret** direction: `1` = bullish, `-1` = bearish, `0` = neutral
3. **Present** as: "[SYMBOL] is **{direction}** with {confidence * 100}% confidence — target ${target_price} ({expected_move_pct}% move)"
4. **Add context** from `human_readable_explanation` — plain-English AI analysis
5. **Show conviction** from `committee.votes` — 4 independent AI analysts voted
6. **Warn** with `risk_controls` — what could invalidate the signal

## Example agent interaction

User: "What's the outlook for tech stocks?"
→ Fetch XLK, QQQ, SOXX, SMH signals (4 calls)
→ Synthesize: "Tech sector is mixed — QQQ bearish (-1.2%, 85% conf) while SMH is bullish (+2.1%, 78% conf). The divergence is driven by..."
→ Add risk factors and committee consensus

User: "Any strong signals today?"
→ Fetch a representative set: SPY, QQQ, XLK, XLE, XLF, GLD, TLT, EEM, FXI (9 calls)
→ Present the highest-confidence signals with direction and reasoning

## Response fields

| Field | Type | Description |
|-------|------|-------------|
| `direction` | -1, 0, 1 | bearish, neutral, bullish |
| `confidence` | 0.0–1.0 | signal confidence level |
| `target_price` | number | predicted target price |
| `expected_move_pct` | number | expected % move |
| `human_readable_explanation` | string | plain-English analysis |
| `decision_chain` | array | step-by-step reasoning |
| `committee.votes` | array | 4 independent analyst opinions |
| `committee.consensus_strength` | number | consensus level 0–100 |
| `risk_controls` | array | what could invalidate the call |
| `source_urls` | array | research sources used |

## ETF coverage (52 total)

- **US Broad**: SPY QQQ DIA IWM
- **Sectors**: XLK XLF XLE XLV XLI XLC XLY XLP XLB XLRE XLU
- **Thematic**: SOXX SMH ARKK XBI ITB ITA TAN
- **International**: EFA EEM FXI INDA EWZ EWJ VEA VGK MCHI EWY EWG EIDO EPHE THD VNM
- **Fixed Income**: TLT IEF TIP HYG LQD
- **Commodities**: GLD SLV USO DBA IBIT

## Related skills

- **moltstreet-spy** — focused on US market indices (SPY/QQQ/DIA/IWM)
- **moltstreet-sectors** — 11 SPDR sector ETFs for rotation analysis
- **moltstreet-portfolio** — cross-asset portfolio analysis
- **moltstreet-alerts** — high-conviction signals only
- **moltstreet-news** — news-driven market narratives with source links

## Limits

- Signals update once daily (~07:00 UTC). Not real-time quotes.
- ETFs only. Individual stocks not yet covered.
- AI-generated analysis. Not financial advice.

## Example response

```json
{
  "symbol": "SPY",
  "direction": -1,
  "confidence": 0.85,
  "target_price": 565,
  "expected_move_pct": -1.19,
  "human_readable_explanation": "The SPY ETF faces bearish pressure from...",
  "committee": {
    "votes": [
      {"fellow": "fellow-1", "direction": "bearish", "confidence": 75, "target_price": 565},
      {"fellow": "fellow-2", "direction": "bearish", "confidence": 80, "target_price": 560},
      {"fellow": "fellow-3", "direction": "bearish", "confidence": 70, "target_price": 568},
      {"fellow": "fellow-4", "direction": "bullish", "confidence": 55, "target_price": 580}
    ],
    "consensus_strength": 90
  },
  "risk_controls": ["Fed policy reversal could invalidate bearish thesis"]
}
```
