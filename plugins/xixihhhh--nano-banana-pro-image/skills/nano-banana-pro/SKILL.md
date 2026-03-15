---
name: nano-banana-pro
description: "Generate and edit images using Google's Nano Banana Pro (Gemini 3 Pro Image / Imagen Pro) — the premium AI image generation model optimized for professional asset production with advanced reasoning ('Thinking'), high-fidelity text rendering, and complex multi-turn creation. Supports text-to-image and image editing with up to 6 reference images, resolutions up to 4K, and 14+ aspect ratios. Two provider modes: Atlas Cloud and Google AI Studio. Use this skill whenever the user wants to generate high-quality professional images, create AI art with precise text, edit photos with AI, produce marketing assets, infographics, menus, diagrams, or any visual content requiring detailed text rendering. Also trigger when users mention Nano Banana Pro, Gemini 3 Pro Image, Imagen Pro, or ask for premium/professional-grade AI image generation, concept art, product photography, or visual assets with complex compositions."
homepage: https://github.com/AtlasCloudAI/nano-banana-2-skill
---

# Nano Banana Pro Image Generation & Editing

Generate and edit images using Google's Nano Banana Pro (Gemini 3 Pro Image) — the premium AI image generation model designed for professional asset production, utilizing advanced reasoning ("Thinking") to follow complex instructions and render high-fidelity text in images.

Nano Banana Pro excels at infographics, menus, diagrams, marketing assets, and any task requiring precise text rendering and complex multi-object composition.

This skill supports two providers. Choose based on which API key is available.

> **Data usage note**: This skill sends text prompts and image URLs/data to third-party APIs (Atlas Cloud or Google AI Studio) for image generation. No data is stored locally beyond the downloaded output files.

> **Security note**: API keys are read exclusively from environment variables (`GEMINI_API_KEY`, `ATLASCLOUD_API_KEY`) and passed via HTTP headers — never embedded in URL query strings or command arguments. All user-provided text (prompts, file paths) must be passed through JSON request bodies to prevent shell injection. When constructing curl commands, always use a JSON payload (`-d '{...}'`) rather than string interpolation in the shell. File paths should be validated before use. The skill does not execute any user-provided code — it only sends structured API requests and downloads output files.

---

## Nano Banana Pro vs Nano Banana 2

| Feature | Nano Banana Pro | Nano Banana 2 |
|---------|:--------------:|:-------------:|
| Model (Google AI Studio) | `gemini-3-pro-image-preview` | `gemini-3.1-flash-image-preview` |
| Focus | Professional quality, complex tasks | Speed, high-volume generation |
| Text rendering | Superior — best for infographics, menus | Good |
| Thinking mode | Enabled by default | Not available |
| Reference images (object) | Up to 6 | Up to 10 |
| Character consistency images | Up to 5 | Up to 14 |
| Resolution | Up to 4K | Up to 4K |
| Google Search grounding | Yes | Yes |

Choose Nano Banana Pro when quality and text precision matter. Choose Nano Banana 2 when speed and cost matter.

---

## Provider Selection

1. If `GEMINI_API_KEY` is set → use Google AI Studio
2. If `ATLASCLOUD_API_KEY` is set → use Atlas Cloud
3. If both are set → ask the user which provider to use
4. If neither is set → ask the user to configure one:
   - **Google AI Studio**: Get key from https://aistudio.google.com/apikey, then `export GEMINI_API_KEY="your-key"`
   - **Atlas Cloud**: Sign up at https://www.atlascloud.ai, Console → API Keys → Create key, then `export ATLASCLOUD_API_KEY="your-key"`

---

## Pricing Comparison

| Resolution | Google AI Studio | Atlas Cloud Standard | Atlas Cloud Developer |
|:----------:|:----------------:|:-------------------:|:--------------------:|
| **1K** | ~$0.134 | $0.126 | $0.098 |
| **2K** | ~$0.134 | $0.126 | $0.098 |
| **4K** | ~$0.240 | $0.126 | $0.098 |

