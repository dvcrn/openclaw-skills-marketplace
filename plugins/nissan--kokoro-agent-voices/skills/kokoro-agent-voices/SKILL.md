---
name: kokoro-agent-voices
description: "Local zero-cost text-to-speech with per-agent voice profiles using Kokoro TTS (82M params). 54 voices available, named agent mappings, WAV output. Use when building voice-enabled agents without API costs. Requires espeak-ng and a Python environment with kokoro dependencies."
---

# Kokoro Agent Voices

Give each AI agent a distinct voice using Kokoro TTS — a lightweight 82M parameter model that runs locally with zero API costs. 54 voices across American, British, and other accents.

## Agent Voice Profiles

```python
AGENT_VOICES = {
    "loki": "am_fenrir",      # Deep, authoritative
    "archie": "bm_george",    # British analytical
    "sara": "af_bella",       # Warm, creative
    "kit": "am_echo",         # Clear, technical
    "liv": "af_nova",         # Bright, energetic
    "belle": "bf_emma",       # Refined, thoughtful
}
```

## Usage

```bash
python3 scripts/speak.py --agent loki "System check complete"
python3 scripts/speak.py --voice af_bella "Hello world" --output /tmp/greeting.wav
python3 scripts/speak.py --list-voices    # Show all 54 voices
python3 scripts/speak.py --list-agents    # Show configured agent profiles
```

## Setup

Requires a Python environment with `kokoro`, `soundfile`, and `espeak-ng` installed. The model downloads automatically from Hugging Face on first use (~350MB).

## Files

- `scripts/speak.py` — TTS script with agent profiles and voice selection
