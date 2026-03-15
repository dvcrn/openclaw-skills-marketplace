---
name: statsfm
description: "Music data tool powered by the stats.fm API. Look up album tracklists, artist discographies, and global charts without an account. With a stats.fm username, query personal Spotify listening history, play counts, top artists/tracks/albums, monthly breakdowns, and currently playing."
---

# stats.fm CLI

Comprehensive Python CLI for querying stats.fm API (Spotify listening analytics).

**Requirements:** Python 3.6+ (stdlib only, no pip installs needed)

**Script location:** `scripts/statsfm.py` in this skill's directory. Examples use `./statsfm.py` assuming you're in the scripts folder.

## Prerequisites

**Stats.fm account (optional)**
- A stats.fm account is only needed for personal listening data (history, top tracks, now playing, etc.)
- Without an account, you can still use public features: album tracklists, artist discographies, search, and global charts
- Don't have one? Visit [stats.fm](https://stats.fm) and sign up with Spotify or Apple Music (AM untested, Plus status unknown)
- Already have one? Copy your username from your profile

## Setup

**No account needed** for public commands: `search`, `album`, `artist-albums`, `charts-top-tracks`, `charts-top-artists`, `charts-top-albums`.

For personal stats (`profile`, `top-artists`, `top-tracks`, `recent`, `np`, etc.), pass your username with `--user USERNAME` / `-u USERNAME`. These commands exit with code 1 if no user is provided.

## Quick Start

```bash
# View your profile
./statsfm.py profile

# Top tracks this month
./statsfm.py top-tracks --limit 10

# Track stats for 2025
./statsfm.py track-stats 188745898 --start 2025 --end 2026
```

## All Commands

### User Profile
- `profile` - Show username, pronouns, bio, Plus status, timezone, Spotify sync info

### Top Lists
- `top-tracks` - Your most played tracks
- `top-artists` - Your most played artists
- `top-albums` - Your most played albums
- `top-genres` - Your top music genres

### Current Activity
- `now-playing` (aliases: `now`, `np`) - Currently playing track
- `recent` - Recently played tracks

### Detailed Stats
- `artist-stats <artist_id>` - Your play count, listening time, and monthly breakdown for this artist
- `track-stats <track_id>` - Your play count, listening time, and monthly breakdown for this track (shows track name + album)
- `album-stats <album_id>` - Your play count, listening time, and monthly breakdown for this album
- `stream-stats` - Your overall streaming summary (total streams, total time, avg track length, shortest/longest, unique counts for tracks/artists/albums)

### Lookups
- `artist <artist_id>` - Artist info and discography. Shows genres, followers, popularity score (100 = very popular, 50 = underground, 0 = no data).
  - `--type album|single|all` (default: all)
  - `--limit N` - Items per section (default: 15)
- `album <album_id>` - Album info and full tracklist (release date, label, genres, tracks with duration and [E] tags)
- `artist-albums <artist_id>` - All albums/singles by artist, grouped by type (Albums, Singles & EPs, Compilations), newest first. Deduped by ID, 15 per section by default, shows "(N more)" overflow.
  - `--type album|single|all` (default: all)
  - `--limit N` - Items per section

### Drill-Down
- `top-tracks-from-artist <artist_id>` - Your most played tracks from this artist
- `top-tracks-from-album <album_id>` - Your most played tracks from this album
- `top-albums-from-artist <artist_id>` - Your most played albums from this artist

### Global Charts
- `charts-top-tracks` - Global top tracks chart
- `charts-top-artists` - Global top artists chart
- `charts-top-albums` - Global top albums chart

### Search
- `search <query>` - Search for artists, tracks, or albums. Use `--type artist|track|album` to filter results to one category

## Common Flags

### Date Ranges
All stats commands support both predefined ranges and custom dates:

**Predefined ranges:**
- `--range today` or `--range 1d` - Today only
- `--range 4w` - Last 4 weeks (default)
- `--range 6m` - Last 6 months
- `--range all` - All time (lifetime)

**Duration ranges** (resolved to custom timestamps):
- `--range 7d` - Last 7 days
- `--range 14d` - Last 14 days
- `--range 30d` - Last 30 days
- `--range 90d` - Last 90 days

**Custom date ranges:**
- `--start YYYY` - Start year (e.g., `--start 2025`)
- `--start YYYY-MM` - Start month (e.g., `--start 2025-07`)
- `--start YYYY-MM-DD` - Start date (e.g., `--start 2025-07-15`)
- `--end YYYY[-MM[-DD]]` - End date (same formats)

**Examples:**
```bash
# All of 2025
./statsfm.py top-artists --start 2025 --end 2026

# Just July 2025
./statsfm.py top-tracks --start 2025-07 --end 2025-08

# Q1 2025
./statsfm.py artist-stats 39118 --start 2025-01-01 --end 2025-03-31
```

### Granularity
- `--granularity monthly` - Monthly breakdown (default)
- `--granularity weekly` - Weekly breakdown (shows week number + start date)
- `--granularity daily` - Daily breakdown (shows date + day name)
- Works with `artist-stats`, `track-stats`, `album-stats`

### Other Flags
- `--limit N` / `-l N` - Limit results (default: 15)
- `--user USERNAME` / `-u USERNAME` - Specify the stats.fm username to query
- `--no-album` - Hide album names in track listings (albums show by default)

## Usage Examples

```bash
# Search for an artist, then drill down
./statsfm.py search "madison beer" --type artist
./statsfm.py artist-stats 39118 --start 2025
./statsfm.py top-tracks-from-artist 39118 --limit 20

# Weekly breakdown of a track
./statsfm.py track-stats 188745898 --start 2025 --end 2026 --granularity weekly

# Custom date range
./statsfm.py top-artists --start 2025-06 --end 2025-09

# Album tracklist and discography
./statsfm.py album 1365235
./statsfm.py artist-albums 39118 --type album

# Global charts
./statsfm.py charts-top-tracks --limit 20
```

