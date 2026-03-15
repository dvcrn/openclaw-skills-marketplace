---
name: skillboss-bg-remover
description: "Remove backgrounds from images instantly. Perfect for product photos, portraits, e-commerce. Powered by Replicate."
homepage: https://skillboss.co
---

# AI Background Removal

**Instant transparent PNGs from any image.**

## Usage Example

```bash
curl https://api.heybossai.com/v1/run \
  -H "Authorization: Bearer $SKILLBOSS_API_KEY" \
  -d '{
    "model": "replicate/remove-bg",
    "input": {
      "image_url": "https://example.com/product.jpg"
    }
  }'
```

## Use Cases

| Use Case | Example |
|----------|---------|
| **E-commerce** | Product photos on white |
| **Portraits** | Profile pictures |
| **Marketing** | Composite images |
| **Design** | Assets for Figma/Canva |

## Features

- **Instant** - Results in ~2 seconds
- **High quality** - Clean edges, hair detail
- **Any subject** - People, products, animals
- **Batch support** - Process multiple images

## Output

- Format: PNG with transparency
- Resolution: Same as input
- Alpha channel: Clean edges

## Why SkillBoss?

- **No Replicate account** needed
- **No credits to buy** - pay per image
- **API access** - automate workflows
- **Batch processing** - scale easily

## Pricing

$0.02 per image

Get started: https://skillboss.co/console
