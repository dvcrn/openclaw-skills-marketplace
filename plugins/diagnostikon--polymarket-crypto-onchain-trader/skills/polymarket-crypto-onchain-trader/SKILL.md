---
name: polymarket-crypto-onchain-trader
description: "Trades Polymarket prediction markets on Bitcoin, Ethereum, Solana price milestones, ETF inflows, halving events, and DeFi protocol milestones using on-chain data as the primary signal. Use when you want to capture alpha by combining Polymarket probability with live blockchain metrics."
---

# Crypto & On-Chain Trader

> **This is a template.**
> The default signal is keyword-based market discovery combined with probability-extreme detection — remix it with the data sources listed in the Edge Thesis below.
> The skill handles all the plumbing (market discovery, trade execution, safeguards). Your agent provides the alpha.

## Strategy Overview

On-chain data leads price action by 2-12h. Remix: Glassnode free tier (SOPR, NUPL, exchange flows), CoinGlass ETF flow tracker, Dune Analytics dashboards, Arkham Intelligence wallet tracking.


## Edge Thesis

Crypto markets have the most sophisticated on-chain data infrastructure of any asset class — and Polymarket's retail participants rarely use it:

- **Exchange inflow/outflow**: Large BTC withdrawals from exchanges precede price rises. Large inflows precede selling pressure. Glassnode publishes 24h delayed data for free
- **ETF flow data**: BlackRock/Fidelity BTC ETF daily inflows are published by CoinGlass before Polymarket reprices price-threshold markets
- **Fear & Greed Index**: Extreme fear (<20) and extreme greed (>80) are historically mean-reverting — markets at extremes are systemically mispriced
- **Funding rates**: Perpetual swap funding rates on Binance/Bybit signal over-leveraged positioning. Extreme positive funding → long squeeze likely → fade YES on price targets

### Remix Signal Ideas
- **Glassnode**: https://glassnode.com/ (free tier available)
- **CoinGlass ETF flows**: https://www.coinglass.com/bitcoin-etf
- **Alternative.me Fear & Greed**: https://api.alternative.me/fng/
- **Dune Analytics**: https://dune.com/ — custom on-chain SQL queries


## Safety & Execution Mode

**The skill defaults to paper trading (`venue="sim"`). Real trades only with `--live` flag.**

| Scenario | Mode | Financial risk |
|---|---|---|
| `python trader.py` | Paper (sim) | None |
| Cron / automaton | Paper (sim) | None |
| `python trader.py --live` | Live (polymarket) | Real USDC |

`autostart: false` and `cron: null` — nothing runs automatically until you configure it in Simmer UI.

## Required Credentials

| Variable | Required | Notes |
|---|---|---|
| `SIMMER_API_KEY` | Yes | Trading authority. Treat as high-value credential. |

## Tunables (Risk Parameters)

All declared as `tunables` in `clawhub.json` and adjustable from the Simmer UI.

| Variable | Default | Purpose |
|---|---|---|
| `SIMMER_MAX_POSITION` | See clawhub.json | Max USDC per trade |
| `SIMMER_MIN_VOLUME` | See clawhub.json | Min market volume filter |
| `SIMMER_MAX_SPREAD` | See clawhub.json | Max bid-ask spread |
| `SIMMER_MIN_DAYS` | See clawhub.json | Min days until resolution |
| `SIMMER_MAX_POSITIONS` | See clawhub.json | Max concurrent open positions |

## Dependency

`simmer-sdk` by Simmer Markets (SpartanLabsXyz)
- PyPI: https://pypi.org/project/simmer-sdk/
- GitHub: https://github.com/SpartanLabsXyz/simmer-sdk
