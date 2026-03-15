---
name: media-news-digest
description: "Generate media & entertainment industry news digests. Covers Hollywood trades (THR, Deadline, Variety), box office, streaming, awards season, film festivals, and production news. Four-source data collection from RSS feeds, Twitter/X KOLs, Reddit, and web search. Pipeline-based scripts with retry mechanisms and deduplication. Supports Discord and email output with PDF attachments."
homepage: https://github.com/draco-agent/media-news-digest
---

# Media News Digest

Automated media & entertainment industry news digest system. Covers Hollywood trades, box office, streaming platforms, awards season, film festivals, production news, and industry deals.

## Quick Start

1. **Generate Digest** (unified pipeline — runs all 4 sources in parallel):
   ```bash
   python3 scripts/run-pipeline.py \
     --defaults <SKILL_DIR>/config/defaults \
     --config <WORKSPACE>/config \
     --hours 48 --freshness pd \
     --archive-dir <WORKSPACE>/archive/media-news-digest/ \
     --output /tmp/md-merged.json --verbose --force
   ```

2. **Use Templates**: Apply Discord or email templates to merged output

## Data Sources (65 total, 64 enabled)

- **RSS Feeds (36, 35 enabled)**: THR, Deadline, Variety, IndieWire, The Wrap, Collider, Vulture, Awards Daily, Gold Derby, Screen Rant, Empire, The Playlist, /Film, Entertainment Weekly, Roger Ebert, CinemaBlend, Den of Geek, The Direct, MovieWeb, CBR, What's on Netflix, Decider, Anime News Network, and more
- **Twitter/X KOLs (18)**: @THR, @DEADLINE, @Variety, @FilmUpdates, @DiscussingFilm, @BoxOfficeMojo, @MattBelloni, @Borys_Kit, @TheAcademy, @letterboxd, @A24, and more
- **Reddit (11)**: r/movies, r/boxoffice, r/television, r/Oscars, r/TrueFilm, r/entertainment, r/netflix, r/marvelstudios, r/DC_Cinematic, r/anime, r/flicks
- **Web Search (9 topics)**: Brave Search / Tavily with freshness filters

## Topics (9 sections)

- 🇨🇳 China / 中国影视 — China mainland box office, Chinese films, Chinese streaming
- 🎬 Production / 制作动态 — New projects, casting, filming updates
- 💰 Deals & Business / 行业交易 — M&A, rights, talent deals
- 🎞️ Upcoming Releases / 北美近期上映 — Theater openings, release dates, trailers
- 🎟️ Box Office / 票房 — NA/global box office, opening weekends
- 📺 Streaming / 流媒体 — Netflix, Disney+, Apple TV+, HBO, viewership
- 🏆 Awards / 颁奖季 — Oscars, Golden Globes, Emmys, BAFTAs
- 🎪 Film Festivals / 电影节 — Cannes, Venice, TIFF, Sundance, Berlin
- ⭐ Reviews & Buzz / 影评口碑 — Critical reception, RT/Metacritic scores

## Scripts Pipeline

### Unified Pipeline
```bash
python3 scripts/run-pipeline.py \
  --defaults config/defaults --config workspace/config \
  --hours 48 --freshness pd \
  --archive-dir workspace/archive/media-news-digest/ \
  --output /tmp/md-merged.json --verbose --force
```
- **Features**: Runs all 4 fetch steps in parallel, then merges + deduplicates + scores
- **Output**: Final merged JSON ready for report generation (~30s total)
- **Flags**: `--skip rss,twitter` to skip steps, `--enrich` for full-text enrichment

### Individual Scripts
- `fetch-rss.py` — Parallel RSS fetcher (10 workers, 30s timeout, caching)
- `fetch-twitter.py` — Dual backend: official X API v2 + twitterapi.io (auto fallback, 3-worker concurrency)
- `fetch-web.py` — Web search via Brave (multi-key rotation) or Tavily
- `fetch-reddit.py` — Reddit public JSON API (4 workers, no auth)
- `merge-sources.py` — Quality scoring, URL dedup, multi-source merging
- `summarize-merged.py` — Structured overview sorted by quality_score
- `enrich-articles.py` — Full-text enrichment for top articles
- `generate-pdf.py` — PDF generation with Chinese typography + emoji
- `send-email.py` — MIME email with HTML body + PDF attachment
- `sanitize-html.py` — XSS-safe markdown to HTML conversion
- `validate-config.py` — Configuration validator
- `source-health.py` — Source health tracking
- `config_loader.py` — Config overlay loader (defaults + user overrides)
- `test-pipeline.sh` — Pipeline testing with --only/--skip/--twitter-backend filters

## Cron Integration

Reference `references/digest-prompt.md` in cron prompts.

### Daily Digest
```
MODE = daily, FRESHNESS = pd, RSS_HOURS = 48
```

### Weekly Digest
```
MODE = weekly, FRESHNESS = pw, RSS_HOURS = 168
```

## Dependencies

All scripts work with **Python 3.8+ standard library only**. `feedparser` optional but recommended.