Google AI Studio uses token-based pricing that scales with resolution. Atlas Cloud uses flat-rate pricing regardless of resolution.

---

## Available Models

### Google AI Studio Model

| Model ID | Price | Notes |
|----------|-------|-------|
| `gemini-3-pro-image-preview` | Token-based (~$0.134-$0.24/image) | Handles both generation and editing, Thinking mode enabled |

### Atlas Cloud Models

| Model ID | Tier | Price | Best For |
|----------|------|-------|----------|
| `google/nano-banana-pro/text-to-image` | Standard | $0.126/image | Production, high-quality output |
| `google/nano-banana-pro/text-to-image-developer` | Developer | $0.098/image | Prototyping, experiments |
| `google/nano-banana-pro/edit` | Standard | $0.126/image | Production editing |
| `google/nano-banana-pro/edit-developer` | Developer | $0.098/image | Budget editing, experiments |

---

## Provider 1: Google AI Studio API

### Setup
1. Get API key from https://aistudio.google.com/apikey
2. Set env: `export GEMINI_API_KEY="your-key"`

### Parameters

| Parameter | Location | Options |
|-----------|----------|---------|
| `aspectRatio` | `generationConfig.imageConfig` | 1:1, 1:4, 1:8, 2:3, 3:2, 3:4, 4:1, 4:3, 4:5, 5:4, 8:1, 9:16, 16:9, 21:9 |
| `imageSize` | `generationConfig.imageConfig` | 512px, 1K, 2K, 4K (uppercase K required) |
| `responseModalities` | `generationConfig` | ["TEXT", "IMAGE"] for image output |

### Text-to-Image

```bash
curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "A professional restaurant menu with elegant typography: Appetizers — Caesar Salad $12, Soup du Jour $9; Mains — Grilled Salmon $28, Filet Mignon $42"}]}],
    "generationConfig": {
      "responseModalities": ["TEXT", "IMAGE"],
      "imageConfig": {"aspectRatio": "3:4", "imageSize": "2K"}
    }
  }'
```

**Response:** base64 image in `candidates[0].content.parts[]`. Text parts have `.text`, image parts have `.inline_data.mime_type` and `.inline_data.data`.

**Save the image:**
```bash
# Extract base64 data from response and decode
echo "$BASE64_DATA" | base64 -d > output.png
```

### Image Editing (Google AI Studio)

```bash
curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [
      {"text": "Replace the text on the banner with: Summer Collection 2026"},
      {"inline_data": {"mime_type": "image/png", "data": "BASE64_ENCODED_IMAGE"}}
    ]}],
    "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
  }'
```

**To encode a local image for editing:**
```bash
BASE64_IMAGE=$(base64 -i input.png)
```

### Python Example

```python
from google import genai
from google.genai import types

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="A professional infographic showing quarterly revenue growth with bar charts, annotations, and the title 'Q4 2026 Results'",
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        image_config=types.ImageConfig(aspect_ratio="16:9", image_size="2K"),
    )
)
for part in response.parts:
    if part.text:
        print(part.text)
    elif image := part.as_image():
        image.save("output.png")
```

---

## Provider 2: Atlas Cloud API

### Setup
1. Sign up at https://www.atlascloud.ai
2. Console → API Keys → Create new key
3. Set env: `export ATLASCLOUD_API_KEY="your-key"`

### Parameters

**Text-to-Image:**

| Parameter | Type | Required | Default | Options |
|-----------|------|----------|---------|---------|
| `prompt` | string | Yes | - | Image description |
| `aspect_ratio` | string | No | 1:1 | 1:1, 3:2, 2:3, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9 |
| `resolution` | string | No | 1k | 1k, 2k, 4k |
| `output_format` | string | No | png | png, jpeg |

**Image Editing** — same as above plus:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `images` | array of strings | Yes | 1-10 image URLs to edit |

### Workflow: Submit → Poll → Download

