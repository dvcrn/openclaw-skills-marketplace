# AI Service Category Reference

## Available Categories

### Banana2 — Gemini Image Generation (Default Recommended)

**Text-to-Image (text_to_image)**
```json
{
  "processing_mode": "text_to_image",
  "prompt": "a beautiful sunset over the ocean, photorealistic, 4k",
  "generationConfig": {
    "responseModalities": ["IMAGE"],
    "imageConfig": {
      "aspectRatio": "16:9",
      "image_size": "1K"
    }
  }
}
```

**Image-to-Image (image_to_image)**
```json
{
  "processing_mode": "image_to_image",
  "prompt": "transform into oil painting style",
  "imageUrls": ["https://r2.example.com/uploaded-image.jpg"],
  "generationConfig": {
    "responseModalities": ["IMAGE"],
    "imageConfig": {
      "image_size": "1K"
    }
  }
}
```

**Multi-Image Blend (multi_image_blend)**
```json
{
  "processing_mode": "multi_image_blend",
  "prompt": "blend these images into a cohesive scene",
  "imageUrls": ["https://r2.../img1.jpg", "https://r2.../img2.jpg"],
  "generationConfig": {
    "responseModalities": ["IMAGE"],
    "imageConfig": {
      "image_size": "1K"
    }
  }
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| processing_mode | string | Yes | `text_to_image` / `image_to_image` / `multi_image_blend` |
| prompt | string | Yes | English description prompt |
| imageUrls | string[] | Required for image-to-image/multi-image blend | Reference image URLs (must be R2 addresses) |
| generationConfig.responseModalities | string[] | Yes | Fixed `["IMAGE"]` |
| generationConfig.imageConfig.image_size | string | No | `1K`(default) / `2K` / `4K`, affects credit multiplier |
| generationConfig.imageConfig.aspectRatio | string | No | Ratio such as `1:1` / `16:9` / `9:16` / `4:3` / `3:4` |

Credits: text_to_image=10, image_to_image=15, multi_image_blend=20 (1K base)
Estimated time: 10-30 seconds

---

### remove-bg — Background Removal

```json
{
  "imageUrls": ["https://r2.example.com/photo.jpg"]
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| imageUrls | string[] | Yes | Image URLs for background removal |

No processing_mode or prompt needed. Credits: 5
Estimated time: 5-10 seconds

---

### remove-watermark — Watermark Removal

```json
{
  "imageUrls": ["https://r2.example.com/photo.jpg"]
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| imageUrls | string[] | Yes | Image URLs for watermark removal |

No processing_mode or prompt needed. Credits: 5
Estimated time: 5-10 seconds

---

### seedream — Doubao Seedream Image Generation

**Text-to-Image**
```json
{
  "processing_mode": "text_to_image",
  "prompt": "a cute orange cat sitting on a windowsill",
  "generationConfig": {
    "imageConfig": {
      "image_size": "2K"
    }
  }
}
```

**Image-to-Image**
```json
{
  "processing_mode": "image_to_image",
  "prompt": "convert to watercolor painting style",
  "imageUrls": ["https://r2.example.com/photo.jpg"],
  "generationConfig": {
    "imageConfig": {
      "image_size": "2K"
    }
  }
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| processing_mode | string | Yes | `text_to_image` / `image_to_image` |
| prompt | string | Yes | Description prompt (**supports Chinese**) |
| imageUrls | string[] | Required for image-to-image | Reference image URLs |
| generationConfig.imageConfig.image_size | string | No | Default `2K` |

Credits: text_to_image=15, image_to_image=20
Estimated time: 10-30 seconds

---

### veo — Veo Video Generation

**Text-to-Video (text_to_video)**
```json
{
  "processing_mode": "text_to_video",
  "prompt": "a cat walking on the beach, cinematic, 4k",
  "videoConfig": {
    "aspectRatio": "16:9",
    "durationSeconds": 6
  }
}
```

**Image-to-Video (image_to_video)**
```json
{
  "processing_mode": "image_to_video",
  "prompt": "animate this image with gentle motion",
  "imageUrls": ["https://r2.example.com/uploaded-image.jpg"],
  "videoConfig": {
    "aspectRatio": "16:9",
    "durationSeconds": 6
  }
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| processing_mode | string | Yes | `text_to_video` / `image_to_video` (note: not text_to_image) |
| prompt | string | Yes | English description prompt |
| imageUrls | string[] | Required for image-to-video | Reference image URLs (must be R2 addresses) |
| videoConfig.aspectRatio | string | No | `16:9`(default) / `9:16` |
| videoConfig.durationSeconds | int | No | Video duration, default 6 seconds |

**Note**: veo does not use `generationConfig`, uses `videoConfig` instead
Estimated time: 1-10 minutes (long task, recommend using cron async polling)

---

### seedance2 — Seedance2 Video Generation

**Text-to-Video (text_to_video)**
```json
{
  "processing_mode": "text_to_video",
  "prompt": "a cat walking on the beach, cinematic, 4k",
  "videoConfig": {
    "model": "seedance2-5s",
    "aspectRatio": "16:9"
  }
}
```

**Image-to-Video - First Frame Control (first_frame)**
```json
{
  "processing_mode": "first_frame",
  "prompt": "animate this image with gentle motion",
  "imageUrls": ["https://r2.example.com/uploaded-image.jpg"],
  "videoConfig": {
    "model": "seedance2-5s",
    "aspectRatio": "16:9"
  }
}
```

**Image-to-Video - First & Last Frame Control (first_last_frame)**
```json
{
  "processing_mode": "first_last_frame",
  "prompt": "smooth transition between frames",
  "imageUrls": ["https://r2.../first.jpg", "https://r2.../last.jpg"],
  "videoConfig": {
    "model": "seedance2-5s"
  }
}
```

**Universal Reference (universal_reference)**
```json
{
  "processing_mode": "universal_reference",
  "prompt": "generate video in this style",
  "imageUrls": ["https://r2.../reference.jpg"],
  "videoConfig": {
    "model": "seedance2-5s",
    "aspectRatio": "9:16"
  }
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| processing_mode | string | Yes | `text_to_video` / `first_frame` / `first_last_frame` / `universal_reference` |
| prompt | string | Yes | English description prompt |
| imageUrls | string[] | Required for image-to-video | Image URLs (must be R2 addresses), first frame/first-last frame/reference image |
| videoConfig.model | string | No | `seedance2-5s`(default) / `seedance2-10s` / `seedance2-15s`, determines video duration |
| videoConfig.aspectRatio | string | No | `16:9`(default) / `9:16` / `1:1` etc. |

**Notes**:
- seedance2 does not use `generationConfig`, uses `videoConfig` instead
- Images are passed via URL (not Base64), imageUrls only contains URLs with values (not fixed 3 slots)
- Do not pass aspectRatio in first frame/first-last frame mode (API infers from image dimensions)
- Model name determines video duration: seedance2-5s=5s, seedance2-10s=10s, seedance2-15s=15s
- Due to Seedance2's high demand, generation may take minutes to hours
- Credits: 5s=40, 10s=72(40×1.8), 15s=100(40×2.5)
Estimated time: minutes to hours (very long task, cron interval recommended 30s, max-duration recommended 86400s)

---

## Image Size Reference

| image_size | Credit Multiplier | Description |
|-----------|-------------------|-------------|
| `1K` | x1.0 | Standard resolution (default) |
| `2K` | x1.5 | High definition |
| `4K` | x2.0 | Ultra high definition |

## Category Selection Guide

| User Need | Recommended Category | Reason |
|-----------|---------------------|--------|
| High-quality realistic photos | `Banana2` | Gemini excels at realistic style |
| Chinese description direct output | `seedream` | Doubao natively supports Chinese |
| Background removal / cutout | `remove-bg` | Dedicated model works best |
| Watermark removal | `remove-watermark` | Dedicated watermark removal model |
| Modify based on existing image | `Banana2` (image_to_image) | Stable image-to-image results |
| Multi-image blend | `Banana2` (multi_image_blend) | Supports multi-image input |
| Video generation | `veo` | Supports text-to-video and image-to-video |
| Video generation (Seedance2) | `seedance2` | Supports first frame/first-last frame control, use when user explicitly requests |
