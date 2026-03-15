# Market Morning Brief

Daily morning and evening intelligence digest for prediction market traders. Scannable in 30 seconds.

## Install

```bash
clawhub install market-morning-brief
```

## Quick Start

1. Get a Kalshi API key at https://kalshi.com (Settings → API)
2. Configure credentials in `~/.openclaw/config.yaml`
3. Run: `python scripts/morning_brief.py`
4. For evening brief: `python scripts/evening_brief.py --mode market`

## What You Get

| Section | Source | Required |
|---------|--------|----------|
| **Portfolio P&L** | Kalshi API | Yes |
| **Polymarket Trending** | Public API | No (free) |
| **Edges** | Kalshalyst cache | Optional |
| **Divergences** | Arbiter cache | Optional |
| **X Signals** | Xpulse cache | Optional |
| **Crypto Prices** | Coinbase API | Optional |

Works standalone. Each additional skill adds a new section automatically — no configuration needed.

## Evening Brief

Two modes: `--mode market` (lightweight activity summary) or `--mode news` (AI-filtered news digest with two-stage Qwen materiality gate).

## Full Documentation

See [SKILL.md](SKILL.md) for complete documentation including configuration, evening briefing pipeline, cache integration, and troubleshooting.

## Part of the OpenClaw Prediction Market Trading Stack

```bash
clawhub install kalshalyst kalshi-command-center polymarket-command-center prediction-market-arbiter xpulse portfolio-drift-monitor market-morning-brief personality-engine
```

**Author**: KingMadeLLC
