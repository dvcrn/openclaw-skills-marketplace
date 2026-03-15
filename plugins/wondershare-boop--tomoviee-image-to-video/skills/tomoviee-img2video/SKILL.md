---
name: tomoviee-img2video
description: "Generate videos from image + text prompt. Animates static images with motion and camera movements. Use when users request image_to_video operations or related tasks."
---

# Tomoviee AI - 图生视频 (Image-to-Video)

## Overview

Generate videos from image + text prompt. Animates static images with motion and camera movements.

**API**: `tm_img2video_b`

## Quick Start

### Authentication

```bash
python scripts/generate_auth_token.py YOUR_APP_KEY YOUR_APP_SECRET
```

### Python Client

```python
from scripts.tomoviee_image_to_video_client import TomovieeClient

client = TomovieeClient("app_key", "app_secret")
```

## API Usage

### Basic Example

```python
task_id = client._make_request({
    prompt='Camera slowly panning right, leaves rustling'
    image='https://example.com/landscape.jpg'
})

result = client.poll_until_complete(task_id)
import json
output = json.loads(result['result'])
```

### Parameters

- `prompt` (required): Motion and camera description
- `image` (required): Image URL (JPG/JPEG/PNG/WEBP, <200M)
- `resolution`: `720p` or `1080p`
- `aspect_ratio`: `16:9`, `9:16`, `4:3`, `3:4`, `1:1`, `original`
- `camera_move_index`: Optional camera movement (1-46)

## Async Workflow

1. **Create task**: Get `task_id` from API call
2. **Poll for completion**: Use `poll_until_complete(task_id)`
3. **Extract result**: Parse returned JSON for output URLs

**Status codes**:
- 1 = Queued
- 2 = Processing
- 3 = Success (ready)
- 4 = Failed
- 5 = Cancelled
- 6 = Timeout

## Resources

### scripts/
- `tomoviee_image_to_video_client.py` - API client
- `generate_auth_token.py` - Auth token generator

### references/
See bundled reference documents for detailed API documentation and examples.

## External Resources

- **Developer Portal**: https://www.tomoviee.ai/developers.html
- **API Documentation**: https://www.tomoviee.ai/doc/
- **Get API Credentials**: Register at developer portal
