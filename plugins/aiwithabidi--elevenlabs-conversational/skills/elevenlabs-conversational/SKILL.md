---
name: elevenlabs-conversational
description: "Full ElevenLabs platform integration — text-to-speech, voice cloning, and Conversational AI agent creation. Not just TTS — build interactive voice agents with emotion control, streaming audio, and phone system integration. Use for voice synthesis, cloning, or building conversational AI agents."
homepage: https://www.agxntsix.ai
---

# 🗣️ ElevenLabs Conversational

**Not just TTS — full Conversational AI.** Voice synthesis, cloning, and conversational AI agent creation for OpenClaw agents.

## Voice Synthesis vs Conversational AI

| Feature | Voice Synthesis (TTS) | Conversational AI |
|---------|----------------------|-------------------|
| What | Text → Speech | Full voice agent |
| Flow | One-way | Bidirectional |
| Use case | Narration, alerts | Phone agents, assistants |
| Latency | Batch OK | Real-time required |

Existing ElevenLabs skills only do TTS. This skill covers the **full platform** including Conversational AI agents.

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `ELEVENLABS_API_KEY` | ✅ | ElevenLabs API key |

## Quick Start

```bash
# List available voices
python3 {baseDir}/scripts/elevenlabs_api.py voices

# Text to speech
python3 {baseDir}/scripts/elevenlabs_api.py tts "Hello world" --voice Rachel --output hello.mp3

# TTS with emotion control
python3 {baseDir}/scripts/elevenlabs_api.py tts "I'm so excited!" --voice Rachel --stability 0.3 --style 0.8

# Streaming TTS (lower latency)
python3 {baseDir}/scripts/elevenlabs_api.py tts-stream "Hello world" --voice Rachel --output hello.mp3

# List conversational AI agents
python3 {baseDir}/scripts/elevenlabs_api.py list-agents

# Create a conversational AI agent
python3 {baseDir}/scripts/elevenlabs_api.py create-agent --name "Support Bot" --voice Rachel --prompt "You are a helpful support agent."

# Get agent details
python3 {baseDir}/scripts/elevenlabs_api.py get-agent <agent_id>

# Voice cloning (instant)
python3 {baseDir}/scripts/elevenlabs_api.py clone-voice "My Voice" --files sample1.mp3 sample2.mp3
```

## Commands

### `voices`
List all available voices with ID, name, category, and language.

### `tts <text>`
Convert text to speech (non-streaming).
- `--voice NAME` — voice name or ID (default: Rachel)
- `--output FILE` — output file path (default: output.mp3)
- `--model ID` — model (default: eleven_multilingual_v2)
- `--stability FLOAT` — 0.0-1.0, lower = more expressive (default: 0.5)
- `--similarity FLOAT` — 0.0-1.0, voice similarity boost (default: 0.75)
- `--style FLOAT` — 0.0-1.0, style exaggeration (default: 0.0)

### `tts-stream <text>`
Streaming TTS — lower latency, outputs as chunks arrive.
- Same options as `tts`

### `list-agents`
List all Conversational AI agents.

### `create-agent`
Create a new Conversational AI agent.
- `--name NAME` — agent name
- `--voice NAME` — voice to use
- `--prompt TEXT` — system prompt for the agent
- `--first-message TEXT` — greeting message
- `--language CODE` — language code (default: en)

### `get-agent <agent_id>`
Get details of a conversational AI agent.

### `clone-voice <name>`
Create an instant voice clone.
- `--files FILE [FILE ...]` — audio samples (minimum 1, recommended 3+)
- `--description TEXT` — voice description

## Integration Patterns

### With Twilio (Phone)
1. Create a Conversational AI agent
2. Configure Twilio webhook to point to ElevenLabs
3. Incoming calls route to your AI agent

### With Vapi
1. Create voice in ElevenLabs
2. Use voice ID in Vapi assistant config
3. Vapi handles orchestration, ElevenLabs handles voice

### With LiveKit
1. Generate TTS audio via streaming API
2. Publish audio track to LiveKit room
3. Subscribe to participant audio for STT pipeline

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
