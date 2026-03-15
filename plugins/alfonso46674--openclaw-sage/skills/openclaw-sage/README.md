# openclaw-sage

An [OpenClaw](https://openclaw.ai) skill that makes any agent an expert on [OpenClaw](https://docs.openclaw.ai) documentation — with live doc fetching, BM25 ranked search, section extraction, full-text indexing, and change tracking.

## Requirements

- `bash`
- `curl`
- `python3` *(optional, recommended — enables BM25 ranked search, `--toc`/`--section` extraction, JSON output, and `recent.sh` date parsing)*
- `lynx` or `w3m` *(optional, recommended — improves HTML-to-text quality)*

## Environment Variables

All variables are optional. Defaults work out of the box.

| Variable | Default | Description |
|---|---|---|
| `OPENCLAW_SAGE_SITEMAP_TTL` | `3600` | Sitemap cache TTL in seconds (1hr) |
| `OPENCLAW_SAGE_DOC_TTL` | `86400` | Doc page cache TTL in seconds (24hr) |
| `OPENCLAW_SAGE_CACHE_DIR` | `<skill_root>/.cache/openclaw-sage` | Cache directory |
| `OPENCLAW_SAGE_LANGS` | `en` | Languages to fetch: comma-separated codes (`en,zh`) or `all` |
| `OPENCLAW_SAGE_OUTPUT` | *(unset)* | Set to `json` for machine-readable output from `search.sh` and `sitemap.sh` |
| `OPENCLAW_SAGE_DOCS_BASE_URL` | `https://docs.openclaw.ai` | Override the base docs URL (useful for testing or private mirrors) |

Examples:
```bash
OPENCLAW_SAGE_DOC_TTL=60 ./scripts/fetch-doc.sh gateway/configuration
OPENCLAW_SAGE_LANGS=en,zh ./scripts/build-index.sh fetch
OPENCLAW_SAGE_OUTPUT=json ./scripts/search.sh webhook
```

## Scripts

All scripts live in `./scripts/` and cache results in `.cache/openclaw-sage/` inside the skill root.

### Core

```bash
./scripts/sitemap.sh              # List all docs grouped by category
./scripts/sitemap.sh --json       # Same, as JSON [{category, paths[]}]
./scripts/cache.sh status         # Show cache location, age, TTLs, and doc count
./scripts/cache.sh refresh        # Clear sitemap cache to force re-fetch
./scripts/cache.sh clear-docs     # Remove all cached docs, HTML, and index
```

### Search & Fetch

```bash
./scripts/search.sh discord                   # Search cached docs by keyword (BM25 ranked if index built)
./scripts/search.sh --json "webhook retry"    # Same, as JSON {query, mode, results[]}
./scripts/recent.sh 7                         # Docs updated in the last N days (default: 7)

./scripts/fetch-doc.sh gateway/configuration          # Fetch full doc as plain text
./scripts/fetch-doc.sh gateway/configuration --toc    # Show headings only
./scripts/fetch-doc.sh gateway/configuration --section "Retry Settings"  # Extract one section
./scripts/fetch-doc.sh gateway/configuration --max-lines 50              # Truncate output
```

**Recommended workflow for long docs:**
```bash
./scripts/fetch-doc.sh gateway/configuration --toc         # 1. See available sections
./scripts/fetch-doc.sh gateway/configuration --section retry  # 2. Fetch just what you need
```

### Full-Text Index

Build a local BM25 index for ranked search across all docs:

```bash
./scripts/build-index.sh fetch                  # Download all docs to cache (respects OPENCLAW_SAGE_LANGS)
./scripts/build-index.sh build                  # Build BM25 index + index_meta.json
./scripts/build-index.sh search "webhook retry" # BM25-ranked search
./scripts/build-index.sh status                 # Show doc/index/meta counts
```

### Version Tracking

```bash
./scripts/track-changes.sh snapshot            # Save a snapshot of the current doc list
./scripts/track-changes.sh list                # Show all saved snapshots
./scripts/track-changes.sh since 2026-01-01    # Show docs added/removed since a date
./scripts/track-changes.sh diff <snap1> <snap2> # Compare two specific snapshots
```

## Cache

Files are stored in `.cache/openclaw-sage/` inside the skill root by default (override with `OPENCLAW_SAGE_CACHE_DIR`):

| File | Description |
|---|---|
| `sitemap.xml` | Raw sitemap XML from docs.openclaw.ai |
| `sitemap.txt` | Parsed sitemap, human-readable (TTL: `SITEMAP_TTL`) |
| `doc_<path>.txt` | Cached doc as plain text (TTL: `DOC_TTL`) |
| `doc_<path>.html` | Raw HTML cache — required for `--toc` and `--section` |
| `index.txt` | Full-text search index (pipe-delimited: `path\|line`) |
| `index_meta.json` | Pre-computed BM25 statistics (doc lengths, term frequencies) |
| `snapshots/` | Timestamped doc-list snapshots for change tracking |

The `.cache/` directory is gitignored.

## Docs

All documentation is at [docs.openclaw.ai](https://docs.openclaw.ai).

## License

MIT
