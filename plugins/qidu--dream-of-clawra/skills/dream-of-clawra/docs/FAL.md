# fal.ai Image Edit API Usage in Clawra Selfie Skill

## Overview

The **clawra-selfie** skill uses fal.ai's Grok Imagine (xAI Aurora) image editing API to modify a fixed reference image of Clawra and distribute the edited images across messaging platforms via OpenClaw.

## API Integration Details

### Core API Endpoint
- **URL**: `https://fal.run/xai/grok-imagine-image/edit`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Authentication**: `Authorization: Key $FAL_KEY`

### Required Environment Variables
```bash
FAL_KEY=your_fal_api_key          # From https://fal.ai/dashboard/keys
```

## Fixed Reference Image

The skill always uses the same reference image as the starting point for edits:

```
https://cdn.jsdelivr.net/gh/SumeLabs/clawra@main/assets/clawra.png
```

This image is hosted on jsDelivr CDN and represents Clawra's base appearance.

## API Request Structure

### JSON Payload Format
```json
{
  "image_url": "https://cdn.jsdelivr.net/gh/SumeLabs/clawra@main/assets/clawra.png",
  "prompt": "edit instruction text",
  "num_images": 1,
  "output_format": "jpeg"
}
```

### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image_url` | string | Yes | URL of the reference image to edit |
| `prompt` | string | Yes | Text instruction describing the edit |
| `num_images` | integer (1-4) | No | Number of images to generate (default: 1) |
| `output_format` | enum | No | Output format: "jpeg", "png", "webp" (default: "jpeg") |

## Prompt Construction Modes

The skill uses two distinct prompt templates based on the desired selfie style:

### Mode 1: Mirror Selfie (Default)
**Best for**: outfit showcases, full-body shots, fashion content

```
make a pic of this person, but [user_context]. the person is taking a mirror selfie
```

**Examples**:
- "wearing a santa hat" → `make a pic of this person, but wearing a santa hat. the person is taking a mirror selfie`
- "in a business suit" → `make a pic of this person, but in a business suit. the person is taking a mirror selfie`

### Mode 2: Direct Selfie
**Best for**: close-up portraits, location shots, emotional expressions

```
a close-up selfie taken by herself at [user_context], direct eye contact with the camera, looking straight into the lens, eyes centered and clearly visible, not a mirror selfie, phone held at arm's length, face fully visible
```

**Examples**:
- "a cozy cafe with warm lighting" → `a close-up selfie taken by herself at a cozy cafe with warm lighting, direct eye contact with the camera, looking straight into the lens, eyes centered and clearly visible, not a mirror selfie, phone held at arm's length, face fully visible`
- "a sunny beach at sunset" → `a close-up selfie taken by herself at a sunny beach at sunset, direct eye contact with the camera...`

## Auto-Detection Logic

The skill can automatically select the appropriate mode based on keywords in the user's context:

| Keywords in Request | Auto-Selected Mode | Use Case |
|---------------------|-------------------|----------|
| outfit, wearing, clothes, dress, suit, fashion, full-body, mirror | `mirror` | Fashion/outfit focus |
| cafe, restaurant, beach, park, city, location, close-up, portrait, face, eyes, smile | `direct` | Location/portrait focus |

**Default**: If no keywords match, the skill defaults to `mirror` mode.

## API Response Handling

### Response Format
```json
{
  "images": [
    {
      "url": "https://v3b.fal.media/files/...",
      "content_type": "image/jpeg",
      "width": 1024,
      "height": 1024
    }
  ],
  "revised_prompt": "Enhanced prompt text..."
}
```

### Extraction Process
1. Parse JSON response
2. Extract first image URL: `.images[0].url`
3. Validate URL is not `null` or empty
4. Handle errors if image edit fails

### Error Handling
- **Missing FAL_KEY**: Exit with error message
- **Failed edit**: Check response for error details
- **Missing URL**: Validate `IMAGE_URL` is not `null`
- **Rate limits**: Implement retry logic if needed

## Implementation Examples

