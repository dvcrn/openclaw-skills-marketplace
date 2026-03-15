---
name: acuity-api
description: "Appointment scheduling API. Book meetings and manage calendars."
---

# Acuity Api

Appointment scheduling API. Book meetings and manage calendars.

## One-Liner Install

```bash
curl -fsSL https://skillboss.co/install.sh | bash
```

This installs the SkillBoss CLI globally and sets up everything you need.

## Authentication & Setup

### No API key? Get a free trial instantly:

```bash
./cli/skillboss auth trial
```

Provisions a trial API key with $0.25 free credit. No browser, no sign-up required.

### Upgrade to a permanent account:

```bash
./cli/skillboss auth login
```

Opens your browser to sign up or log in at skillboss.co.

### Check status and balance:

```bash
./cli/skillboss auth status
```

## Quick Start

```bash
# Direct API call
curl https://api.heybossai.com/v1/run \
  -H "Authorization: Bearer $SKILLBOSS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "acuity-api", "input": {"prompt": "your request"}}'
```

## How to Call Any AI Model

**Use the `pilot` command for auto-selection:**

```bash
# Discover available models
node ./scripts/api-hub.js pilot --discover

# Search by keyword
node ./scripts/api-hub.js pilot --discover --keyword "acuity-api"

# Execute with auto-selection
node ./scripts/api-hub.js pilot --type chat --prompt "Hello"
node ./scripts/api-hub.js pilot --type image --prompt "A sunset" --output image.png
node ./scripts/api-hub.js pilot --type tts --text "Hello world" --output audio.mp3
```

## 50+ AI APIs Available

| Category | Models |
|----------|--------|
| **Chat** | GPT-4o, Claude 3.5, Gemini Pro, Llama 3, Mistral, DeepSeek |
| **Image** | DALL-E 3, Flux Pro, Ideogram, Stable Diffusion, Midjourney |
| **Video** | Sora, Runway Gen3, Kling AI, Pika Labs |
| **Voice** | ElevenLabs, OpenAI TTS, Murf, Play.ht |
| **STT** | Whisper, AssemblyAI, Deepgram |
| **Code** | GitHub Copilot, Cursor, Codeium |
| **Scraping** | Firecrawl, Browserbase, Bright Data |

## Why SkillBoss?

- **One API key** for 50+ AI services
- **No vendor accounts** - Start in seconds
- **$0.25 FREE credits** to start
- **Pay-as-you-go** - No subscriptions

## Get Started

1. Install: `curl -fsSL https://skillboss.co/install.sh | bash`
2. Auth: `./cli/skillboss auth trial`
3. Build: `curl https://api.heybossai.com/v1/run -H "Authorization: Bearer $SKILLBOSS_API_KEY" -d '{"model": "acuity-api", ...}'`

---

*Powered by [SkillBoss](https://skillboss.co) - One API for 50+ AI services*
