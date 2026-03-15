---
name: tomoviee-text2speech
description: "Convert text to natural-sounding speech audio. Use when users request text_to_speech operations or related tasks."
---

# Tomoviee AI - 文字转语音 (Text-to-Speech)

## Overview

Convert text to natural-sounding speech audio.

**API**: `tm_text2speech_b`

## Quick Start

### Authentication

```bash
python scripts/generate_auth_token.py YOUR_APP_KEY YOUR_APP_SECRET
```

### Python Client

```python
from scripts.tomoviee_text_to_speech_client import TomovieeClient

client = TomovieeClient("app_key", "app_secret")
```

## API Usage

### Basic Example

```python
task_id = client._make_request({
    text='Welcome to Tomoviee AI platform'
    speaker_choice='GEN_ZH_F_001'
})

result = client.poll_until_complete(task_id)
import json
output = json.loads(result['result'])
```

### Parameters

- `text` (required): Text to convert (max 5000 chars)
- `speaker_choice`: Voice ID (default: GEN_ZH_F_001)
- `emotion_choice`: Emotion type
- `speed_adjustment`: Speed multiplier (0.5-2.0)

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
- `tomoviee_text_to_speech_client.py` - API client
- `generate_auth_token.py` - Auth token generator

### references/
See bundled reference documents for detailed API documentation and examples.

## External Resources

- **Developer Portal**: https://www.tomoviee.ai/developers.html
- **API Documentation**: https://www.tomoviee.ai/doc/
- **Get API Credentials**: Register at developer portal
