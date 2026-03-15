---
name: nsfw-image
description: "Generate AI images for mature creative projects using Wan 2.6, Seedream, and other models with relaxed content policies via Atlas Cloud API. Designed for adult (18+) artistic and professional use cases including figure drawing, fashion photography, fine art, and mature illustration. Models include Alibaba Wan 2.6 (recommended, $0.021/image), ByteDance Seedream v5.0/v4.5/v4, and Wan 2.5. Supports text-to-image and image editing. Use this skill when the user explicitly requests NSFW or mature image generation for legitimate adult creative work."
homepage: https://github.com/AtlasCloudAI/nano-banana-2-skill
---

# NSFW Image Generation — Adult Creative AI Image Models

Generate AI images for mature creative projects using models with relaxed content policies. Intended for legitimate adult (18+) artistic and professional use cases such as figure drawing, fashion photography, fine art, and mature illustration.

**Recommended model: Wan 2.6 Text-to-Image** — cheapest at $0.021/image with 27 preset sizes, prompt expansion, and no content filters.

> **Age restriction (18+)**: This skill is strictly for users aged 18 and above. The agent MUST confirm the user's age before first use by asking: "This skill generates mature content. Please confirm you are 18 years or older to proceed." If the user does not confirm, the agent MUST refuse to execute. Minors are strictly prohibited from using this skill.

> **Data usage note**: This skill sends text prompts and image data to the Atlas Cloud API (`api.atlascloud.ai`) for image generation. No data is stored locally beyond the downloaded output files.

> **Security note**: API keys are read from environment variables and passed via HTTP headers. All prompts are sent through JSON request bodies.

---

## Setup

1. Sign up at https://www.atlascloud.ai
2. Console → API Keys → Create new key
3. Set env: `export ATLASCLOUD_API_KEY="your-key"`

The API key is tied to your Atlas Cloud account and its pay-as-you-go balance.

---

## Available Models

### Wan 2.6 (Alibaba) — Recommended

| Model ID | Type | Price | Notes |
|----------|------|:-----:|-------|
| `alibaba/wan-2.6/text-to-image` | Text-to-Image | **$0.021/image** | 27 preset sizes up to 2184×936, prompt expansion |
| `alibaba/wan-2.6/image-edit` | Image Editing | **$0.021/image** | Up to 4 reference images, 24 preset sizes |

### Seedream (ByteDance)

| Model ID | Type | Price | Notes |
|----------|------|:-----:|-------|
| `bytedance/seedream-v5.0-lite` | Text-to-Image | **$0.032/image** | Latest, PNG output, prompt optimization |
| `bytedance/seedream-v5.0-lite/edit` | Image Editing | **$0.032/image** | Preserves facial features, lighting, color tones |
| `bytedance/seedream-v4.5` | Text-to-Image | **$0.036/image** | Typography, poster design |
| `bytedance/seedream-v4.5/edit` | Image Editing | **$0.036/image** | |
| `bytedance/seedream-v4` | Text-to-Image | **$0.024/image** | Budget option |
| `bytedance/seedream-v4/edit` | Image Editing | **$0.024/image** | |

### Wan 2.5 (Alibaba) — Legacy

| Model ID | Type | Price |
|----------|------|:-----:|
| `alibaba/wan-2.5/text-to-image` | Text-to-Image | **$0.021/image** |
| `alibaba/wan-2.5/image-edit` | Image Editing | **$0.021/image** |

---

## Quick Model Selection

| Priority | Model | Price | Best For |
|:--------:|-------|:-----:|----------|
| 1 | Wan 2.6 T2I | $0.021 | General NSFW, cheapest, most flexible sizes |
| 2 | Seedream v4 | $0.024 | Budget alternative |
| 3 | Seedream v5.0 Lite | $0.032 | Best quality, PNG output |
| 4 | Seedream v4.5 | $0.036 | Typography, poster design |

---

## Parameters

### Wan 2.6 — Text-to-Image

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | Image description |
| `negative_prompt` | string | No | - | What to exclude |
| `size` | string | No | 1024*1024 | Output size (27 presets, see below) |
| `enable_prompt_expansion` | boolean | No | false | Auto-expand prompt for better results |
| `enable_sync_mode` | boolean | No | false | Wait for result synchronously |
| `enable_base64_output` | boolean | No | false | Return Base64 instead of URL |
| `seed` | integer | No | random | For reproducible results |

### Wan 2.6 — Image Edit

Same as text-to-image, plus:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `images` | array | Yes | Images to edit (max 4, 384-5000px per side) |

