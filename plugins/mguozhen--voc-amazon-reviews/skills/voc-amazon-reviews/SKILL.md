---
name: voc-amazon-reviews
description: "VOC AI — Amazon Review Intelligence. Input an ASIN, automatically scrape Amazon reviews and run AI analysis. Outputs a structured bilingual report: sentiment breakdown, top pain points, key selling points, and Listing optimization suggestions. Triggers: voc, amazon review analysis, asin analysis, voice of customer, listing optimization, pain points, selling points, review insights, amazon fba, product research"
---

# VOC AI — Amazon Review Intelligence

> Input an ASIN, AI automatically scrapes and deeply analyzes Amazon reviews, outputting a structured bilingual insight report.

## Prerequisites

Ensure the `browser` skill is installed (used for scraping reviews):

```bash
npx skills add browserbase/skills@browser
```

Set your Claude API Key:

```bash
export ANTHROPIC_API_KEY="your-api-key"
```

## Quick Start

```bash
# Basic analysis (scrapes latest 100 reviews by default)
bash ~/.agents/skills/voc-amazon-reviews/voc.sh B08N5WRWNW

# Specify review count
bash ~/.agents/skills/voc-amazon-reviews/voc.sh B08N5WRWNW --limit 200

# Specify marketplace (default: amazon.com)
bash ~/.agents/skills/voc-amazon-reviews/voc.sh B08N5WRWNW --market amazon.co.uk

# Save report to file
bash ~/.agents/skills/voc-amazon-reviews/voc.sh B08N5WRWNW --output report.md
```

## Sample Output

```
╔══════════════════════════════════════════════════════╗
║     VOC AI Analysis Report                          ║
║  ASIN: B08N5WRWNW  |  Reviews Analyzed: 100         ║
║  Market: amazon.com  |  Generated: 2026-03-08        ║
╚══════════════════════════════════════════════════════╝

📊 Sentiment Distribution
  Positive  ████████████░░░░  74%  (74 reviews)
  Neutral   ███░░░░░░░░░░░░░  16%  (16 reviews)
  Negative  ██░░░░░░░░░░░░░░  10%  (10 reviews)

🔴 Top 5 Pain Points
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Short battery life (28 mentions)
   "Battery drained in 2 days, very disappointed"

2. Unstable Bluetooth connection (19 mentions)
   "Bluetooth keeps disconnecting randomly"

🟢 Top 5 Selling Points
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Excellent sound quality (52 mentions)
   "Amazing bass and crystal clear highs for the price"

💡 Listing Optimization Suggestions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. [Title] Add battery capacity (e.g. 800mAh) and playtime hours
   to reduce negative reviews from mismatched expectations.

2. [Images] Add a scene image showing Bluetooth range and include
   pairing instructions in A+ Content.

3. [Bullets] Lead first bullet with sound quality, use authentic
   customer language like "crystal clear" and "deep bass".
```

## How It Works

```
① Input ASIN
      ↓
② browser CLI opens Amazon review pages (with pagination)
      ↓
③ Parse review data (rating, body, date, Verified badge)
      ↓
④ Claude AI deep semantic analysis
      ↓
⑤ Output structured bilingual report
```

## Scripts

| File | Description |
|---|---|
| `voc.sh` | Main entry point |
| `scraper.sh` | Amazon review scraper (based on browser CLI) |
| `analyze.sh` | Claude API analysis script |

## Notes

- Amazon has strong anti-bot measures — configure `BROWSERBASE_API_KEY` for reliable remote browser access
- Each analysis uses approximately 2,000–5,000 Claude API tokens (~$0.01–$0.03)
- Review scraping takes ~5–10 seconds per page; 100 reviews ≈ 1–2 minutes
- Please use responsibly — avoid frequent bulk scraping of the same product

## Resources

- [Amazon Seller Listing Optimization Guide](#)
- [How VOC Data Drives Product Improvement](#)
- [Using Review Data to Outcompete Rivals](#)
