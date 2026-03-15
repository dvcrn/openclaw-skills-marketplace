---
name: tomoviee-firstlast2video
description: "Generate videos from first and last frame images. Input two images (first frame and last frame) to create 5-second dynamic videos. Supports 720p/1080p, multiple aspect ratios (16:9, 9:16, 4:3, 3:4, 1:1, original), and 46 camera movement types. Use when users request first-last frame video generation, keyframe-to-video animation, or creating videos from two images showing start and end states."
---

# Tomoviee AI - 首尾帧生视频 (First-Last Frame to Video)

## Overview

Generate 5-second dynamic videos from two keyframe images (first frame and last frame). The AI model intelligently interpolates motion between the two frames, creating smooth transitions with optional camera movements and text-guided motion control.

**API**: `tm_tail2video_b`

**Key Features**:
- Input: Two images (first frame + last frame)
- Output: 5-second video (720p/1080p)
- Motion control via text prompts (subject + motion + background)
- 46 camera movement types
- Physics-based motion simulation (gravity/fluid/collision)
- Cinematic camera movements (push/pull/pan/tilt/orbit)

## Quick Start

### Authentication

```bash
python scripts/generate_auth_token.py YOUR_APP_KEY YOUR_APP_SECRET
```

### Python Client

```python
from scripts.tomoviee_firstlast2video_client import TomovieeFirstLast2VideoClient

client = TomovieeFirstLast2VideoClient("app_key", "app_secret")
```

## API Usage

### Basic Example

```python
task_id = client.firstlast_to_video(
    prompt="角色从头部开始变形，伴随大量白色和灰色烟雾，旋转的沙子，逐渐巧妙变形为老虎",
    image="https://example.com/first-frame.jpg",
    image_tail="https://example.com/last-frame.jpg",
    resolution="1080p",
    aspect_ratio="16:9"
)

result = client.poll_until_complete(task_id)
import json
video_url = json.loads(result['result'])['video_path'][0]
```

### Parameters

- `prompt` (required): Text description (subject + motion + background motion)
- `image` (required): First frame image URL (<200M, 720P+ recommended, JPG/JPEG/PNG/WEBP)
- `image_tail` (required): Last frame image URL (<200M, 720P+ recommended, JPG/JPEG/PNG/WEBP)
- `resolution`: `720p` or `1080p` (default: `720p`)
- `duration`: Duration in seconds (only `5` supported)
- `aspect_ratio`: `16:9`, `9:16`, `4:3`, `3:4`, `1:1`, `original` (default: `16:9`)
- `camera_move_index`: Camera movement type (1-46, optional)

### Image Requirements

- **Size**: <200M per image
- **Resolution**: 720P+ recommended (short edge >720px)
- **Format**: JPG, JPEG, PNG, WEBP
- **Recommendation**: Input and output aspect ratios should match to avoid cropping

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
- 5 = Tilt up
- 7 = Push in (dolly in)
- 8 = Pull out (dolly out)
- 23 = Timelapse landscape
- None = Auto-select

See `references/camera_movements.md` for all 46 types.

## Prompt Engineering

### Formula

**提示词 = 主体+运动，背景+运动**

- **主体**: 画面中的人物、动物、物体等主体
- **运动**: 目标主体希望实现的运动轨迹
- **背景**: 画面中的背景及其动态变化

### Tips

- Use simple words and sentence structures
- Describe motion that follows physics laws
- Avoid descriptions too different from input images (may cause scene cuts)
- Complex physics motions (ball bouncing, projectile motion) are challenging
- Don't upload images with picture frames (may cause unwanted camera movements)

### Examples

**Example 1**:
- **First frame**: Character portrait
- **Last frame**: Tiger portrait
- **Prompt**: "角色从头部变形，伴随着大量白色和灰色烟雾和旋转的沙子，逐渐巧妙地变形为老虎"
- **Translation**: "Character transforms from head, accompanied by lots of white and gray smoke and swirling sand, gradually transforming into a tiger"

**Example 2**:
- **First frame**: Milk splash starting
- **Last frame**: Milk splash ending
- **Prompt**: "这是一种美味的牛奶，在Wirbel制作和搅拌之后，3D效果"
- **Translation**: "This is delicious milk, after Wirbel making and stirring, 3D effect"

See `references/prompt_guide.md` for detailed guidance.

## Use Cases

- **Short video creation**: Transform static images into dynamic clips
- **Film pre-visualization**: Storyboard animation and scene previsualization
- **Advertising effects**: Product animation with keyframe control
- **Motion design**: Precise control over start and end states
- **Animation prototyping**: Quick motion tests with keyframe anchoring

## Resources

### scripts/
- `tomoviee_firstlast2video_client.py` - First-Last Frame to Video API client
- `generate_auth_token.py` - Auth token generator

### references/
- `video_apis.md` - Detailed video API documentation
- `camera_movements.md` - All 46 camera movement types
- `prompt_guide.md` - Prompt engineering guide and best practices

## External Resources

- **Developer Portal**: https://www.tomoviee.ai/developers.html
- **API Documentation**: https://www.tomoviee.ai/doc/ai-video/first-and-last-frame-to-video.html
- **Get API Credentials**: Register at developer portal
