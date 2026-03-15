---
name: daily-investment-digest
description: "Fetch financing event lists from the iYiou skill API and generate a daily financing report in Markdown to stdout. Use when the task asks to pull investment/financing events via `https://api.iyiou.com/skill/info?page=...&pageSize=...`, paginate with `pageSize=10` and `page<=5`, deduplicate records, default to yesterday's date, and optionally use today's date only when explicitly requested by the user."
---

# Daily Investment Digest

## Overview

- Pull investment/financing events from `https://api.iyiou.com/skill/info`.
- Normalize fields, deduplicate rows, and generate a structured Chinese daily report.

## Workflow

1. One-command full report (recommended, default uses yesterday).
```bash
node "{baseDir}/scripts/run_full_report.mjs" \
  --max-page 5
```

2. If user explicitly asks for today's report, pass today's date.
```bash
node "{baseDir}/scripts/run_full_report.mjs" \
  --report-date 2026-03-11 \
  --max-page 5
```

3. Direct output mode (stdout only, no file).
```bash
node "{baseDir}/scripts/fetch_events.mjs" \
  --report-date 2026-03-11 \
  --stdout-json | \
node "{baseDir}/scripts/generate_report.mjs" \
  --input-json - \
  --top-n 0 \
  --stdout
```

## Path Safety

- Always call scripts with quoted `{baseDir}` paths to avoid whitespace-path issues.
- Scripts resolve relative input paths against the skill root directory.

## Required API Rules

- Use `pageSize=10`.
- Start at `page=1`.
- Increment `page` by 1 each request.
- Stop when `page>5` or API event list is empty.
- Parse response strictly by schema: `response.code` -> `response.data.posts`.
- Treat non-zero `code` as API failure.
- Retry failed requests up to 3 times before skipping a page.

## Script Interfaces

### `scripts/run_full_report.mjs`

- One-command pipeline: fetch + generate
- Defaults to full output (`top-n=0`)
- Supports `--report-date`, `--max-page`, `--page-size`, `--timeout-seconds`, `--retry`, `--delay-seconds`
- Supports `--top-n` (`0` means all events)

### `scripts/fetch_events.mjs`

- `--page-size` default `10`
- `--max-page` default `5`
- `--report-date` default yesterday (`YYYY-MM-DD`)
- `--timeout-seconds` default `15`
- `--retry` default `3`
- `--delay-seconds` default `0`
- Always prints JSON to stdout (`--stdout-json` kept only for compatibility)
- Numeric args are bounded for safety: `page-size[1,100]`, `max-page[1,500]`, `retry[1,10]`

### `scripts/generate_report.mjs`

- `--input-json` required
- `--top-n` default `0` (`0` means all events)
- Always prints report text to stdout (`--stdout` kept only for compatibility)
- Numeric args are bounded for safety: `top-n[0,500]`

## Output Files

- Disabled by design. This skill is stdout-only and does not write report artifacts to disk.

## Data Mapping

- Follow [field_mapping.md](references/field_mapping.md) for source-to-target mapping and fallback rules.
- To reduce context size, the fetch output keeps only: `brief`, `createdAt`, `originalLink`, `postTitle`, `tags`.

## Failure Handling

- Continue on single-page failure after retries.
- Use progressive retry backoff (`0.5s`, `1.0s`, `1.5s`, ...).
- Record page-level errors in output JSON `meta.errors`.
- Generate a report even when no events are found, and clearly mark it as an empty-day report.

## Output Policy

- Date policy: default to yesterday; only use today when the user explicitly asks for today.
- If user asks full detail, run with `--top-n 0`.
- Use script stdout as the main body and keep event entries unchanged.
- Output order is mandatory:
1. First output the full event list.
2. Each event must include: `公司简称`、`轮次`、`投资方`、`事件摘要`、`来源链接`.
3. After the full event list, append one ending section titled `投资事件总结`.
- Do not output `投资事件总结` before event entries.

## Quick Checks

1. Run fetch step and confirm `meta.total_unique_events > 0` on active days.
2. Run report step and confirm stdout contains:
- `核心数据概览`
- `融资事件按行业分类`
3. In final AI response, confirm order:
- Event list appears first and each item includes `公司简称`、`轮次`、`投资方`、`事件摘要`、`来源链接`.
- `投资事件总结` appears only after the event list.
- `投资事件总结` appears exactly once at the end.
4. In final AI response, confirm it appends:
- `投资事件总结`

## Example End-to-End Command

```bash
node "{baseDir}/scripts/run_full_report.mjs" \
  --report-date 2026-03-11 \
  --max-page 5
```
