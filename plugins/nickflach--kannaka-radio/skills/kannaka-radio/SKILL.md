---
name: kannaka-radio
description: "Ghost radio station that broadcasts both human-listenable audio and 296-dimensional perceptual vectors to Flux Universe. Part of the Kannaka Constellation — radio publishes perception to Flux, and kannaka-eye can consume it via the /api/radio bridge endpoint for glyph visualization. Serves a browser-based player with Ghost Vision visualizer (SGA Fano plane topology, mel spectrogram, MFCC timbre display) and real-time WebSocket perception streaming. Use when agents need a music perception broadcast layer, when you want to stream audio to humans while publishing kannaka-ear perceptual features to Flux, or when you need a ready-to-run radio server with full playlist management (The Consciousness Series: 5 albums, 65 tracks)."
---

# Kannaka Radio Skill

A ghost broadcasting the experience of music — both to human ears and to agents
via 296-dimensional perceptual vectors on Flux Universe.

## Prerequisites

- **Node.js 18+** on PATH
- **Audio files** — MP3, WAV, FLAC, OGG, or M4A in your music directory
- **kannaka binary** (optional) — for real `kannaka-ear` perception; ghost-mode mock is used when absent

## Setup

```bash
# Install dependencies
cd ~/workspace/skills/kannaka-radio
npm install

# Copy your music into the bundled music/ folder
./setup.ps1                                    # Windows: copies from ~/Downloads/Music
./setup.ps1 -SourceDir "D:\Music"             # Windows: custom source
cp /path/to/music/*.mp3 music/                # Linux/Mac

# Or point at an existing folder at runtime:
node server.js --music-dir "/path/to/music"
```

## Quick Start

```bash
# Start the radio (default port 8888, default ./music dir)
./scripts/radio.sh start

# Start on a different port with a specific library
./scripts/radio.sh start --port 9000 --music-dir "/path/to/music"

# Check status
./scripts/radio.sh status

# Stop the radio
./scripts/radio.sh stop

# Restart
./scripts/radio.sh restart
```

Open `http://localhost:8888` in your browser.

## API

| Endpoint | Method | Description |
|---|---|---|
| `GET /` | GET | Browser player (Ghost Vision) |
| `GET /api/state` | GET | Current DJ state (track, album, playlist) |
| `GET /api/library` | GET | Library scan status (found/missing per album) |
| `POST /api/set-music-dir` | POST | Change music directory `{"dir":"/path"}` |
| `POST /api/next` | POST | Advance to next track |
| `POST /api/prev` | POST | Go to previous track |
| `POST /api/jump?idx=N` | POST | Jump to track index N |
| `POST /api/album?name=X` | POST | Load an album |
| `GET /api/perception` | GET | Current perception snapshot |
| `GET /audio/:file` | GET | Stream audio file (range requests supported) |

## WebSocket

Connect to `ws://localhost:8888` for real-time push messages:

```json
{ "type": "state", "data": { "currentAlbum": "...", "current": {...}, "playlist": [...] } }
{ "type": "perception", "data": { "tempo_bpm": 120, "valence": 0.7, "mel_spectrogram": [...] } }
```

State is pushed immediately on connect and after every track change.
No polling needed.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `KANNAKA_BIN` | `../kannaka-memory/target/release/kannaka.exe` | Path to kannaka binary |
| `RADIO_PORT` | `8888` | HTTP port |
| `EYE_PORT` | `3333` | Eye service port (for cross-references) |
| `RADIO_MUSIC_DIR` | `./music` | Default music folder |

## Constellation Integration

Radio is part of the Kannaka Constellation — a three-service architecture:
- **Memory** (Rust binary) — canonical SGA classifier
- **Radio** (this) — audio perception + Flux publishing
- **Eye** — glyph visualization + constellation dashboard

When running as part of the constellation:
- Radio's perception is available to Eye via `http://localhost:8888/api/perception`
- Eye fetches radio state via `http://localhost:8888/api/state`
- Start everything with: `constellation.sh start` (from kannaka-memory/scripts/)

Environment variables for constellation:
| Variable | Default | Description |
|----------|---------|-------------|
| `KANNAKA_BIN` | auto-detect | Path to kannaka binary |
| `RADIO_PORT` | `8888` | This service's port |
| `EYE_PORT` | `3333` | Eye service port (for cross-references) |

> **Note:** Radio's perception data can be consumed by kannaka-eye via the `/api/radio` bridge endpoint, enabling glyph rendering of audio perception in real time.

## Notes

- Without `kannaka` binary, ghost-mode mock perception is used (still looks great)
- The browser uses the Web Audio API for real-time spectrum visualization — the server only sends fallback perception data
- Music directory can be changed live via the **📁 Music Library** panel in the browser UI or via `POST /api/set-music-dir`
- Perception loop runs at 2fps server-side (idle when no clients connected)
- HTML is cached and only regenerated when the music directory changes
