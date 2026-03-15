---
name: sellersprite-product-research
description: "SellerSprite Product Research Skill — Input a keyword or category, automatically fetch market data via SellerSprite API and run AI analysis, output a structured product research report: Blue Ocean Index, competition landscape, entry opportunities, and risk signals. Triggers: product research, sellersprite, amazon product research, blue ocean, keyword research, competitor analysis, market analysis, asin research, amazon fba"
---

# SellerSprite Product Research

> Input a keyword or ASIN, AI automatically calls the SellerSprite API to fetch market data and outputs a structured product research report.

## Prerequisites

Set your SellerSprite API Key (get one at [open.sellersprite.com](https://open.sellersprite.com)):

```bash
export SELLERSPRITE_SECRET_KEY="your-secret-key"
```

Ensure `openclaw` CLI is installed (used for AI analysis):

```bash
which openclaw
```

## Quick Start

```bash
# Basic product research (keyword)
bash ~/.claude/skills/sellersprite-product-research/selection.sh --keyword "wireless earbuds"

# Specify marketplace (default: US)
bash ~/.claude/skills/sellersprite-product-research/selection.sh --keyword "yoga mat" --marketplace UK

# Use a specific AI model
bash ~/.claude/skills/sellersprite-product-research/selection.sh --keyword "phone case" --model claude
bash ~/.claude/skills/sellersprite-product-research/selection.sh --keyword "phone case" --model gemini
bash ~/.claude/skills/sellersprite-product-research/selection.sh --keyword "phone case" --model gpt-5
bash ~/.claude/skills/sellersprite-product-research/selection.sh --keyword "phone case" --model grok

# Use full model ID
bash ~/.claude/skills/sellersprite-product-research/selection.sh --keyword "yoga mat" --model anthropic/claude-opus-4-6

# Analyze a competitor by ASIN
bash ~/.claude/skills/sellersprite-product-research/selection.sh --asin B08N5WRWNW --marketplace US

# Save report to file
bash ~/.claude/skills/sellersprite-product-research/selection.sh --keyword "LED strip" --output report.md
```

## Supported Models

Uses `openclaw` for AI inference. Pass `--model` with a shorthand alias or full model ID:

| Alias | Model |
|---|---|
| `claude` | anthropic/claude-sonnet-4-6 |
| `claude-opus` | anthropic/claude-opus-4-6 |
| `claude-haiku` | anthropic/claude-haiku-4-5 |
| `gemini` | google/gemini-2.5-pro |
| `gemini-flash` | google/gemini-2.5-flash |
| `gpt-4o` | openai/gpt-4o |
| `gpt-5` | openai/gpt-5 |
| `grok` | xai/grok-4 |
| `deepseek` | groq/deepseek-r1-distill-llama-70b |
| `qwen` | groq/qwen/qwen3-32b |
| `mistral` | mistral/mistral-large-latest |

Any full model ID from `openclaw models list --all` is also accepted.

## Sample Output

```
╔══════════════════════════════════════════════════════════════╗
║       SellerSprite Product Research Report                  ║
║  Keyword: wireless earbuds  |  Market: US  |  2026-03-09   ║
╚══════════════════════════════════════════════════════════════╝

📊 Market Overview
──────────────────────────────────────
  Products          1,284
  Avg Monthly Units 456/mo
  Avg Price         $28.50
  Avg Ratings       3,210
  Blue Ocean Index  ████░░░░░░░░░  3.2 / 10

🔴 Risk Signals
══════════════════════════════════════════════
1. High Competition — TOP10 monthly sales concentration 78%
2. Brand Barrier — Anker/JBL hold 35% market share
...

🟢 Opportunity Windows
══════════════════════════════════════════════
1. [Price Gap] $15-$20 range has few competitors but strong search volume
2. [New Product Bonus] New listings grew 42% in last 90 days
...

🎯 Recommended Entry Strategy
══════════════════════════════════════════════
1. Target $15-18 price range, differentiate on sport/waterproof features...

📌 Top Reference Products
──────────────────────────────────────────────
B0XXXXXXXX   2,340/mo   $19.9   4.3★   FBA  ⭐ Best Seller
...
```

## How It Works

```
① Input keyword / ASIN / category
      ↓
② Call SellerSprite API (product research + keyword research)
      ↓
③ Parse market data (sales, price, competition, trends)
      ↓
④ Claude AI deep analysis (Blue Ocean scoring + strategy)
      ↓
⑤ Output structured product research report
```

## Scripts

| File | Description |
|---|---|
| `selection.sh` | Main entry point |
| `fetch.sh` | SellerSprite API data fetching |
| `analyze.sh` | AI analysis and report rendering |

## Marketplace Codes

| Code | Market |
|---|---|
| US | United States |
| UK | United Kingdom |
| DE | Germany |
| JP | Japan |
| CA | Canada |
| FR | France |
| IT | Italy |
| ES | Spain |
| MX | Mexico |
| AU | Australia |

## Notes

- API rate limit: 40 requests/min, max 100 items per request
- Max 2,000 products per query
- Each analysis uses approx 3,000–8,000 tokens ($0.02–$0.05)
- Recommend querying data from the last 1–3 months for freshness
