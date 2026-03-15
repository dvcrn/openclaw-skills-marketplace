# Music Analysis v2 Upgrade Notes

## Summary

This release upgrades the skill from a lightweight audio snapshot + temporal heuristic into a more producer-facing music listener with:
- groove/pocket analysis
- pulse stability and swing proxy
- section/repetition structure
- key clarity and harmonic tension
- explainable emotion modeling
- lyric-aware final vibe detection

## What Changed

### 1. Groove / Pulse
Added:
- tempo_bpm
- pulse_stability
- pulse_confidence
- swing_proxy
- pocket labels (`grid-locked`, `steady`, `push-pull / swung`, `loose / breathing`)

Why it matters:
BPM alone misses feel. This gives a better read on whether a track feels rigid, human, breathing, or pushed/pulled.

### 2. Structure
Added:
- section segmentation with A/B/C labels
- repeated section detection
- structure summaries like `A → B → A`

Important constraint:
These are similarity labels, not semantic claims like verse/chorus.

### 3. Harmony / Tension
Added:
- key estimate with mode
- key clarity
- chroma entropy
- harmonic change rate
- tonal motion
- tension score + tension description

Why it matters:
The skill can now distinguish stable/resolved passages from restless/unresolved ones instead of reducing everything to energy.

### 4. Explainable Emotion
Added:
- arousal / valence / tension style read
- explicit reasons grounded in measured features
- audio-layer explanation instead of black-box mood guessing

### 5. Lyric-Aware Final Vibe
Added:
- Whisper artifact filtering
- non-lyric segment rejection (`[MUSIC]`, `[BLANK_AUDIO]`, empty/bracket noise)
- lyric mood scoring from filtered text
- final emotional read that can become **lyrics-led** when the text is clearly darker, warmer, or more intense than the arrangement

Design principle:
If the lyrics are dark over bright music, the final vibe should still read dark.

## Pipeline (v2)

1. Run snapshot analysis (groove / timbre / structure / harmony)
2. Run Whisper and filter for real lyrics only
3. Run temporal listen over windows
4. Align lyrics to windows
5. Compute lyric mood
6. Combine lyric mood with audio emotion
7. Let lyrics override the final vibe when confidence is high

## Validation Notes

Validated on:
- `the-hum-ii.mp3` — instrumental; correctly falls back to audio-led mood
- `strength_of_a_young_man.mp3` — improved structure/timbre/tension reporting
- `back_to_the_old_house.mp3` — correctly shifts to lyric-led `dark / heavy`

## Files Added / Updated

Added:
- `scripts/music_analysis_v2.py`
- `references/v2-upgrade-notes.md`

Updated:
- `scripts/analyze_music.py`
- `scripts/temporal_listen.py`
- `scripts/listen.py`
- `SKILL.md`

## Backup

Pre-v2 backup created at:
- `~/.openclaw/backups/skills/music-analysis-pre-v2-20260310-200538`

## Commits

- `e964afc` — upgrade music-analysis skill to v2
- `a40acd1` — make music analyzer lyric-aware and filter Whisper artifacts
