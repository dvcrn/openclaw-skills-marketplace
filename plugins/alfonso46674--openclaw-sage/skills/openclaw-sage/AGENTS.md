# AGENTS.md — Quick Reference for AI Agents

This is a condensed reference for AI agents using the openclaw-sage skill. For full tool documentation see [`SKILL.md`](SKILL.md).

---

## What This Skill Does

Gives you access to OpenClaw documentation via shell scripts. Docs are fetched from `https://docs.openclaw.ai`, cached locally, and searchable with BM25 ranking.

---

## Decision Tree

| User asks about... | First call |
|---|---|
| Setup / getting started | `fetch-doc.sh start/getting-started` |
| A specific provider (Discord, Telegram, etc.) | `fetch-doc.sh providers/<name>` |
| Configuration | `fetch-doc.sh gateway/configuration --toc` → then `--section` |
| Troubleshooting | `fetch-doc.sh gateway/troubleshooting` |
| A concept (sessions, models, queues...) | `fetch-doc.sh concepts/<topic>` |
| Automation / cron / webhooks | `fetch-doc.sh automation/<topic>` |
| Installation / deployment | `fetch-doc.sh install/docker` or `platforms/<os>` |
| What's new / recent changes | `recent.sh 7` |
| Unsure which doc to use | `search.sh <keyword>` |
| Doc cached, want to check relevance before reading | `info.sh <path>` |

---

## Tool Chaining Patterns

### Check before you fetch
```bash
./scripts/info.sh gateway/configuration          # 1. Check word count + headings
./scripts/fetch-doc.sh gateway/configuration --section retry  # 2. Fetch only what you need
```

### Long doc — read only what you need
```bash
./scripts/fetch-doc.sh gateway/configuration --toc         # 1. See sections
./scripts/fetch-doc.sh gateway/configuration --section retry  # 2. Fetch that section
```

### Discovery → fetch
```bash
./scripts/search.sh --json webhook retry     # 1. Find relevant docs (quotes optional)
./scripts/fetch-doc.sh automation/webhook    # 2. Fetch the top result
```

### Unknown path
```bash
./scripts/sitemap.sh --json   # list all paths by category, then fetch
```

---

## Tool Reference

```bash
# Sitemap
./scripts/sitemap.sh                         # all doc paths, grouped by category
./scripts/sitemap.sh --json                  # [{category, paths[]}]

# Doc metadata (cache only — does not fetch)
./scripts/info.sh <path>                     # title, headings, word count, cache age
./scripts/info.sh <path> --json              # {path, url, title, headings[], word_count, cached_at, fresh}

# Fetch a doc
./scripts/fetch-doc.sh <path>                # full plain text
./scripts/fetch-doc.sh <path> --toc          # headings only
./scripts/fetch-doc.sh <path> --section <h>  # one section (partial, case-insensitive)
./scripts/fetch-doc.sh <path> --max-lines 80 # truncated

# Search — multi-word queries work without quotes
./scripts/search.sh webhook retry            # same as search.sh "webhook retry"
./scripts/search.sh --json webhook retry     # {query, mode, results[], sitemap_matches[]}

# Full index (run once, then use build-index.sh search for best results)
./scripts/build-index.sh fetch               # download all docs
./scripts/build-index.sh build               # build BM25 index
./scripts/build-index.sh search webhook retry  # multi-word, no quotes needed

# What's new
./scripts/recent.sh 7                        # docs updated in last 7 days

# Cache
./scripts/cache.sh status                    # freshness, TTLs, doc count
```

---

## JSON Output

Set `OPENCLAW_SAGE_OUTPUT=json` globally, or pass `--json` per call.

**`search.sh --json` response:**
```json
{
  "query": "webhook retry",
  "mode": "bm25",
  "results": [
    {
      "score": 0.823,
      "path": "automation/webhook",
      "url": "https://docs.openclaw.ai/automation/webhook",
      "excerpt": "Configure retry with maxAttempts..."
    }
  ],
  "sitemap_matches": [
    { "path": "automation/webhook", "url": "https://docs.openclaw.ai/automation/webhook" }
  ]
}
```

`mode` values: `"bm25"` (ranked, index built) · `"grep"` (unranked, no index) · `"sitemap-only"` (no cached content)

**`info.sh --json` response:**
```json
{
  "path": "gateway/configuration",
  "url": "https://docs.openclaw.ai/gateway/configuration",
  "title": "Gateway Configuration | OpenClaw Docs",
  "headings": ["Overview", "Authentication", "Retry Settings"],
  "word_count": 1840,
  "cached_at": "2026-03-06 14:22",
  "fresh": true
}
```
Error (not cached): `{"error": "not_cached", "path": "...", "url": "..."}` with exit 1.

**`sitemap.sh --json` response:**
```json
[
  { "category": "gateway", "paths": ["gateway/configuration", "gateway/security"] },
  { "category": "providers", "paths": ["providers/discord", "providers/telegram"] }
]
```

---

## Error Recovery

| Error | Recovery |
|---|---|
| `fetch-doc.sh` returns empty or fails | Run `search.sh <topic>` to find the right path; check `sitemap.sh` |
| `--section` not found | Error message lists available sections — retry with correct name |
| `search.sh` returns no results | Run `build-index.sh fetch && build-index.sh build` for full coverage |
| Network unavailable | Scripts serve cached content automatically; results may be stale |
| `--toc` / `--section` requires python3 | Fall back to `fetch-doc.sh <path> --max-lines 80` |

---

## Source URL

Always cite the source when answering: `https://docs.openclaw.ai/<path>`