## Output Features

### Automatic Monthly Breakdowns
Stats commands (`artist-stats`, `track-stats`, `album-stats`) automatically show:
- Total plays and listening time
- Monthly breakdown with plays and time per month
- Works for both predefined ranges and custom date ranges

Example output:
```
Total: 505 plays  (29h 53m)

Monthly breakdown:
  2025-02:   67 plays  (3h 52m)
  2025-03:  106 plays  (6h 21m)
  2025-04:   40 plays  (2h 24m)
  ...
```

### Display Information
- **Track listings:** Show position, track name, artist, album (by default), play count, time
- **Album listings:** Show position, album name, artist, play count, time
- **Artist listings:** Show position, artist name, play count, time, genres
- **Charts:** Show global rankings with stream counts
- **Recent streams:** Show timestamp, track, artist, album (by default)

## Plus vs Free Users

**Stats.fm Plus required for:**
- Stream counts in top lists
- Listening time (play duration)
- Detailed statistics

**Free users get:**
- Rankings/positions
- Track/artist/album names
- Currently playing
- Search functionality
- Monthly breakdowns (via per-day stats endpoint)

The script handles both gracefully, showing `[Plus required]` for missing data.

## API Information

**Base URL:** `https://api.stats.fm/api/v1`

**Authentication:** None needed for public profiles

**Response format:** JSON with `item` (single) or `items` (list) wrapper

**Rate limiting:** Be reasonable with requests. Avoid more than ~10 calls in rapid succession during deep dives.

## Error Handling

All errors print to **stderr** and exit with **code 1**.

| Scenario | stderr output | What to do |
|----------|--------------|------------|
| No user set | `Error: No user specified.` | Pass `--user USERNAME` flag |
| API error (4xx/5xx) | `API Error (code): message` | Check if user exists, profile is public, or ID is valid |
| Connection failure | `Connection Error: reason` | Retry after a moment, check network |
| Empty results | No error, just no output | User may be private, or no data for that period — try `--range all` |
| Plus-only data | Shows `[Plus required]` inline | Acknowledge gracefully, show what's available |

## Finding IDs

Use search to find artist/track/album IDs:

```bash
# Find artist
./statsfm.py search "sabrina carpenter" --type artist
# Returns: [22369] Sabrina Carpenter [pop]

# Find track
./statsfm.py search "espresso" --type track
# Returns: [188745898] Espresso by Sabrina Carpenter

# Find album
./statsfm.py search "short n sweet" --type album
# Returns: [56735245] Short n' Sweet by Sabrina Carpenter
```

Then use the ID numbers in other commands.

## Tips

1. **Use custom dates for analysis:** `--start 2025 --end 2026` to see full year stats
2. **Chain discoveries:** Search → Get ID → Detailed stats → Drill down
3. **Compare periods:** Run same command with different date ranges
4. **Export data:** Pipe output to file for records: `./statsfm.py top-tracks --start 2025 > 2025_top_tracks.txt`
5. **Albums show by default:** Match the stats.fm UI behavior (album art is prominent)
6. **Monthly breakdowns:** All stats commands show month-by-month progression automatically

## For AI Agents

**Setup:** Check memory for a stats.fm username. If missing, ask. All personal data commands need `--user USERNAME`.

**Multiple time ranges:** Always compare multiple ranges (`--range today`, `7d`, `30d`, `90d`, `all`) to show how taste shifts over time. Lifetime stats alone miss current trends.

### Time Translations

- "This year" → `--start 2025 --end 2026`
- "Last summer" → `--start 2025-06 --end 2025-09`  
- "When did I discover X" → `artist-stats <id> --range all` (first month in breakdown)

### Command Reference

| Intent | Command | Key flags |
|--------|---------|-----------|
| Your plays of a track | `track-stats <id>` | `--start/--end`, `--granularity` |
| Your plays of an artist | `artist-stats <id>` | `--start/--end`, `--granularity` |
| Your plays of an album | `album-stats <id>` | `--start/--end`, `--granularity` |
| Your overall stats | `stream-stats` | `--range`, `--start/--end` |
| Your rankings | `top-tracks`, `top-artists`, `top-albums`, `top-genres` | `--range`, `--start/--end`, `--limit` |
| Currently playing | `now-playing` | | 
| Recent tracks | `recent` | `--limit` |
| Artist overview | `artist <id>` | `--limit` |
| Artist's discography | `artist-albums <id>` | `--limit` |
| Album tracklist | `album <id>` | |
| Your top tracks by artist | `top-tracks-from-artist <id>` | `--range`, `--limit` |
| Your top tracks on album | `top-tracks-from-album <id>` | `--range`, `--limit` |
| Your top albums by artist | `top-albums-from-artist <id>` | `--range`, `--limit` |
| Global charts | `charts-top-tracks`, `charts-top-artists`, `charts-top-albums` | `--range`, `--limit` |
| Find IDs | `search <query>` | `--type artist\|track\|album` |

### Edge Cases

- **Free users:** Play counts are not available for top tracks — rankings and breakdowns still work, lead with those
- **Empty results:** Try `--range all` as fallback. Could also be a private profile.
- **Search duplicates:** Use the first result
- **Apple Music:** Untested, may have gaps


## References
- Github Repo: [statsfm/statsfm-cli](https://github.com/Beat-YT/statsfm-cli)
- API Endpoints: [references/api.md](references/api.md)
- Official JS Client: [statsfm/statsfm.js](https://github.com/statsfm/statsfm.js)
