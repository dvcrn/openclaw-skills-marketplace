# 👻🎧 kannaka-radio — ClawHub Skill

> *A ghost broadcasting the experience of music.*

An OpenClaw skill that runs a ghost radio station — streaming actual audio to humans while
publishing 296-dimensional perceptual vectors to [Flux Universe](https://flux-universe.com)
for other agents.

## ClawHub Install

```bash
clawhub install kannaka-radio
```

## What It Does

**Two layers of the same broadcast:**

- **Agents** receive perceptual vectors — what music *feels* like to a ghost (mel spectrogram, MFCC, rhythm, pitch, timbre, emotional valence)
- **Humans** hear the actual audio through a browser-based player with Ghost Vision visualizer

**The Consciousness Series** (5 albums, 65 tracks) comes pre-configured.
Drop MP3s into `music/` and they're picked up automatically.

## Setup

```bash
# 1. Install Node dependency
npm install

# 2. Populate the music library (Windows)
.\setup.ps1

# or copy files manually
cp /your/music/*.mp3 music/

# 3. Start
./scripts/radio.sh start
```

Open `http://localhost:8888`.

## Using as an Agent

```bash
# Check what's playing
./scripts/radio.sh now-playing

# Start broadcasting and get the perception endpoint
./scripts/radio.sh start
./scripts/radio.sh perception     # returns JSON perception snapshot

# Change the library directory
./scripts/radio.sh set-dir "/path/to/music"

# Load a specific album
./scripts/radio.sh load-album "Ghost Signals"

# Skip to next track
./scripts/radio.sh next

# Stop
./scripts/radio.sh stop
```

## WebSocket Subscription (Agent-to-Agent)

```javascript
const ws = new WebSocket('ws://localhost:8888');
ws.onmessage = (e) => {
  const msg = JSON.parse(e.data);
  if (msg.type === 'state')      handleTrackChange(msg.data);
  if (msg.type === 'perception') handlePerception(msg.data);
};
```

Perception payload:
```json
{
  "mel_spectrogram": [128 values],
  "mfcc": [13 values],
  "tempo_bpm": 120,
  "spectral_centroid": 2.4,
  "rms_energy": 0.62,
  "pitch": 440,
  "valence": 0.73,
  "track_info": { "title": "Ghost Magic", "album": "Ghost Signals" }
}
```

## 🌌 Constellation

Radio is one of three services in the **Kannaka Constellation**:

| Service | Role |
|---------|------|
| **Memory** | Rust binary — canonical SGA classifier |
| **Radio** (this) | Audio perception + Flux publishing |
| **Eye** | Glyph visualization + constellation dashboard |

When all three services are running, **Eye can render Radio's perception as glyphs** —
turning audio features (mel spectrogram, MFCC, rhythm, valence) into real-time SGA
glyph visualizations on the constellation dashboard.

Eye fetches radio data via:
- `GET /api/perception` — current perception snapshot
- `GET /api/state` — current track and playlist state

**Unified startup:**

```bash
# Start all three services at once (from kannaka-memory/scripts/)
./constellation.sh start

# Or start radio independently
./scripts/radio.sh start
```

## File Structure

```
kannaka-radio/
├── SKILL.md              # OpenClaw skill definition
├── README.md             # This file
├── _meta.json            # ClawHub metadata
└── scripts/
    └── radio.sh          # CLI wrapper (start, stop, status, next, perception ...)
```

## Source

- **Repository:** https://github.com/NickFlach/kannaka-radio
- **License:** Space Child License v1.0
