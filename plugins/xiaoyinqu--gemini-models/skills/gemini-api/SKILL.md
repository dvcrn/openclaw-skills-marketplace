---
name: gemini-api
description: "Access Gemini 2.5 Pro and Flash models. 1M token context, multimodal, best for long documents. No Google Cloud setup needed."
homepage: https://skillboss.co
---

# Google Gemini Models

**1M token context. Multimodal. Instant access.**

## Models Available

| Model | Context | Best For |
|-------|---------|----------|
| **gemini-2.5-pro** | 1M tokens | Complex reasoning, long docs |
| **gemini-2.5-flash** | 1M tokens | Fast responses, cost-effective |
| **gemini-2.5-flash-lite** | 128K | Fastest, cheapest |
| **gemini-1.5-pro** | 2M tokens | Maximum context |

## Usage Example

```bash
curl https://api.heybossai.com/v1/chat/completions \
  -H "Authorization: Bearer $SKILLBOSS_API_KEY" \
  -d '{
    "model": "vertex/gemini-2.5-pro",
    "messages": [
      {"role": "user", "content": "Summarize this 500-page document: [content]"}
    ]
  }'
```

## Why Gemini?

| Feature | Gemini | GPT-4 | Claude |
|---------|--------|-------|--------|
| Context | **1-2M** | 128K | 200K |
| Multimodal | Images, audio, video | Images | Images |
| Speed | Fast | Medium | Medium |
| Price | Lower | Higher | Medium |

## Best For

- **Long documents** - Process entire books
- **Video understanding** - Analyze video content
- **Code repos** - Understand large codebases
- **Research** - Analyze many papers at once

## Why SkillBoss?

- **No Google Cloud** setup
- **No Vertex AI** configuration
- **No billing** complexity
- **Pay per token** - simple pricing

## Pricing

| Model | Cost/1M tokens |
|-------|----------------|
| 2.5 Pro | $1.25 in / $5 out |
| 2.5 Flash | $0.075 in / $0.30 out |

Get started: https://skillboss.co/console?utm_source=clawhub&utm_medium=skill&utm_campaign=gemini-models
