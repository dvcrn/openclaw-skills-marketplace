---
name: tomoviee-text2music
description: "Generate background music from text description. Use when users request text_to_music operations or related tasks."
---

# Tomoviee AI - 文生音乐 (Text-to-Music)

## Overview

Generate background music from text description.

**API**: `tm_text2music`

## Quick Start

### Authentication

```bash
python scripts/generate_auth_token.py YOUR_APP_KEY YOUR_APP_SECRET
```

### Python Client

```python
from scripts.tomoviee_text_to_music_client import TomovieeClient

client = TomovieeClient("app_key", "app_secret")
```

## API Usage

### Basic Example

```python
task_id = client._make_request({
    prompt='Upbeat tech music, modern, energetic electronic pop'
    duration=60
})

result = client.poll_until_complete(task_id)
import json
output = json.loads(result['result'])
```

### Parameters

- `prompt` (required): Music description
- `duration`: Duration in seconds (5-900, default: 20)
- `qty`: Number of tracks (1-4)

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
- `tomoviee_text_to_music_client.py` - API client
- `generate_auth_token.py` - Auth token generator

### references/
See bundled reference documents for detailed API documentation and examples.

## External Resources

- **Developer Portal**: https://www.tomoviee.ai/developers.html
- **API Documentation**: https://www.tomoviee.ai/doc/
- **Get API Credentials**: Register at developer portal
