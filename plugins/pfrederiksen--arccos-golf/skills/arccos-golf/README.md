# Arccos Golf Performance Analyzer

An OpenClaw skill that fetches live data from the Arccos Golf API and generates performance analysis: strokes gained, club distances, scoring patterns, pace of play, and recent rounds.

> **Unofficial.** Not affiliated with Arccos Golf LLC. Uses a reverse-engineered API. Use with your own account only.

## ⚠️ Before You Install

This skill makes **authenticated network requests** to Arccos Golf servers using your account credentials. Specifically:

- Your Arccos email and password are used to obtain a session token
- The token is cached at `~/.arccos_creds.json` (permissions 0600)
- Live API calls are made to `authentication.arccosgolf.com` and `api.arccosgolf.com`
- An external Python library (`arccos`) is installed from GitHub

**Review the `arccos` library source before installing:** <https://github.com/pfrederiksen/arccos-api>

If you prefer not to provide credentials, use `--file` with a pre-exported JSON file (offline mode — no network calls, no credentials required).

---

## Features

- Strokes Gained breakdown — overall, driving, approach, short game, putting
- Smart club distances (AI-filtered carry per club)
- Pace of play by course, color-coded by duration
- Recent rounds with date, score, and course name
- Current handicap index
- JSON output for piping into other tools

---

## Installation

```bash
# 1. Install the arccos library (required)
git clone https://github.com/pfrederiksen/arccos-api
pip install -e arccos-api/

# 2. Install this skill via ClawHub
clawhub install arccos-golf

# 3. Log in — prompts for email + password, caches token to ~/.arccos_creds.json
arccos login
```

**Prefer interactive login** (`arccos login`) over passing `--password` on the command line — command-line passwords can appear in process lists and shell history.

---

## Usage

```bash
# Full report (uses cached credentials)
python3 scripts/arccos_golf.py

# Pass credentials explicitly
python3 scripts/arccos_golf.py --email you@example.com --password secret

# Specific sections
python3 scripts/arccos_golf.py --summary
python3 scripts/arccos_golf.py --strokes-gained
python3 scripts/arccos_golf.py --clubs             # all clubs
python3 scripts/arccos_golf.py --clubs iron         # filter by type
python3 scripts/arccos_golf.py --pace
python3 scripts/arccos_golf.py --recent-rounds 10

# JSON output
python3 scripts/arccos_golf.py --format json

# Offline mode — no credentials, no network (requires pre-exported JSON)
python3 scripts/arccos_golf.py --file /path/to/arccos-data.json
```

---

## Network & Credential Access

| What | Details |
|------|---------|
| Login endpoint | `POST authentication.arccosgolf.com/accessKeys` |
| Token refresh | `POST authentication.arccosgolf.com/tokens` |
| Rounds | `GET api.arccosgolf.com/users/{id}/rounds` |
| Courses | `GET api.arccosgolf.com/courses/{id}` |
| Handicap | `GET api.arccosgolf.com/users/{id}/handicaps/latest` |
| Club distances | `GET api.arccosgolf.com/v4/clubs/user/{id}/smart-distances` |
| Strokes gained | `GET api.arccosgolf.com/v2/sga/shots/{roundIds}` |
| Credential cache | `~/.arccos_creds.json` (read + written, mode 0600) |

No other network calls are made. Delete `~/.arccos_creds.json` when you're done if you want to remove cached tokens.

---

## Dependencies

- Python ≥ 3.11
- [`arccos`](https://github.com/pfrederiksen/arccos-api) library — MIT licensed, wraps `requests`, `click`, `rich`
- Standard library only in the analysis script itself

---

## License

MIT

## Related

- [arccos-api](https://github.com/pfrederiksen/arccos-api) — the underlying API library this skill uses
- [OpenClaw](https://github.com/openclaw/openclaw) — AI-powered CLI assistant
