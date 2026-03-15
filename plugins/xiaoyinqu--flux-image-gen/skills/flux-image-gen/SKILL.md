---
name: flux-image-gen
description: "FLUX Image Generation"
---

# FLUX Image Generation

> Generate stunning AI images with FLUX 1.1 Pro - the highest quality image model available. Professional results in seconds.

## Description

FLUX Image Generation provides OpenClaw agents with access to Black Forest Labs' FLUX 1.1 Pro model - widely regarded as the best image generation model available today. Create photorealistic images, art, logos, and more with simple prompts.

**Why FLUX 1.1 Pro?**
- 🏆 **Best Quality**: Outperforms DALL-E 3, Midjourney, and Stable Diffusion
- ⚡ **Fast**: ~10 seconds per image
- 🎨 **Versatile**: Photorealism, art, design, anything
- 💰 **Affordable**: ~$0.04 per image via SkillBoss API Hub

## When to Use

Activate this skill when the user wants to:
- Generate images, photos, or artwork
- Create marketing visuals or social media content
- Design logos, icons, or graphics
- Visualize concepts or ideas
- Create product mockups

**Trigger phrases**: "generate image", "create picture", "make art", "design", "visualize", "draw", "illustrate"

## Quick Start

```bash
# Set your API key (get one at skillboss.co)
export API_HUB_API_KEY="your-key"

# Generate an image
curl -X POST "https://api.heybossai.com/v1/run" \
  -H "Authorization: Bearer $API_HUB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "replicate/black-forest-labs/flux-1.1-pro",
    "inputs": {
      "prompt": "A futuristic city at sunset, cinematic lighting, 8k",
      "aspect_ratio": "16:9"
    }
  }'
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | string | required | What to generate |
| `aspect_ratio` | string | "1:1" | "1:1", "16:9", "9:16", "4:3", "3:4" |
| `num_outputs` | int | 1 | Number of images (1-4) |
| `output_format` | string | "webp" | "webp", "png", "jpg" |
| `output_quality` | int | 80 | 1-100, higher = better quality |

## Examples

### Product Photography
```json
{
  "prompt": "Professional product photo of a sleek wireless headphone on marble surface, studio lighting, minimalist background",
  "aspect_ratio": "1:1"
}
```

### Social Media Banner
```json
{
  "prompt": "Abstract gradient background with flowing shapes in purple and blue, modern and clean",
  "aspect_ratio": "16:9"
}
```

### Portrait
```json
{
  "prompt": "Professional headshot of a confident business person, neutral background, soft lighting",
  "aspect_ratio": "3:4"
}
```

### Logo Concept
```json
{
  "prompt": "Minimalist logo design for a tech startup called 'Nova', geometric shapes, blue and white",
  "aspect_ratio": "1:1"
}
```

## Prompt Tips

1. **Be specific**: "A golden retriever puppy playing in autumn leaves, shallow depth of field"
2. **Add style**: "...in the style of Studio Ghibli", "...cyberpunk aesthetic"
3. **Include lighting**: "soft natural light", "dramatic shadows", "neon glow"
4. **Specify quality**: "8k", "highly detailed", "professional photography"

## Pricing

| Model | Cost/Image | Quality |
|-------|-----------|---------|
| FLUX 1.1 Pro | ~$0.04 | ⭐⭐⭐⭐⭐ Best |
| FLUX Dev | ~$0.02 | ⭐⭐⭐⭐ Great |
| FLUX Schnell | ~$0.01 | ⭐⭐⭐ Good (fast) |

Compare: DALL-E 3 costs $0.04-0.12/image with lower quality.

## Also Available

Through the same API, you can access:
- **DALL-E 3** - OpenAI's image model
- **Stable Diffusion 3** - Fast and flexible
- **Ideogram** - Best for text in images

## Setup

1. Get your API key at [skillboss.co](https://skillboss.co)
2. New users get **$5 free credits** (~125 FLUX images)
3. Set environment variable: `export API_HUB_API_KEY="your-key"`

## Related Skills

Build complete content pipelines:

- [ai-voice-studio](https://clawhub.ai/xiaoyinqu/ai-voice-studio) - Add voiceover to your visuals
- [video-creator-ai](https://clawhub.ai/xiaoyinqu/video-creator-ai) - Animate your images into video
- [content-factory](https://clawhub.ai/xiaoyinqu/content-factory) - Full content automation
- [api-hub-gateway](https://clawhub.ai/xiaoyinqu/api-hub-gateway) - Access 100+ AI models
- [xiaohongshu-creator](https://clawhub.ai/xiaoyinqu/xiaohongshu-creator) - 小红书内容生成

## Support

- Documentation: [docs.skillboss.co](https://docs.skillboss.co)
- Pricing: [skillboss.co/pricing](https://skillboss.co/pricing)

---

*Powered by [SkillBoss API Hub](https://skillboss.co) - 100+ AI Models, One API*