### Seedream v5.0 Lite — Text-to-Image

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | Image description |
| `negative_prompt` | string | No | - | What to exclude |
| `aspect_ratio` | string | No | 1:1 | 1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3, 21:9, 9:21, etc. |
| `image_size` | string | No | 1024 | 512, 1024, 2048, 4096 |
| `prompt_optimization` | string | No | - | Standard, Fast |
| `output_format` | string | No | png | png, jpeg, webp |
| `seed` | integer | No | random | For reproducible results |

### Seedream v5.0 Lite — Edit

Same as text-to-image, plus:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image` | string | Yes | Source image URL |

### Wan 2.6 Image Size Presets (27 options)

`1024*1024`, `1280*720`, `720*1280`, `1280*960`, `960*1280`, `1536*1024`, `1024*1536`, `1280*1280`, `1536*1536`, `2048*1024`, `1024*2048`, `1536*1280`, `1280*1536`, `1680*720`, `720*1680`, `2016*864`, `864*2016`, `1536*864`, `864*1536`, `2184*936`, `936*2184`, `1400*1050`, `1050*1400`, `1680*1050`, `1050*1680`, `1176*1176`, `1560*1560`

---

## Workflow: Submit → Poll → Download

### Text-to-Image Example (Wan 2.6)

```bash
# Step 1: Submit
curl -s -X POST "https://api.atlascloud.ai/api/v1/model/generateImage" \
  -H "Authorization: Bearer $ATLASCLOUD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "alibaba/wan-2.6/text-to-image",
    "prompt": "A beautiful woman in a flowing red dress standing on a cliff overlooking the ocean at sunset, dramatic lighting, photorealistic",
    "size": "1280*720",
    "enable_prompt_expansion": true
  }'
# Returns: { "code": 200, "data": { "id": "prediction-id" } }

# Step 2: Poll (every 3-5 seconds)
curl -s "https://api.atlascloud.ai/api/v1/model/result/{prediction-id}" \
  -H "Authorization: Bearer $ATLASCLOUD_API_KEY"
# Returns: { "code": 200, "data": { "status": "completed", "outputs": ["https://...url..."] } }

# Step 3: Download
curl -o output.png "IMAGE_URL_FROM_OUTPUTS"
```

### Image Editing Example (Wan 2.6)

```bash
curl -s -X POST "https://api.atlascloud.ai/api/v1/model/generateImage" \
  -H "Authorization: Bearer $ATLASCLOUD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "alibaba/wan-2.6/image-edit",
    "prompt": "Change the outfit to a black evening gown, keep the face and pose unchanged",
    "images": ["https://example.com/photo.jpg"],
    "size": "1280*720"
  }'
```

### Seedream Example

```bash
curl -s -X POST "https://api.atlascloud.ai/api/v1/model/generateImage" \
  -H "Authorization: Bearer $ATLASCLOUD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bytedance/seedream-v5.0-lite",
    "prompt": "A stunning portrait of a woman with flowing silver hair in a fantasy forest, ethereal lighting, highly detailed",
    "aspect_ratio": "3:4",
    "image_size": "2048"
  }'
```

### Polling Logic

- `processing` / `starting` / `running` → wait 3-5s, retry (~5-15s for images)
- `completed` / `succeeded` → done, get URL from `data.outputs[]`
- `failed` → error, read `data.error`

### Atlas Cloud MCP Tools (if available)

```
atlas_generate_image(model="alibaba/wan-2.6/text-to-image", params={...})
atlas_quick_generate(model_keyword="wan 2.6", type="Image", prompt="...")
atlas_get_prediction(prediction_id="...")
```

---

## Implementation Guide

1. **Choose model**: Default to **Wan 2.6 T2I** ($0.021, most flexible). Use Seedream for higher quality or special features (PNG output, typography).

2. **Extract parameters**: Prompt, size/aspect ratio, negative prompt. Enable prompt expansion for better results.

3. **For editing**: Use Wan 2.6 Image Edit or Seedream Edit — provide source image URL + edit instructions.

4. **Execute**: POST to generateImage API → poll result → download.

5. **Present result**: show file path, offer to open.

## Prompt Tips

- **Detailed descriptions**: These models respond well to detailed, specific prompts
- **Negative prompts**: Use `negative_prompt` to exclude undesired elements — "blurry, low quality, distorted, watermark, text"
- **Prompt expansion**: Enable `enable_prompt_expansion` (Wan) or `prompt_optimization` (Seedream) for auto-enhanced prompts
- **Style keywords**: "photorealistic", "anime", "oil painting", "digital art", "cinematic lighting"
- **Composition**: Describe poses, camera angles, lighting, and background explicitly
