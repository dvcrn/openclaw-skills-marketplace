---
name: gold-price-report
description: "Gold/silver price lookup and market brief via the CNGold/Jijinhao quote source. Use when the user asks things like 查金价, 黄金多少钱, 今日金价, 白银价格, 品牌金价, 老凤祥/周大福/周生生金价, 沪金/沪银/comex黄金/comex白银, or wants a daily/scheduled gold-price report. Returns three panels: related spot products, physical gold brand prices, and precious-metals futures."
---

# Gold Price Report

Use the bundled script to fetch three quote panels from the underlying Jijinhao real-time quote API used by CNGold.

## What this skill returns

- **Related spot products**: 现货黄金、现货白银、现货铂金、现货钯金、中国香港黄金、中国台湾黄金
- **Physical gold brands**: 老凤祥、周大福、周生生、老庙、周六福、六福珠宝、周大生、菜百
- **Precious-metals futures**: 沪金、沪银、comex黄金、comex白银、沪铜

## Default workflow

1. Run `scripts/fetch_gold_panels.py --format md` for a human-readable report.
2. If the user wants structured output, run with `--format json`.
3. If the user wants only one or two panels, use `--sections` with comma-separated values from:
   - `related`
   - `physical`
   - `futures`
4. Summarize in plain Chinese unless the user asks for raw data only.

## Commands

### Markdown report

```bash
python3 skills/gold-price-report/scripts/fetch_gold_panels.py --format md
```

### JSON output

```bash
python3 skills/gold-price-report/scripts/fetch_gold_panels.py --format json
```

### Only selected panels

```bash
python3 skills/gold-price-report/scripts/fetch_gold_panels.py --sections related,physical --format md
```

## Notes

- The source page itself is hard to scrape directly, but the underlying quote API is machine-readable.
- Prices are fetched from `https://api.jijinhao.com/quoteCenter/realTime.htm`.
- For the `related` and `physical` sections, display **latest price**.
- For the `futures` section, display **latest price** and **change percent**.
- If a quote is missing, report it as `----` rather than inventing a value.
- For scheduled reports, prefer the markdown format and a concise summary.
