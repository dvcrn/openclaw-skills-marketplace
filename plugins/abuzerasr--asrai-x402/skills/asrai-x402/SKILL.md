---
name: asrai-x402
description: "Crypto market analysis using Asrai API. Covers technical analysis, screeners, sentiment, forecasting, smart money, Elliott Wave, cashflow, DEX data, and AI-powered insights. Each API call costs $0.005 USDC from your own wallet on Base mainnet via x402."
---

# Asrai — Crypto Analysis via x402

## Install

```bash
npx -y -p asrai-mcp install-skill
```

Auto-detects OpenClaw, Cursor, Cline, and other agents. Then set your key:

```
ASRAI_PRIVATE_KEY=0x<your_private_key>  # add to ~/.env
```

For MCP agents (Cursor, Cline, Claude Desktop) also add to config:

```json
{
  "mcpServers": {
    "asrai": { "command": "npx", "args": ["-y", "asrai-mcp"] }
  }
}
```

---

Use Asrai tools when the user asks about crypto prices, market analysis, trading signals, sentiment, or investment advice.

## When to use

- Crypto price / chart / technical analysis → use asrai tools
- Market sentiment, CBBI, fear/greed → use asrai tools
- "What should I buy?" / portfolio advice → use `portfolio` tool
- Elliott Wave, smart money, order blocks → use asrai tools
- DEX data, low-cap tokens → use asrai tools
- General knowledge you already know well → answer directly (costs $0.005 per call)

## How to call

### If asrai MCP tools are available (Cursor, Cline, Claude Desktop)

Call the appropriate MCP tool directly:
```
technical_analysis(symbol, timeframe)
sentiment()
forecast(symbol)
market_overview()
ask_ai(question)
...
```

### If no MCP tool — use bash (OpenClaw and other agents)

Use the same tool names via bash:
```bash
npx -y -p asrai-mcp asrai <tool> [args...]
```

Examples:
```bash
npx -y -p asrai-mcp asrai ask_ai "What is the outlook for BTC today?"
npx -y -p asrai-mcp asrai technical_analysis BTC 4h
npx -y -p asrai-mcp asrai sentiment
npx -y -p asrai-mcp asrai forecast ETH
npx -y -p asrai-mcp asrai market_overview
npx -y -p asrai-mcp asrai coin_info SOL
npx -y -p asrai-mcp asrai portfolio
npx -y -p asrai-mcp asrai indicator_guide ALSAT
```

Requires `ASRAI_PRIVATE_KEY` set in `~/.env` or environment. Payment is signed automatically.

## MCP tools

| Tool | What it does | Cost |
|---|---|---|
| `market_overview` | Full brief: trending, gainers/losers, RSI, screeners, sentiment, cashflow — use for complete reports only | $0.095 (19 calls) |
| `trending` | Currently trending coins | $0.005 |
| `gainers_losers` | Top gainers and losers | $0.005 |
| `top_bottom` | RSI extremes, top/bottom signals, bounce/dip candidates | $0.015 (3 calls) |
| `volume_spikes` | Coins with unusually high volume | $0.005 |
| `high_volume_low_cap` | Low market cap coins with high volume | $0.005 |
| `ath_tracker` | Coins near or at all-time high | $0.005 |
| `dominance` | BTC & altcoin dominance signals | $0.01 (2 calls) |
| `macro` | S&P 500 & Nasdaq signals — global market context | $0.01 (2 calls) |
| `sentiment` | CBBI, CMC sentiment, AI insights, channel news, Galaxy Score, social dominance | $0.03 (6 calls) |
| `late_unlocked_coins` | Post-vesting coins with low remaining selling pressure | $0.005 |
| `trade_signals` | Trade setups: trending movers, bounces, SAR & MACD entries | $0.025 (5 calls) |
| `technical_analysis(symbol, timeframe)` | Signals, ALSAT, SuperALSAT, PSAR, MACD-DEMA, AlphaTrend, TD, SMC, S/R, Elliott Wave, Ichimoku | $0.06 (12 calls) |
| `forecast(symbol)` | AI 3-7 day price prediction | $0.005 |
| `screener(type)` | Find coins by criteria (ichimoku-trend, rsi, vwap, volume, bounce-dip...) | $0.005 |
| `smart_money(symbol, timeframe)` | Order blocks, fair value gaps, support/resistance | $0.01 (2 calls) |
| `elliott_wave(symbol, timeframe)` | Elliott Wave analysis | $0.005 |
| `ichimoku(symbol, timeframe)` | Ichimoku cloud analysis | $0.005 |
| `cashflow(mode, symbol)` | Capital flow data | $0.005 |
| `coin_info(symbol)` | Stats, price, tags, CMC AI + auto DEX data | $0.025–$0.03 (5–6 calls) |
| `dexscreener(contract)` | DEX trading data | $0.005 |
| `chain_tokens(chain, max_mcap)` | Low-cap tokens on a specific chain | $0.005 |
| `portfolio` | Abu's curated model portfolio — investment reference | $0.005 |
| `ask_ai(question)` | AI analyst freeform answer | $0.01 |
| `indicator_guide(name)` | Reference guide for Asrai-specific indicators | FREE |

## Output rules

- Write like an experienced trader explaining to a friend — conversational, confident, direct
- Think like both a trader AND a long-term investor. Default to investor mode. Switch to trader mode only when user asks for entries
- Keep responses 200–400 words. Short lines, breathing room between sections
- Never list raw indicator values — synthesize into plain language verdict
- End with 1 clear action bias: accumulate / wait / avoid — and why
- Never mention tool names, API calls, or payment details in responses

## Cost

$0.005 USDC per call (most tools), $0.01 for `ask_ai`, FREE for `indicator_guide`. Signed from the user's own wallet on Base mainnet. Tell the user if they ask.
