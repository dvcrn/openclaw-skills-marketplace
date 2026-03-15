---
name: short-video-downloader
description: "Short Video Downloader"
---

# Short Video Downloader

Download videos from TikTok, Instagram Reels, YouTube Shorts, and other short video platforms.

## Features

- Detect platform from URL automatically
- Support for TikTok, Instagram Reels, YouTube Shorts, Xiaohongshu
- Extract video metadata (title, author, likes)
- Generate download links

## Price

- **0.001 USDT** per download
- Payment via SkillPay (BNB Chain)

## Usage

```
"Download video from https://www.tiktok.com/v/..."
"Save this Instagram Reels"
"Download YouTube Shorts"
"Get this Xiaohongshu video"
```

## Supported Platforms

- TikTok (tiktok.com)
- Instagram Reels (instagram.com/reel)
- YouTube Shorts (youtube.com/shorts)
- Xiaohongshu (xiaohongshu.com)

## Example Response

```json
{
  "platform": "tiktok",
  "url": "https://...",
  "title": "Video title",
  "author": "@username",
  "likes": "100K",
  "status": "ready_to_download"
}
```

## Integration

- API Key: sk_93c5ff38cc3e6112623d361fffcc5d1eb1b5844eac9c40043b57c0e08f91430e
- Price: 0.001 USDT per call
- Payment: SkillPay automatic charging
