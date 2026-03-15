# Changelog

All notable changes to openclaw-sage are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.2.4] — 2026-03-11

### Fixed

- **BUG-15** (`snippets/common-configs.md`) — Model name `claude-sonnet-4-5` updated to `claude-sonnet-4-6` to match `SKILL.md`.
- **BUG-17** (`recent.sh`, `build-index.sh`) — Remaining hardcoded `https://docs.openclaw.ai` URLs missed by the BUG-01 fix. `recent.sh` Python heredoc now receives `$DOCS_BASE_URL` via `sys.argv`. `build-index.sh` awk blocks use `-v base_url=`, grep/sed pipelines use `$DOCS_BASE_URL`. All produce correct output when `OPENCLAW_SAGE_DOCS_BASE_URL` is overridden.
- **BUG-18** (`fetch-doc.sh`) — Removed local `fetch_and_cache()` that shadowed the shared `lib.sh` version. Replaced with a thin `_do_fetch` wrapper that calls the lib version and adds fetch-doc-specific error messages.
- **BUG-19** (`search.sh`) — "Tip: For comprehensive ranked results..." diagnostic block was sent to stdout, polluting agent-parseable output. Redirected to stderr.
- **BUG-20** (`build-index.sh`) — "Error: Could not get URL list from sitemap..." message was sent to stdout instead of stderr. Added `>&2`.
- **I-1** (`build-index.sh`) — Bare redirection `> "$INDEX_FILE"` (ShellCheck SC2188) replaced with `: > "$INDEX_FILE"`.

### Added

- `tests/test_build_index.bats` — 2 new tests: BUG-20 stderr routing, BUG-17 URL override regression.
- `tests/test_search.bats` — 1 new test: BUG-19 tip text not on stdout.
- `tests/test_recent.bats` — 1 new test: BUG-17 URL override regression.
- `tests/test_fetch_doc.bats` — 1 new test: BUG-18 no local fetch_and_cache shadow.

---

## [0.2.3] 2026-03-10

### Fixed

- **BUG-07** (`build-index.sh`, `lib.sh`) — `build-index.sh fetch` only wrote `.txt` files; the `.html` cache was never populated. Subsequent `--toc`/`--section` calls on bulk-fetched docs required a redundant network round-trip. Added a shared `fetch_and_cache <url> <safe_path>` helper to `lib.sh` that writes both `doc_<safe>.html` and `doc_<safe>.txt` in a single HTTP request. `build-index.sh fetch` now calls this helper instead of `fetch_text`.
- **BUG-08** (`recent.sh`) — sitemap was only re-fetched when the file was absent (`[ ! -f ]`), ignoring `$SITEMAP_TTL`. A stale sitemap would be served indefinitely. Replaced with `! is_cache_fresh "$SITEMAP_XML" "$SITEMAP_TTL"` consistent with all other scripts.
- **BUG-09** (`recent.sh`) — `$DAYS` argument had no validation; a non-numeric value like `recent.sh foo` would propagate to `find -mtime` (immediate error) and Python `int()` (unhandled exception) with no usage hint. Added `[[ "$DAYS" =~ ^[0-9]+$ ]]` guard after sourcing `lib.sh`, printing `Usage: recent.sh [days]` and exiting 1 on invalid input.

### Added

- `tests/test_recent.bats` — 7 tests covering BUG-08 (TTL-based sitemap refresh) and BUG-09 (argument validation).
- `tests/test_build_index.bats` — 4 tests covering BUG-07 (`fetch_and_cache` dual-write regression).

---

## [0.2.2] - 2026-03-09

### Fixed

