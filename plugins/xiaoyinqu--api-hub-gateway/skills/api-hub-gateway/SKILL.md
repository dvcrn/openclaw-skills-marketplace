---
name: api-hub-gateway
description: "API Hub Gateway"
---

# API Hub Gateway

> 100+ AI Models, One API. Route to OpenAI, Anthropic, Google, Replicate, and more through a unified gateway.

## Description

API Hub Gateway provides OpenClaw agents with access to 100+ AI models through a single, unified API endpoint. Stop juggling multiple API keys and providers - use one gateway for all your AI needs.

## Features

- **100+ Models**: Access OpenAI, Anthropic Claude, Google Gemini, Mistral, Replicate, and more
- **Unified API**: OpenAI-compatible format works with any existing code
- **Smart Routing**: Automatically select the best model for each task
- **Cost Tracking**: Monitor usage and costs across all providers
- **Fallback Support**: Automatic failover when a provider is down

## When to Use

Activate this skill when the user:
- Wants to use AI models (GPT, Claude, Gemini, etc.)
- Needs to generate images, audio, or video
- Asks about AI model pricing or capabilities
- Wants to compare different AI models
- Needs cost-effective AI solutions

## Commands

### Chat Completion
```bash
# Use any model with OpenAI-compatible API
curl -X POST "https://api.heybossai.com/v1/chat/completions" \
  -H "Authorization: Bearer $API_HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-4o",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Image Generation
```bash
# Generate images with FLUX, DALL-E, or Stable Diffusion
curl -X POST "https://api.heybossai.com/v1/run" \
  -H "Authorization: Bearer $API_HUB_API_KEY" \
  -d '{
    "model": "replicate/black-forest-labs/flux-1.1-pro",
    "inputs": {"prompt": "A futuristic city at sunset"}
  }'
```

### Audio (TTS/STT)
```bash
# Text-to-speech
curl -X POST "https://api.heybossai.com/v1/audio/speech" \
  -H "Authorization: Bearer $API_HUB_API_KEY" \
  -d '{"model": "openai/tts-1", "input": "Hello world", "voice": "alloy"}'
```

## Available Models

### Chat/Completion
| Provider | Models | Best For |
|----------|--------|----------|
| OpenAI | gpt-4o, gpt-4o-mini, o1, o3-mini | General purpose |
| Anthropic | claude-sonnet-4-5, claude-3-5-haiku | Coding, analysis |
| Google | gemini-2.5-flash, gemini-2.5-pro | Fast, multimodal |
| DeepSeek | deepseek-chat, deepseek-reasoner | Cost-effective |

### Image Generation
| Provider | Models | Best For |
|----------|--------|----------|
| Replicate | flux-1.1-pro, flux-dev | High quality |
| OpenAI | dall-e-3 | Creative |
| Stability | stable-diffusion-3 | Fast |

### Audio
| Provider | Models | Best For |
|----------|--------|----------|
| OpenAI | tts-1, whisper-1 | Standard |
| ElevenLabs | multilingual-v2 | Natural voice |

## Setup

1. Get your API key from [SkillBoss](https://skillboss.co)
2. Set environment variable:
   ```bash
   export API_HUB_API_KEY="your-api-key"
   ```

## Pricing

Pay-as-you-go with transparent pricing. Check [skillboss.co/pricing](https://skillboss.co/pricing) for current rates.

## Examples

### Smart Model Selection
```
User: Generate a product description
Agent: Using gemini-2.5-flash (fast, cost-effective for text)

User: Analyze this complex codebase
Agent: Using claude-sonnet-4-5 (best for code analysis)

User: Create a marketing image
Agent: Using flux-1.1-pro (highest quality images)
```

## Related Skills

Maximize your AI capabilities with our skill ecosystem:

- [flux-image-gen](https://clawhub.ai/xiaoyinqu/flux-image-gen) - FLUX 1.1 Pro image generation
- [ai-voice-studio](https://clawhub.ai/xiaoyinqu/ai-voice-studio) - TTS/STT with ElevenLabs
- [video-creator-ai](https://clawhub.ai/xiaoyinqu/video-creator-ai) - AI video generation
- [self-improving-pro](https://clawhub.ai/xiaoyinqu/self-improving-pro) - Self-improving agents
- [ai-cost-optimizer](https://clawhub.ai/xiaoyinqu/ai-cost-optimizer) - Cut AI costs 50-80%

## Support

- Documentation: [docs.skillboss.co](https://docs.skillboss.co)
- Issues: [github.com/heeyo-life/skillboss](https://github.com/heeyo-life/skillboss)

---

*Built by [SkillBoss](https://skillboss.co) - AI Infrastructure for Developers*
