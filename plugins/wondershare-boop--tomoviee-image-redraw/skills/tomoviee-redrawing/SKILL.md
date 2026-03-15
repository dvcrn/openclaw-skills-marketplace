---
name: tomoviee-redrawing
description: "Redraw specific regions of image using mask (white=redraw, black=keep). Use when users request image_redrawing operations or related tasks."
---

# Tomoviee AI - 图像重绘 (Image Redrawing)

## Overview

Redraw specific regions of image using mask (white=redraw, black=keep).

**API**: `tm_redrawing`

## Quick Start

### Authentication

```bash
python scripts/generate_auth_token.py YOUR_APP_KEY YOUR_APP_SECRET
```

### Python Client

```python
from scripts.tomoviee_image_redrawing_client import TomovieeClient

client = TomovieeClient("app_key", "app_secret")
```

## API Usage

### Basic Example

```python
task_id = client._make_request({
    prompt='Clear blue sky with fluffy clouds'
    image='https://example.com/photo.jpg'
})

result = client.poll_until_complete(task_id)
import json
output = json.loads(result['result'])
```

### Parameters

- `prompt` (required): Description of what to redraw
- `image` (required): Original image URL
- `mask` (required): Mask image URL
- `resolution`: `512*512`, `768*768`, `1024*1024`
- `image_num`: Number of variations (1-4)

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
- `tomoviee_image_redrawing_client.py` - API client
- `generate_auth_token.py` - Auth token generator

### references/
See bundled reference documents for detailed API documentation and examples.

## External Resources

- **Developer Portal**: https://www.tomoviee.ai/developers.html
- **API Documentation**: https://www.tomoviee.ai/doc/
- **Get API Credentials**: Register at developer portal