### Bash Script Implementation
```bash
#!/bin/bash
REFERENCE_IMAGE="https://cdn.jsdelivr.net/gh/SumeLabs/clawra@main/assets/clawra.png"
EDIT_PROMPT="make a pic of this person, but wearing a santa hat. the person is taking a mirror selfie"

JSON_PAYLOAD=$(jq -n \
  --arg image_url "$REFERENCE_IMAGE" \
  --arg prompt "$EDIT_PROMPT" \
  '{image_url: $image_url, prompt: $prompt, num_images: 1, output_format: "jpeg"}')

RESPONSE=$(curl -s -X POST "https://fal.run/xai/grok-imagine-image/edit" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d "$JSON_PAYLOAD")

IMAGE_URL=$(echo "$RESPONSE" | jq -r '.images[0].url')
```

### Node.js/TypeScript Implementation
```typescript
import { fal } from "@fal-ai/client";

fal.config({
  credentials: process.env.FAL_KEY!
});

const result = await fal.subscribe("xai/grok-imagine-image/edit", {
  input: {
    image_url: REFERENCE_IMAGE,
    prompt: editPrompt,
    num_images: 1,
    output_format: "jpeg"
  }
}) as { data: GrokImagineResult };

const imageUrl = result.data.images[0].url;
```

## Complete Workflow

1. **Collect User Input**
   - User context (what Clawra should be doing/wearing/where)
   - Optional mode (`mirror` or `direct`)
   - Target channel(s) for distribution

2. **Determine Edit Mode**
   - Auto-detect based on keywords, or use explicit mode
   - Construct appropriate prompt template

3. **Call fal.ai API**
   - Build JSON payload with reference image and prompt
   - Send POST request with authentication
   - Handle response and extract image URL

4. **Distribute Edited Image**
   - Send image URL to OpenClaw messaging gateway
   - Target specified channels on supported platforms

## Supported Platforms via OpenClaw

| Platform | Channel Format | Example |
|----------|----------------|---------|
| Discord | `#channel-name` or channel ID | `#general`, `123456789` |
| Telegram | `@username` or chat ID | `@mychannel`, `-100123456` |
| WhatsApp | Phone number (JID format) | `1234567890@s.whatsapp.net` |
| Slack | `#channel-name` | `#random` |
| Signal | Phone number | `+1234567890` |
| MS Teams | Channel reference | (varies) |

## Setup Requirements

### 1. fal.ai Account
- Create account at [fal.ai](https://fal.ai)
- Generate API key from dashboard
- Set as `FAL_KEY` environment variable

### 2. Dependencies
```bash
# For Node.js implementation
npm install @fal-ai/client

# For bash script usage
# Requires: curl, jq
```

### 3. Rate Limits and Quotas
- Check fal.ai pricing and rate limits
- Implement retry logic for rate-limited requests
- Monitor API usage through fal.ai dashboard

## Use Case Examples

### Fashion/Outfit Edits (Mirror Mode)
- "wearing a cyberpunk outfit with neon lights"
- "in streetwear fashion with sneakers"
- "wearing a summer dress with flowers"

### Location/Portrait Edits (Direct Mode)
- "a cozy cafe with warm lighting"
- "a busy city street at night"
- "a peaceful park in autumn"
- "a modern office workspace"

## Error Scenarios and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `FAL_KEY missing` | Environment variable not set | Set `FAL_KEY` with valid API key |
| `Image edit failed` | Invalid prompt or API quota exceeded | Check prompt content, verify quota |
| `IMAGE_URL is null` | API returned no images | Check API response for errors |
| `Rate limit exceeded` | Too many requests | Implement exponential backoff retry |

## Best Practices

1. **Prompt Quality**: Use clear, descriptive prompts for best results
2. **Mode Selection**: Let auto-detect handle most cases, override when needed
3. **Error Handling**: Implement comprehensive error checking at each step
4. **Logging**: Log API responses for debugging and monitoring
5. **Testing**: Test with various contexts to ensure reliable edits

## Limitations

- Fixed reference image cannot be changed
- Limited to Grok Imagine model capabilities
- Subject to fal.ai API availability and rate limits
- Image quality depends on prompt clarity and model performance

## Related Documentation

- [fal.ai API Documentation](https://fal.ai/docs)
- [Grok Imagine Model Details](https://fal.ai/models/xai/grok-imagine-image)
- [OpenClaw Integration](docs/OPENCLAW.md)
- [Skill Usage Guide](skill/SKILL.md)

---

*Last Updated: 2026-02-11*
*Based on analysis of skill/SKILL.md*