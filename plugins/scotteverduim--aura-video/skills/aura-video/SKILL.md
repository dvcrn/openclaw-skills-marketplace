---
name: aura-video
description: "Generate a complete Aura Creatine TikTok/Instagram video from a JSON script. Reads the script from Google Drive, generates A-roll (Kristina image-to-video via AIML), B-roll (text-to-video via Gemini Veo), and animation scenes (Remotion), then merges everything with voiceover and captions into a final 9:16 MP4."
---

# Aura Video Generator

Generate a complete Aura Creatine video from a single script ID.

## Usage

```bash
bash {baseDir}/scripts/aura_video.sh week1_day1_vid1
```

Replace `week1_day1_vid1` with any script ID from `Google Drive/Aura Creatine/Content Pipeline/01_Scripts/`.

## How it works

1. **Load JSON script** from Google Drive (`Content Pipeline/01_Scripts/<id>.json`)
2. **Generate each scene** based on `type` field:
   - `a-roll` → AIML image-to-video (Kristina base image + prompt)
   - `b-roll` → Gemini Veo text-to-video (prompt only)
   - `animation` → Gemini Veo text-to-video (prompt only, animation style)
3. **Load voiceover** MP3 from Google Drive (`voiceovers/` folder)
4. **Merge scenes** with FFmpeg: concatenate clips, add voiceover, add captions
5. **Upload final video** to Google Drive (`Content Pipeline/03_Final_Videos/`)
6. **Send video** back to the chat

## Script JSON format

```json
{
  "meta": {
    "id": "week1_day1_vid1",
    "title": "Why Women Need Creatine More"
  },
  "assets": {
    "kristina_base_image": "Brand Kit/kristina_reference_primary.png",
    "voiceover_mp3": "voiceovers/Vid 1 Why Women Need Creatine More.mp3",
    "voiceover_text": "Did you know that women naturally have 70-80% lower creatine stores...",
    "on_screen_captions": ["Women have 70-80% less creatine", "Bridge the energy gap", "Start with 3-5g daily"]
  },
  "scenes": [
    { "scene": 1, "type": "a-roll", "prompt": "Kristina sits at kitchen table...", "caption": "Women have 70-80% less creatine", "duration_seconds": 8 },
    { "scene": 2, "type": "b-roll", "prompt": "Animated bar chart showing women vs men creatine levels...", "caption": "Bridge the energy gap", "duration_seconds": 8 },
    { "scene": 3, "type": "a-roll", "prompt": "Kristina focused, smiling, typing on laptop...", "caption": "Start with 3-5g daily", "duration_seconds": 8 }
  ]
}
```

## Available scripts

All scripts are in `Google Drive/Aura Creatine/Content Pipeline/01_Scripts/`:
- `week1_day1_vid1` — Why Women Need Creatine More
- `week1_day2_vid1` — The Creatine Myth Debunked
- `week1_day3_vid1` — Creatine Against Brain Fog
- `week1_day4_vid1` — Sleep Almost An Hour Longer
- `week1_day5_vid1` — Creatine & Depression
- `week1_day6_vid1` — Constantly Feeling Rushed
- `week1_day7_vid1` — Better Memory

## Notes

- All videos are rendered in 9:16 (vertical) format for TikTok/Instagram Reels
- A-roll scenes use the Kristina base image from `Brand Kit/`
- Voiceover MP3s are pre-recorded and loaded from Google Drive (no ElevenLabs cost)
- Final video is ~24 seconds (3 scenes × 8 seconds)
- Output is uploaded to `Content Pipeline/03_Final_Videos/` and sent to chat
