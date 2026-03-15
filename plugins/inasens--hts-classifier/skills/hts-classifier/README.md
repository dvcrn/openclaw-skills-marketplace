# hts-classifier

Look up US HTS tariff codes and 2026 duty rates from the command line. Built for OpenClaw agents.

## What it does

Describe a product in plain English (or provide an HTS code) and get back:

- **HTS code** — Harmonized Tariff Schedule classification
- **Base duty rate** — General (MFN) rate
- **Section 301** — Additional duty on Chinese-origin goods
- **Section 232** — Steel/aluminum tariffs
- **Section 122 (IEEPA)** — Universal tariff (15% as of 2026)
- **Total estimated rate** — All duties stacked
- **Trade data** — Import volumes when available

## Usage

```bash
# Search by product description
python3 scripts/classify.py --query "lithium ion batteries"

# Look up a specific HTS code
python3 scripts/classify.py --hts "8507.60"

# Both at once
python3 scripts/classify.py --query "steel pipes" --hts "7304.19"

# Raw JSON (for piping to other tools)
python3 scripts/classify.py --query "solar panels" --raw
```

## Example output

```json
{
  "results": [
    {
      "hts_code": "8541.40.60.00",
      "description": "Photosensitive semiconductor devices...",
      "base_duty": "Free",
      "section_301_china": 25,
      "section_232": 0,
      "section_122": 15,
      "total_estimated": "40%",
      "warnings": ["Section 301 List 3: 25%", "Section 122 universal tariff: 15%"]
    }
  ]
}
```

## Data source

Live data from [ustariffrates.com](https://ustariffrates.com) — 2026 HTS schedule with all active tariff overlays.

## Pricing context

- **Section 122 (IEEPA)**: 15% universal tariff on all imports (effective 2025, still active 2026)
- **Section 301 (China)**: 7.5%–100% additional duty depending on product list
- **Section 232**: 25% on steel, 10% on aluminum
- Rates stack — a Chinese steel product could face base duty + 301 + 232 + 122

## Requirements

- Python 3.6+
- `curl` (for network access)
- No API key needed for public search
- Optional: set `HTS_API_KEY` env var for direct Cloudflare D1 database fallback

## Disclaimer

Results are informational only. Always verify classifications with a licensed customs broker before filing formal customs entries.
