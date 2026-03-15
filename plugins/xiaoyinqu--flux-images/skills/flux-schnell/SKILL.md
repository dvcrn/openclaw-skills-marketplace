---
name: flux-schnell
description: "Generate images with Black Forest Labs Flux. Models: flux-schnell (fast), flux-dev (quality). Best open-source image model."
homepage: https://skillboss.co
---

# Flux Image Generation

**Best open-source image model, made easy.**

## Models Available

| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| **flux-schnell** | ~1s | Great | Iteration, drafts |
| **flux-dev** | ~10s | Best | Final output |

## Usage Example

```bash
curl https://api.heybossai.com/v1/run \
  -H "Authorization: Bearer $SKILLBOSS_API_KEY" \
  -d '{
    "model": "flux-schnell",
    "input": {
      "prompt": "A cozy coffee shop interior, morning light streaming through windows, plants on shelves, warm colors",
      "aspect_ratio": "16:9"
    }
  }'
```

## Parameters

| Parameter | Options |
|-----------|---------|
| **aspect_ratio** | 1:1, 16:9, 9:16, 4:3, 3:4 |
| **num_outputs** | 1-4 images |
| **seed** | For reproducibility |

## Why Flux?

- **Photorealistic** - Best quality among open models
- **Text rendering** - Actually readable text in images
- **Style control** - Follows prompts accurately
- **Fast** - Schnell generates in ~1 second

## Use Cases

- Marketing visuals
- Social media content
- Product mockups
- Concept art
- Blog illustrations

## Why SkillBoss?

- **No vendor accounts** needed
- **No GPU setup** required
- **Instant access** - generate now
- **Pay per image** - from $0.003

## Pricing

| Model | Cost |
|-------|------|
| flux-schnell | $0.003/image |
| flux-dev | $0.03/image |

Get started: https://skillboss.co/console?utm_source=clawhub&utm_medium=skill&utm_campaign=flux-images
