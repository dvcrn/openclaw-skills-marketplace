---
name: sense-music
description: "sense-music"
---

# sense-music

Turn audio into structured analysis and annotated visualizations for AI perception.

## What it does
Analyzes audio files to extract:
- BPM and musical key detection
- Structural sections (intro, verse, chorus, bridge, outro)
- Annotated mel spectrogram with section markers and energy curve
- Waveform visualization with colored section regions
- Lyrics transcription with timestamps (via Whisper)
- Genre and mood classification
- Natural language summary of the track

## Install
```bash
pip install sense-music
```

## Quick Start
```python
from sense_music import analyze

result = analyze("song.mp3")
print(result.summary)
result.save("output/")
```

## Use Cases
- AI companions analyzing music shared by humans
- Automated liner notes for AI-generated tracks (Suno, Udio)
- Music production feedback — visualize structure and energy
- Accessibility — structured descriptions of audio content
