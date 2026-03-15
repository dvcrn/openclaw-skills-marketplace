---
name: unifai-trading-suite
description: "AI-powered trading insights suite: prediction markets (Polymarket/Kalshi) and social sentiment signals powered by UnifAI."
homepage: https://github.com/zbruceli/trading
---

> Generated note: shared plugin assets for this package live at the plugin root. Common local references were rewritten when they appeared in backticks or markdown links.

# UnifAI Trading Suite

A comprehensive suite for AI-driven trading analysis, aggregating prediction markets and social signals.

## 🛠️ Included Tools

### 1. Prediction Trader
Compare probabilities across Polymarket and Kalshi.
```bash
python3 {baseDir}/skills/prediction-trader/scripts/trader.py analyze "bitcoin"
```

### 2. Kalshi Trader
Regulated US economic indicators (Fed Rates, CPI).
```bash
python3 {baseDir}/skills/kalshi-trader/scripts/kalshi.py fed
```

### 3. Social Signals
Analyze KOL mentions and sentiment via UnifAI.
```bash
python3 {baseDir}/skills/social-signals/scripts/signals.py trending
```

## 🔐 Setup
Requires `UNIFAI_API_KEY` (from unifAI) and `GOOGLE_API_KEY` (for analysis).

## 🚀 Installation
```bash
clawdhub install unifai-trading-suite
```
