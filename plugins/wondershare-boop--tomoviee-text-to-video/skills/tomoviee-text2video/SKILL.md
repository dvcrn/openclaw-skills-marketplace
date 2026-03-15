---
name: tomoviee-text2video
description: "Generate videos from text descriptions. Supports 720p/1080p, multiple aspect ratios (16:9, 9:16, 4:3, 3:4, 1:1), and 46 camera movement types. Returns 5-second video clips. Use when users request text-to-video generation, video creation from prompts, or generating video content with specific camera movements."
---

# Tomoviee AI - 文生视频 (Text-to-Video)

## Overview

Generate 5-second videos from text descriptions. Supports 720p/1080p resolution, flexible aspect ratios, and 46 camera movement effects.

**API**: `tm_text2video_b`

## Quick Start

### Authentication

```bash
python scripts/generate_auth_token.py YOUR_APP_KEY YOUR_APP_SECRET
```

### Python Client

```python
from scripts.tomoviee_text2video_client import TomovieeText2VideoClient

client = TomovieeText2VideoClient("app_key", "app_secret")
```

## API Usage

### Basic Example

```python
task_id = client.text_to_video(
    prompt="Golden retriever running through sunlit meadow, slow motion, cinematic",
    resolution="720p",
    aspect_ratio="16:9",
    camera_move_index=5
)

result = client.poll_until_complete(task_id)
import json
video_url = json.loads(result['result'])['video_path'][0]
```

### Parameters

- `prompt` (required): Text description (subject + action + scene + camera + lighting)
- `resolution`: `720p` or `1080p` (default: `720p`)
- `duration`: Duration in seconds (only `5` supported)
- `aspect_ratio`: `16:9`, `9:16`, `4:3`, `3:4`, `1:1`
- `camera_move_index`: Camera movement type (1-46, optional)

## Async Workflow

1. **Create task**: Get `task_id` from API call
2. **Poll for completion**: Use `poll_until_complete(task_id)`
3. **Extract result**: Parse returned JSON for video URL

**Status codes**:
- 1 = Queued
- 2 = Processing
- 3 = Success (ready)
- 4 = Failed
- 5 = Cancelled
- 6 = Timeout

**Generation time**: 1-5 minutes per 5-second video

## Camera Movements

All video APIs support 46 camera movement types via `camera_move_index`:
- 5 = Slow zoom in
- 12 = Pan right
- 23 = Orbit/circular
- None = Auto-select

See `references/camera_movements.md` for all 46 types.

## Prompt Engineering

Effective prompts improve output quality dramatically.

**Formula**: `Subject + Motion + Scene + Camera + Lighting + Atmosphere`

**Example**:
> "Red Ferrari speeding along coastal highway, camera tracking from side, golden hour sunset, cinematic and epic"

See `references/prompt_guide.md` for detailed guidance.

## Resources

### scripts/
- `tomoviee_text2video_client.py` - Text-to-Video API client
- `generate_auth_token.py` - Auth token generator

### references/
- `video_apis.md` - Detailed video API documentation
- `camera_movements.md` - All 46 camera movement types
- `prompt_guide.md` - Prompt engineering guide and best practices

## External Resources

**🌐 Network Routing Notice:**
- **Global / Overseas Network:** Access the international site (`.ai`).
- **Mainland China Network:** Access the domestic site (`.cn`), which offers localized latency and compliance.

### Global / Overseas (.AI)
- **Developer Portal**: https://www.tomoviee.ai/developers.html
- **API Documentation**: https://www.tomoviee.ai/doc/
- **Get API Credentials**: Register at developer portal

### Mainland China (.CN)
- **Developer Portal**: https://www.tomoviee.cn/developers.html
- **API Documentation**: https://www.tomoviee.cn/doc/
- **Get API Credentials**: Register at developer portal
