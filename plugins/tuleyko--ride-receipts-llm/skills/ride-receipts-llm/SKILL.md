---
name: ride-receipts-llm
description: "Build, refresh, export, and query a local SQLite ride-history database from Gmail ride receipt emails (Uber, Bolt, Yandex Go, Lyft) using LLM extraction from full email HTML. Use when asked to ingest receipts, rebuild/update `rides.sqlite`, investigate ride totals/routes, or extend provider coverage. Requires `gog` Gmail CLI plus authenticated Google account access; processes sensitive receipt data and sends raw email HTML to the active LLM."
---

# ride-receipts-llm

Run a reproducible 3-stage pipeline:

0) initialize/validate SQLite schema (fixed; do not edit)
1) fetch full receipt emails into JSONL
2) extract structured rides with LLM (one-shot + repair)
3) upsert into SQLite

## Prerequisites and safety

- Require `gog` CLI installed and authenticated for the selected Gmail account.
- Prefer configured account: `skills.entries.ride-receipts-llm.config.gmailAccount`; if missing, ask user for account explicitly.
- Ask for date scope before fetch: all-time, after `YYYY-MM-DD`, or between dates.
- Treat receipt content as sensitive financial/location data.
- Before extraction, explicitly confirm user is okay sending raw email HTML to the active LLM.
- Extraction uses raw `text_html` from emails; do not claim local-only parsing.
- Never hallucinate fields; keep unknown values `null`.

## Paths

- Schema (do not modify): `skills/ride-receipts-llm/references/schema_rides.sql`
- Emails JSONL: `./data/ride_emails.jsonl`
- Extracted rides JSONL: `./data/rides_extracted.jsonl`
- SQLite DB: `./data/rides.sqlite`

## 0) Initialize DB

```bash
python3 skills/ride-receipts-llm/scripts/init_db.py \
  --db ./data/rides.sqlite \
  --schema skills/ride-receipts-llm/references/schema_rides.sql
```

## 1) Fetch Gmail receipts → JSONL

```bash
python3 skills/ride-receipts-llm/scripts/fetch_emails_jsonl.py \
  --account <gmail-account> \
  --after YYYY-MM-DD \
  --before YYYY-MM-DD \
  --max-per-provider 5000 \
  --out ./data/ride_emails.jsonl
```

- Omit `--after` / `--before` when not needed.
- Output rows include provider metadata, snippet, and raw `text_html`.

## 2) LLM extraction contract

Read `./data/ride_emails.jsonl`; write one JSON object per line to `./data/rides_extracted.jsonl`.

Per email:
1. Run one-shot extraction for all fields.
2. Quality-gate: `amount,currency,pickup,dropoff,payment_method,distance_text,duration_text,start_time_text,end_time_text`.
3. If any are missing, run repair pass(es) for missing fields only.
4. Merge additively; never replace existing non-null values with `null`.

Schema (one line per ride):

```json
{
  "provider": "Uber|Bolt|Yandex|Lyft",
  "source": {"gmail_message_id": "...", "email_date": "YYYY-MM-DD HH:MM", "subject": "..."},
  "ride": {
    "start_time_text": "...",
    "end_time_text": "...",
    "total_text": "...",
    "currency": "EUR|PLN|USD|BYN|RUB|UAH|null",
    "amount": 12.34,
    "pickup": "...",
    "dropoff": "...",
    "pickup_city": "...",
    "pickup_country": "...",
    "dropoff_city": "...",
    "dropoff_country": "...",
    "payment_method": "...",
    "driver": "...",
    "distance_text": "...",
    "duration_text": "...",
    "notes": "..."
  }
}
```

Rules:
- Use `text_html` as primary source; fallback to `snippet` only if `text_html` is empty.
- Keep addresses/time strings verbatim.
- Keep `amount` numeric; if only textual total exists, set `amount: null` and preserve text in `total_text`.

## 3) Insert extracted rides → SQLite

```bash
python3 skills/ride-receipts-llm/scripts/insert_rides_sqlite_jsonl.py \
  --db ./data/rides.sqlite \
  --schema skills/ride-receipts-llm/references/schema_rides.sql \
  --rides-jsonl ./data/rides_extracted.jsonl
```

Schema is idempotent via `UNIQUE(provider, gmail_message_id) ON CONFLICT REPLACE`.
