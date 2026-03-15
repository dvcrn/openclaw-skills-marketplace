---
name: hts-classifier
description: "Look up HTS tariff codes and 2026 US duty rates. Use when: user asks about tariff codes, duty rates, HTS classification, import taxes, or trade compliance for any product. NOT for: customs brokerage, filing entries, or legal trade advice. No API key needed."
homepage: https://ustariffrates.com
---

# HTS Classifier — US Tariff Code & Duty Rate Lookup

Classify products into HTS codes and get current 2026 US duty rates including Section 301, Section 232, and IEEPA (Section 122) tariffs.

## When to Use

**USE this skill when:**

- "What's the HTS code for solar panels?"
- "Tariff rate on steel pipes from China"
- "Look up duty for HTS 8541.40"
- "How much import tax on lithium batteries?"
- "Classify this product for customs"
- Any question about US import duties or tariff codes

## When NOT to Use

**DON'T use this skill when:**

- Filing customs entries or ISF → use a customs broker
- Legal classification disputes → consult a licensed customs broker
- Export controls / ITAR / EAR → use export compliance tools
- Tariff engineering or structuring advice → consult trade counsel

## Commands

### Search by product description

```bash
python3 ~/.openclaw/skills/hts-classifier/scripts/classify.py --query "solar panels"
```

### Look up a specific HTS code

```bash
python3 ~/.openclaw/skills/hts-classifier/scripts/classify.py --hts "8541.40"
```

### Both at once

```bash
python3 ~/.openclaw/skills/hts-classifier/scripts/classify.py --query "photovoltaic cells" --hts "8541.40"
```

### With LLM ranking (optional, slower — uses local Ollama)

```bash
python3 ~/.openclaw/skills/hts-classifier/scripts/classify.py --query "solar panels" --rank
```

## Output

Returns JSON with top matching HTS codes including:

- `hts_code` — The harmonized tariff code
- `description` — Official HTS description
- `base_duty` — General (MFN) duty rate
- `section_301_china` — Section 301 additional duty (%) for Chinese-origin goods
- `section_232` — Section 232 duty (%) for steel/aluminum
- `section_122` — IEEPA/Section 122 universal tariff (%)
- `total_estimated` — Total estimated effective duty rate
- `warnings` — Active tariff overlays and special notes
- `trade_data` — Import volume data when available

## Environment Variables (all optional)

| Variable | Default | Purpose |
|----------|---------|---------|
| `OLLAMA_URL` | `http://localhost:11434` | Local Ollama endpoint for LLM ranking |
| `OLLAMA_MODEL` | `qwen3:8b` | Ollama model for ranking (must support JSON output) |
| `OLLAMA_TIMEOUT` | `30` | Seconds before ranking times out (falls back to FTS5) |
| `HTS_LOG` | `/tmp/hts-classifier.log` | Log file path (queries are logged — use `/dev/null` to disable) |
| `HTS_API_KEY` | *(unset)* | Cloudflare D1 API token for direct DB fallback — **only set if you operate the ustariffrates D1 database** |

## Network Interactions

- **Always**: queries `ustariffrates.com/api/search` (public API, no auth)
- **Optional**: calls local Ollama (`localhost:11434`) when `--rank` is used
- **Optional**: queries Cloudflare D1 only if `HTS_API_KEY` is explicitly set (disabled by default)

## Notes

- Data is live from ustariffrates.com (2026 HTS schedule)
- Includes Section 301, 232, and IEEPA (Section 122) tariff overlays
- Results are informational — always verify with a licensed customs broker for formal entries
- No API key required for public search
- Queries are logged to `HTS_LOG` — set to `/dev/null` if handling sensitive product descriptions
