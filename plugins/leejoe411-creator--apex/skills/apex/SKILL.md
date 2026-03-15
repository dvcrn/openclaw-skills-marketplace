---
name: apex
description: "APEX Binary Trader"
---

# APEX — Binary Trading Agent

## What I do
APEX is an intelligent binary options trading agent for Kalshi 15-minute crypto markets.
I scan BTC, ETH, SOL, and XRP markets every 15 minutes, analyze signals, consult AI, and place trades.

## Commands
| Command | Description |
|---------|-------------|
| `python3 {baseDir}/scripts/apex.py` | Run one full scan + trade cycle |
| `python3 {baseDir}/scripts/apex.py --status` | Show balance, P&L, open positions |
| `python3 {baseDir}/scripts/apex.py --log` | Show recent trade log |

## How APEX trades
1. Scans Kalshi 15-min binary markets (KXBTC15M, KXETH15M, KXSOL15M, KXXRP15M)
2. Pulls RSI, momentum, volume from Coinbase
3. Votes on direction (UP/DOWN) — needs 3/4 signals aligned
4. GPT-4o-mini confirms trade, picks YES/NO, sizes position
5. Places limit order on Kalshi
6. Judges results when markets resolve

## Environment Variables
- `KALSHI_API_KEY_ID` — Kalshi API key UUID
- `KALSHI_PRIVATE_KEY_PATH` — Path to RSA private key PEM
- `OPENAI_API_KEY` — OpenAI API key
- `TELEGRAM_BOT_TOKEN` — Telegram bot token
- `TELEGRAM_CHAT_ID` — Telegram chat ID

## Market knowledge
- 15-min markets open at :00, :15, :30, :45 every hour
- Markets resolve based on CF Benchmarks BRTI price
- YES = price higher at expiry, NO = price lower
- Best entry window: 8-14 minutes before expiry
- Avoid trading when RSI is 45-55 (choppy/unclear)