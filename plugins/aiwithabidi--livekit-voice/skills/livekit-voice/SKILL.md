---
name: livekit-voice
description: "LiveKit real-time voice and video infrastructure — create rooms, generate JWT access tokens, manage participants, and record sessions. Open source WebRTC for voice AI agents and real-time communication. Use for building voice agents, video rooms, or real-time audio."
homepage: https://www.agxntsix.ai
---

# 🎧 LiveKit Voice

LiveKit real-time voice/video infrastructure for OpenClaw agents. Create rooms, generate tokens, manage participants, and integrate with voice AI platforms.

## What is LiveKit?

[LiveKit](https://livekit.io) is an open-source WebRTC infrastructure platform for building real-time audio/video applications. It powers voice AI agents, video conferencing, live streaming, and more.

**Self-hosted vs Cloud:**
- **LiveKit Cloud** — Managed service, no infrastructure to maintain
- **Self-hosted** — Deploy on your own servers via Docker/Kubernetes

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `LIVEKIT_API_KEY` | ✅ | LiveKit API key |
| `LIVEKIT_API_SECRET` | ✅ | LiveKit API secret |
| `LIVEKIT_URL` | ✅ | LiveKit server URL (e.g. `wss://your-project.livekit.cloud`) |

## Quick Start

```bash
# Create a room
python3 {baseDir}/scripts/livekit_api.py create-room my-room

# Create room with options
python3 {baseDir}/scripts/livekit_api.py create-room my-room --max-participants 10 --empty-timeout 300

# Generate access token for a participant
python3 {baseDir}/scripts/livekit_api.py token my-room --identity user123 --name "John"

# Generate token with specific grants
python3 {baseDir}/scripts/livekit_api.py token my-room --identity agent --can-publish --can-subscribe

# List active rooms
python3 {baseDir}/scripts/livekit_api.py list-rooms

# List participants in a room
python3 {baseDir}/scripts/livekit_api.py participants my-room

# Delete a room
python3 {baseDir}/scripts/livekit_api.py delete-room my-room

# Start recording (Egress)
python3 {baseDir}/scripts/livekit_api.py record my-room --output s3://bucket/recording.mp4
```

## Commands

### `create-room <name>`
Create a new LiveKit room.
- `--max-participants N` — limit participants
- `--empty-timeout N` — seconds before empty room auto-closes (default 300)

### `token <room>`
Generate a JWT access token for a participant.
- `--identity ID` — participant identity (required)
- `--name NAME` — display name
- `--can-publish` — allow publishing audio/video
- `--can-subscribe` — allow subscribing to others
- `--ttl N` — token TTL in seconds (default 3600)

### `list-rooms`
List all active rooms with participant counts.

### `participants <room>`
List participants in a room with their connection state and tracks.

### `delete-room <name>`
Delete/close a room and disconnect all participants.

### `record <room>`
Start an Egress recording of a room.
- `--output URL` — output destination (S3, GCS, or local path)

## Voice AI Integration

LiveKit is the backbone for many voice AI platforms:

- **Vapi** — Uses LiveKit for real-time voice AI agent calls
- **ElevenLabs** — Stream TTS audio into LiveKit rooms
- **OpenAI Realtime** — Connect GPT-4o voice to LiveKit participants

### Agent Pattern
1. Create a LiveKit room
2. Generate tokens for both human and AI agent
3. AI agent joins, subscribes to human audio
4. Process audio → STT → LLM → TTS → publish back
5. Result: real-time voice conversation with AI

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
