---
name: ai-voice-studio
description: "AI Voice Studio"
---

# AI Voice Studio

> Text-to-Speech & Speech-to-Text with ElevenLabs, OpenAI, and more. Natural voices, multiple languages, one API.

## Description

AI Voice Studio provides OpenClaw agents with professional voice synthesis (TTS) and transcription (STT) capabilities through a unified API. Access ElevenLabs, OpenAI Whisper, and more premium voice services.

**Features:**
- 🎙️ **Natural TTS**: ElevenLabs multilingual voices, OpenAI voices
- 📝 **Accurate STT**: OpenAI Whisper for transcription
- 🌍 **Multi-language**: 29+ languages supported
- ⚡ **Fast**: Real-time streaming available
- 💰 **Affordable**: Up to 50% cheaper than direct API

## When to Use

Activate this skill when the user wants to:
- Convert text to speech / generate voiceover
- Transcribe audio or video
- Create podcasts or audiobooks
- Add voice to videos or presentations
- Build voice-enabled applications

**Trigger phrases**: "text to speech", "tts", "voice", "read aloud", "transcribe", "speech to text", "stt", "voiceover", "narration"

## Quick Start

### Text-to-Speech (TTS)

```bash
# ElevenLabs - Most natural
curl -X POST "https://api.heybossai.com/v1/audio/speech" \
  -H "Authorization: Bearer $API_HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "elevenlabs/eleven_multilingual_v2",
    "input": "Hello, this is AI Voice Studio!",
    "voice": "rachel"
  }' --output speech.mp3

# OpenAI TTS - Fast & reliable
curl -X POST "https://api.heybossai.com/v1/audio/speech" \
  -H "Authorization: Bearer $API_HUB_API_KEY" \
  -d '{
    "model": "openai/tts-1",
    "input": "Hello world!",
    "voice": "alloy"
  }' --output speech.mp3
```

### Speech-to-Text (STT)

```bash
# OpenAI Whisper - Best accuracy
curl -X POST "https://api.heybossai.com/v1/audio/transcriptions" \
  -H "Authorization: Bearer $API_HUB_API_KEY" \
  -F "model=openai/whisper-1" \
  -F "file=@audio.mp3"
```

## Available Voices

### ElevenLabs (Premium Natural)
| Voice | Description | Best For |
|-------|-------------|----------|
| rachel | Young female, conversational | Podcasts, videos |
| adam | Middle-aged male, deep | Narration, audiobooks |
| bella | Young female, soft | ASMR, meditation |
| antoni | Young male, American | Marketing, explainers |

### OpenAI
| Voice | Description |
|-------|-------------|
| alloy | Neutral, versatile |
| echo | Male, warm |
| fable | British male |
| onyx | Deep male |
| nova | Female, friendly |
| shimmer | Female, clear |

## Languages

ElevenLabs supports: English, Spanish, French, German, Italian, Portuguese, Polish, Hindi, Japanese, Korean, Chinese, Arabic, and 17+ more.

OpenAI Whisper supports: 100+ languages for transcription.

## Pricing Comparison

| Service | Direct Price | SkillBoss Price | Savings |
|---------|-------------|-----------------|---------|
| ElevenLabs TTS | $0.30/1K chars | $0.18/1K chars | 40% |
| OpenAI TTS-1 | $0.015/1K chars | $0.015/1K chars | - |
| OpenAI TTS-1-HD | $0.030/1K chars | $0.030/1K chars | - |
| OpenAI Whisper | $0.006/min | $0.006/min | - |

## Use Cases

### 1. Podcast Generator
```python
# Generate podcast episode from script
text = "Welcome to Tech Today. In this episode..."
response = requests.post(
    "https://api.heybossai.com/v1/audio/speech",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "model": "elevenlabs/eleven_multilingual_v2",
        "input": text,
        "voice": "rachel"
    }
)
```

### 2. Video Voiceover
```bash
# Create voiceover for video
curl -X POST "https://api.heybossai.com/v1/audio/speech" \
  -H "Authorization: Bearer $API_HUB_API_KEY" \
  -d '{
    "model": "openai/tts-1-hd",
    "input": "Introducing our new product...",
    "voice": "onyx"
  }' -o voiceover.mp3
```

### 3. Meeting Transcription
```bash
# Transcribe meeting recording
curl -X POST "https://api.heybossai.com/v1/audio/transcriptions" \
  -H "Authorization: Bearer $API_HUB_API_KEY" \
  -F "model=openai/whisper-1" \
  -F "file=@meeting.mp3" \
  -F "language=en"
```

## Setup

1. Get your API key at [skillboss.co](https://skillboss.co)
2. New users get **$5 free credits**
3. Set: `export API_HUB_API_KEY="your-key"`

## Related Skills

- [flux-image-gen](https://clawhub.ai/xiaoyinqu/flux-image-gen) - AI image generation
- [api-hub-gateway](https://clawhub.ai/xiaoyinqu/api-hub-gateway) - 100+ AI models

---

*Powered by [SkillBoss API Hub](https://skillboss.co) - 100+ AI Models, One API*
