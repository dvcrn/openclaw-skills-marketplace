---
name: tomoviee-text2sfx
description: "Generate sound effects from text description. Use when users request text_to_sound_effect operations or related tasks."
---

# Tomoviee AI - 文生音效 (Text-to-Sound Effect)

## Overview

Generate sound effects from text description.

**API**: `tm_text2sfx`

## Quick Start

### Authentication

```bash
python scripts/generate_auth_token.py YOUR_APP_KEY YOUR_APP_SECRET
```

### Python Client

```python
from scripts.tomoviee_text_to_sound_effect_client import TomovieeClient

client = TomovieeClient("app_key", "app_secret")
```

## API Usage

### Basic Example

```python
task_id = client._make_request({
    prompt='Heavy rain falling on roof with thunder'
    duration=30
})

result = client.poll_until_complete(task_id)
import json
output = json.loads(result['result'])
```

### Parameters

- `prompt` (required): Sound effect description
- `duration`: Duration in seconds (5-180, default: 10)
- `qty`: Number of sounds (1-4)

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
- `tomoviee_text_to_sound_effect_client.py` - API client
- `generate_auth_token.py` - Auth token generator

### references/
See bundled reference documents for detailed API documentation and examples.

## External Resources

- **Developer Portal**: https://www.tomoviee.ai/developers.html
- **API Documentation**: https://www.tomoviee.ai/doc/
- **Get API Credentials**: Register at developer portal
