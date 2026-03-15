# statsfm-cli

A command-line tool for querying your [stats.fm](https://stats.fm) Spotify listening data. No API key, no dependencies — just Python and your username.

## What it does

```
$ statsfm.py top-tracks --range lifetime --limit 5
  1. Espresso                            Sabrina Carpenter         Short n' Sweet                   847 plays  (42h 3m)
  2. ...
```

- **Top lists** — your most played tracks, artists, albums, and genres
- **Now playing** — see what's currently playing on your Spotify
- **Recent streams** — last N tracks you listened to
- **Detailed stats** — per-artist, per-track, per-album play counts with monthly breakdowns
- **Drill-downs** — top tracks from a specific artist or album
- **Global charts** — what's trending worldwide on stats.fm
- **Search** — find artist/track/album IDs by name

## Usage

```bash
export STATSFM_USER=your_username

statsfm.py top-artists --range lifetime
statsfm.py top-tracks --start 2025 --end 2026
statsfm.py now-playing
statsfm.py artist-stats 22369
statsfm.py search "sabrina carpenter" --type artist
```

**Time ranges:** `today` · `weeks` · `months` · `lifetime` · or custom `--start`/`--end` dates (YYYY, YYYY-MM, or YYYY-MM-DD)

## Requirements

Python 3.6+ · stdlib only · no pip installs