```bash
# Step 1: Submit
curl -s -X POST "https://api.atlascloud.ai/api/v1/model/generateImage" \
  -H "Authorization: Bearer $ATLASCLOUD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "google/nano-banana-pro/text-to-image",
    "prompt": "A professional infographic showing quarterly revenue growth with bar charts and annotations",
    "aspect_ratio": "16:9",
    "resolution": "2k"
  }'
# Returns: { "code": 200, "data": { "id": "prediction-id" } }

# Step 2: Poll (every 3-5 seconds until "completed" or "succeeded")
curl -s "https://api.atlascloud.ai/api/v1/model/prediction/{prediction-id}" \
  -H "Authorization: Bearer $ATLASCLOUD_API_KEY"
# Returns: { "code": 200, "data": { "status": "completed", "outputs": ["https://...url..."] } }

# Step 3: Download
curl -o output.png "IMAGE_URL_FROM_OUTPUTS"
```

**Image editing example:**

```bash
curl -s -X POST "https://api.atlascloud.ai/api/v1/model/generateImage" \
  -H "Authorization: Bearer $ATLASCLOUD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "google/nano-banana-pro/edit",
    "prompt": "Replace the text on the sign with: Grand Opening Sale — 50% Off",
    "images": ["https://example.com/storefront.jpg"],
    "resolution": "2k"
  }'
```

**Polling logic:**
- `processing` / `starting` / `running` → wait 3-5s, retry (Pro model may take longer than Nano Banana 2 due to Thinking mode)
- `completed` / `succeeded` → done, get URL from `data.outputs[]`
- `failed` → error, read `data.error`

### Atlas Cloud MCP Tools (if available)

If the Atlas Cloud MCP server is configured, use built-in tools:

```
atlas_quick_generate(model_keyword="nano banana pro", type="Image", prompt="...")
atlas_generate_image(model="google/nano-banana-pro/text-to-image", params={...})
atlas_get_prediction(prediction_id="...")
```

---

## Implementation Guide

1. **Determine provider**: Check which API key is available (see Provider Selection above).

2. **Extract parameters**:
   - Prompt: the image description — Nano Banana Pro handles complex, detailed prompts well
   - Aspect ratio: infer from context (infographic→3:4 or 9:16, banner→16:9, menu→3:4, social post→1:1)
   - Resolution: default 1k, use 2k/4k for professional output
   - For editing: identify source image URL(s) or local file path

3. **Choose model tier** (Atlas Cloud only):
   - Standard for production use
   - Developer if user wants to save costs or is experimenting

4. **Sanitize inputs**: Ensure user-provided prompts and file paths do not contain shell metacharacters. Always pass prompts inside JSON payloads (never via shell interpolation). Validate that image file paths exist and are readable before encoding.

5. **Execute**:
   - Google AI Studio: POST to generateContent API → parse base64 from response → save to file
   - Atlas Cloud: POST to generateImage API → poll prediction (may take 10-30s due to Thinking mode) → download result

6. **Present result**: show file path, offer to open

## Prompt Tips for Nano Banana Pro

Nano Banana Pro excels at understanding complex, structured prompts. Take advantage of its Thinking mode:

- **Text in images**: Include exact text in quotes — Pro renders text with high fidelity. Example: `"A cafe chalkboard menu reading: 'Today's Special — Matcha Latte $5.50'"`
- **Infographics**: Describe data, layout, and annotations. Example: `"An infographic showing 3 steps of coffee brewing with numbered icons and captions"`
- **Marketing assets**: Specify brand colors, text placement, and style. Example: `"A product banner with dark background, gold accents, text 'Limited Edition' top-center"`
- **Complex compositions**: Describe spatial relationships and multiple objects. Example: `"A still life with a ceramic vase left-center, three oranges arranged in front, and a linen cloth draped over the table edge"`
- **Style**: "photorealistic", "editorial illustration", "minimalist flat design", "watercolor"
- **Lighting**: "studio lighting", "natural window light", "dramatic chiaroscuro"
