---
name: tomoviee-img2img
description: "Generate new images based on reference image with modifications. Use when users request image_to_image operations or related tasks."
---

# Tomoviee AI - 图生图 (Image-to-Image)

## Overview

Generate new images based on reference image with modifications.

**API**: `tm_reference_img2img`

## Quick Start

### Authentication

```bash
python scripts/generate_auth_token.py YOUR_APP_KEY YOUR_APP_SECRET
```

### Python Client

```python
from scripts.tomoviee_image_to_image_client import TomovieeClient

client = TomovieeClient("app_key", "app_secret")
```

## API Usage

### Basic Example

```python
task_id = client._make_request({
    prompt='Woman in business attire, preserve face, change background to office'
    reference_image='https://example.com/portrait.jpg'
})

result = client.poll_until_complete(task_id)
import json
output = json.loads(result['result'])
```

### Parameters

- `prompt` (required): Reference + preserve + modify description
- `reference_image` (required): Reference image URL
- `control_type`: Control type (0=edge, 1=pose, 2=subject, 3=depth)
- `width/height`: Image dimensions (512-2048)
- `batch_size`: Number of images (1-4)

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
- `tomoviee_image_to_image_client.py` - API client
- `generate_auth_token.py` - Auth token generator

### references/
See bundled reference documents for detailed API documentation and examples.

## External Resources

- **Developer Portal**: https://www.tomoviee.ai/developers.html
- **API Documentation**: https://www.tomoviee.ai/doc/
- **Get API Credentials**: Register at developer portal
