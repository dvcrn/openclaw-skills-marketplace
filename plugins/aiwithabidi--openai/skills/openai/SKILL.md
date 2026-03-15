---
name: openai
description: "OpenAI API integration — chat completions, embeddings, image generation, audio transcription, file management, fine-tuning, and assistants via the OpenAI REST API. Generate text, create images with DALL-E, transcribe audio with Whisper, manage fine-tuning jobs, and build AI assistants. Built for AI agents — Python stdlib only, zero dependencies. Use for AI text generation, image creation, speech-to-text, embeddings, fine-tuning, and AI assistant building."
homepage: https://www.agxntsix.ai
---

# 🧠 OpenAI

OpenAI API integration — chat completions, embeddings, image generation, audio transcription, file management, fine-tuning, and assistants via the OpenAI REST API.

## Features

- **Chat completions** — GPT-4o, GPT-5, o1 model responses
- **Embeddings** — text-embedding-3 for semantic search
- **Image generation** — DALL-E 3 image creation and editing
- **Audio transcription** — Whisper speech-to-text
- **Text-to-speech** — TTS with multiple voices
- **File management** — upload and manage files
- **Fine-tuning** — create and manage fine-tuning jobs
- **Assistants** — build and manage AI assistants
- **Moderation** — content moderation checks
- **Models** — list available models and details

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ | API key/token for OpenAI |

## Quick Start

```bash
# Send chat completion
python3 {baseDir}/scripts/openai.py chat "Explain quantum computing in 3 sentences" --model gpt-4o
```

```bash
# Chat with system prompt
python3 {baseDir}/scripts/openai.py chat-system --system "You are a Python expert" "How do I use asyncio?"
```

```bash
# Generate embeddings
python3 {baseDir}/scripts/openai.py embed "The quick brown fox" --model text-embedding-3-small
```

```bash
# Generate an image
python3 {baseDir}/scripts/openai.py image "A sunset over mountains, oil painting style" --size 1024x1024
```



## Commands

### `chat`
Send chat completion.
```bash
python3 {baseDir}/scripts/openai.py chat "Explain quantum computing in 3 sentences" --model gpt-4o
```

### `chat-system`
Chat with system prompt.
```bash
python3 {baseDir}/scripts/openai.py chat-system --system "You are a Python expert" "How do I use asyncio?"
```

### `embed`
Generate embeddings.
```bash
python3 {baseDir}/scripts/openai.py embed "The quick brown fox" --model text-embedding-3-small
```

### `image`
Generate an image.
```bash
python3 {baseDir}/scripts/openai.py image "A sunset over mountains, oil painting style" --size 1024x1024
```

### `transcribe`
Transcribe audio file.
```bash
python3 {baseDir}/scripts/openai.py transcribe recording.mp3
```

### `tts`
Text to speech.
```bash
python3 {baseDir}/scripts/openai.py tts "Hello, welcome to our service" --voice alloy --output greeting.mp3
```

### `models`
List available models.
```bash
python3 {baseDir}/scripts/openai.py models
```

### `model-get`
Get model details.
```bash
python3 {baseDir}/scripts/openai.py model-get gpt-4o
```

### `files`
List uploaded files.
```bash
python3 {baseDir}/scripts/openai.py files
```

### `file-upload`
Upload a file.
```bash
python3 {baseDir}/scripts/openai.py file-upload data.jsonl --purpose fine-tune
```

### `fine-tune`
Create fine-tuning job.
```bash
python3 {baseDir}/scripts/openai.py fine-tune '{"training_file":"file-abc123","model":"gpt-4o-mini"}'
```

### `fine-tune-list`
List fine-tuning jobs.
```bash
python3 {baseDir}/scripts/openai.py fine-tune-list
```

### `moderate`
Check content moderation.
```bash
python3 {baseDir}/scripts/openai.py moderate "Some text to check"
```

### `usage`
Check API usage.
```bash
python3 {baseDir}/scripts/openai.py usage --date 2026-02-01
```

### `assistants`
List assistants.
```bash
python3 {baseDir}/scripts/openai.py assistants
```


## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
# JSON (default, for programmatic use)
python3 {baseDir}/scripts/openai.py chat --limit 5

# Human-readable
python3 {baseDir}/scripts/openai.py chat --limit 5 --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/openai.py` | Main CLI — all OpenAI operations |

## Data Policy

This skill **never stores data locally**. All requests go directly to the OpenAI API and results are returned to stdout. Your data stays on OpenAI servers.

## Credits
---
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