- **BUG-01** (`search.sh`, `build-index.sh`) — awk grep-fallback path hardcoded `https://docs.openclaw.ai` instead of using `$DOCS_BASE_URL`. Now passes the variable via `awk -v base_url=`.
- **BUG-02** (`sitemap.sh`, `build-index.sh`, `track-changes.sh`) — `grep -oP` uses PCRE which is unsupported on macOS/BSD grep, causing silent failures. Replaced with POSIX-compatible `grep -o '<loc>[^<]*</loc>' | sed 's/<[^>]*>//g'`.
- **BUG-03** (`track-changes.sh`) — `trap "rm -f $AFTER_TMP" EXIT` expanded the variable at registration time; a `TMPDIR` with spaces would break cleanup. Changed to single-quoted `trap 'rm -f "$AFTER_TMP"' EXIT`.
- **BUG-04** (`info.sh`) — JSON `not_cached` error was built with `printf "%s"` interpolation, producing invalid JSON for paths containing `"` or `\`. Now emits via Python `json.dumps`.
- **BUG-05** (`fetch-doc.sh`) — when offline with no HTML cache, `--toc`/`--section` would fall through to a misleading "run without --toc first" error. Now exits immediately with a clear offline message.
- **BUG-06** (`track-changes.sh`) — `get_current_pages` unconditionally overwrote `sitemap.xml` on every call, ignoring `$SITEMAP_TTL` and risking corruption if curl failed silently. Now checks `is_cache_fresh` first and only writes via a temp file + `mv` on success.

### Added

- **`OPENCLAW_SAGE_DOCS_BASE_URL`** env var override in `lib.sh` — allows overriding the docs base URL for testing or private mirrors. Consistent with all other `OPENCLAW_SAGE_*` overrides.

---

## [0.2.1] - 2026-03-08

### Added

- **`scripts/info.sh`** — lightweight doc metadata from cache only (no network request). Returns title (from `<title>` HTML tag), headings list, word count, cache age/freshness, and URL. Exits 1 with a clear `not_cached` message if the doc hasn't been fetched yet. Supports `--json` and `OPENCLAW_SAGE_OUTPUT=json`. Degrades gracefully when HTML cache or `python3` is unavailable (falls back to word count and cache age from `.txt` file).
- **Upfront offline detection** across all fetch-capable scripts. `check_online()` (defined in `lib.sh`) performs a 2-second HEAD request before any network operation. On failure: scripts immediately print `Offline: cannot reach <url>` to stderr and either fall back to cached content or exit cleanly. Affected scripts: `fetch-doc.sh`, `sitemap.sh`, `build-index.sh`, `recent.sh`, `track-changes.sh`, `info.sh`. Agents no longer wait for a 10-15s curl timeout before learning the host is unreachable.
- **Multi-word query support confirmed consistent** across `search.sh` and `build-index.sh search`. Quotes are never required: `./scripts/search.sh webhook retry` and `./scripts/build-index.sh search webhook retry` both work. `search.sh` uses `KEYWORD="${ARGS[*]}"` after flag parsing; `build-index.sh` uses `QUERY="$*"` after subcommand shift; `bm25_search.py` joins `sys.argv[3:]` so it accepts either a single spaced arg or multiple args identically. `AGENTS.md` updated with unquoted examples.

---

## [0.2.0] - 2026-03-07

### Fixed

- **Critical domain bug** in `build-index.sh` — cache file paths were built from `docs.clawd.bot` instead of `docs.openclaw.ai`, producing malformed filenames and fetching from the wrong host.

### Added

- **`scripts/lib.sh`** — shared library sourced by all scripts. Provides `is_cache_fresh()`, `fetch_text()`, `DOCS_BASE_URL`, `CACHE_DIR`, `SITEMAP_TTL`, `DOC_TTL`, and `LANGS`. All values are overridable via env vars.
- **`scripts/bm25_search.py`** — BM25 ranked full-text search over the doc index. Two modes: `search` (outputs `score | path | excerpt`) and `build-meta` (writes `index_meta.json` for faster repeated searches). Falls back to simple term frequency on small corpora.
- **`fetch-doc.sh --toc`** — extract and display the heading tree of a doc without fetching the full body. Parses `<h1>`–`<h6>` from the cached HTML.
- **`fetch-doc.sh --section <heading>`** — extract a specific section by heading name (case-insensitive partial match). On a miss, lists all available headings so the caller can correct the query.
- **`fetch-doc.sh --max-lines <n>`** — truncate doc output to N lines.
- **`search.sh --json`** — structured JSON output: `{query, mode, results[], sitemap_matches[]}`. `mode` is `"bm25"`, `"grep"`, or `"sitemap-only"` so callers know result quality. BM25 scores are floats; grep fallback scores are `null`.
- **`sitemap.sh --json`** — structured JSON output: `[{category, paths[]}]`.
- **`OPENCLAW_SAGE_OUTPUT=json`** env var — global JSON mode flag respected by `search.sh` and `sitemap.sh`.
- **`OPENCLAW_SAGE_LANGS`** env var — filter which language docs to download during `build-index.sh fetch`. Defaults to `en`. Accepts comma-separated language base codes (`en,zh`) or `all`. Correctly handles locale variants like `zh-CN`, `pt-BR`.
- **Language detection** in `build-index.sh fetch` — prints all languages found in the sitemap with doc counts before filtering, so users know what `OPENCLAW_SAGE_LANGS` values are available.
- **HTML caching** (`doc_<path>.html`) alongside plain text — a single HTTP request now caches both. Required for `--toc` and `--section`. Older `.txt`-only cache entries are backfilled on demand.
- **`index_meta.json`** — pre-computed BM25 statistics (doc lengths, term–document frequencies) written by `build-index.sh build`. Used by `bm25_search.py` to skip recomputing on every search.
- iMessage and MS Teams provider snippets in `snippets/common-configs.md`.

### Changed

- **Default cache directory** moved from `~/.cache/openclaw-sage` to `<skill_root>/.cache/openclaw-sage`. Agents sandboxed to their workspace no longer need `HOME` to be accessible. Override with `OPENCLAW_SAGE_CACHE_DIR`.
- **All scripts now source `scripts/lib.sh`** — `is_cache_fresh` and `fetch_text` were previously duplicated in every script.
- **`fetch-doc.sh` doc TTL** raised from 1hr to 24hr (via `DOC_TTL` default). Sitemap TTL stays at 1hr.
- **`fetch-doc.sh` fetch strategy** — now always fetches raw HTML first, then derives plain text from the cached file (single HTTP request instead of potentially two).
- **`build-index.sh search`** now uses BM25 ranking via `bm25_search.py` instead of grep. Falls back to grep when `python3` is unavailable.
- **`search.sh`** unified output format: `[score] path -> url / excerpt` regardless of which search path is taken. BM25 path shows float scores; grep/sitemap paths show `[---]`.
- **`recent.sh`** output split into two clearly labelled sections: `=== Docs updated at source ===` and `=== Recently accessed locally ===`.
- **`cache.sh status`** now shows active TTL values and the env var names that override them.
- **`cache.sh clear-docs`** now also removes `doc_*.html` files and `index_meta.json`.
- **`track-changes.sh`** now uses `trap "rm -f $AFTER_TMP" EXIT` to guarantee temp file cleanup.
- **`SKILL.md`** fully rewritten with formal Tool definitions (purpose, input, output, errors), explicit Decision Rules, inline config snippets for all providers, and an Error Handling table.
- **`README.md`** — `python3` marked as optional/recommended; env var table added; cache file table updated.
- **`.gitignore`** — added `.cache/` to prevent cached docs from being committed.

---

## [0.1.0] - 2026-03-06

Initial release.

- `sitemap.sh` — fetch and display docs by category (cached 1hr)
- `fetch-doc.sh` — fetch a specific doc as plain text (cached 1hr)
- `search.sh` — search cached docs by keyword, with sitemap path fallback
- `build-index.sh` — download all docs, build grep-based full-text index, search index
- `recent.sh` — show docs updated in the last N days via sitemap `lastmod`
- `cache.sh` — cache management (status, refresh, clear-docs, dir)
- `track-changes.sh` — sitemap snapshot diffing (snapshot, list, since, diff)
- `SKILL.md` — agent-facing skill description
- `snippets/common-configs.md` — ready-to-use config snippets for all providers
