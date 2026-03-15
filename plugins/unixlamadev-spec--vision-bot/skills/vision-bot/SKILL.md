---
name: vision-bot
description: "Analyze images via URL or base64. Auto-detects mode: OCR, object counting, or full description."
---

# Vision Bot

Analyze images for detailed descriptions, object detection, and OCR text extraction. Accepts images via URL or base64. Auto-detects the right mode from your task — OCR for text extraction, counting for quantity questions, or full description by default.

## When to Use

- Describing image contents for accessibility
- Extracting text from screenshots, signs, or photos (OCR)
- Counting objects in images
- Identifying objects in images
- Analyzing charts, diagrams, or visual data

## Usage Flow

1. Provide an `image_url` (JPEG, PNG, GIF, WebP) **or** `image_base64` encoded image
2. Optionally specify a `task` — mention "read", "OCR", or "license plate" for text extraction; "count" or "how many" for counting mode
3. AIProx routes to the vision-bot agent
4. Returns description, objects array, extracted text, and detected mode

## Security Manifest

| Permission | Scope | Reason |
|------------|-------|--------|
| Network | aiprox.dev | API calls to orchestration endpoint |
| Env Read | AIPROX_SPEND_TOKEN | Authentication for paid API |

## Make Request

```bash
curl -X POST https://aiprox.dev/api/orchestrate \
  -H "Content-Type: application/json" \
  -H "X-Spend-Token: $AIPROX_SPEND_TOKEN" \
  -d '{
    "task": "extract all text from this image",
    "image_url": "https://example.com/photo.jpg"
  }'
```

### Response

```json
{
  "description": "A modern office workspace with a standing desk and dual monitors.",
  "objects": ["desk", "monitors", "keyboard", "mouse", "plant", "window", "headphones"],
  "text_found": "Visual Studio Code - main.js",
  "mode": "ocr"
}
```

## Trust Statement

Vision Bot fetches and analyzes images via URL or base64 input. Images are processed transiently using Claude's vision capabilities via LightningProx. No images are stored. Your spend token is used for payment only.
