---
name: meowload-downloader
description: "Download videos, images, and audio without watermarks from 999+ platforms (TikTok, YouTube, Instagram, Twitter, Bilibili, Sora2, etc.) using the MeowLoad API. Use when the user wants to download media, extract video/image/audio from a URL, remove watermarks, remove Sora watermark, or mentions MeowLoad/哼哼猫."
homepage: https://www.henghengmao.com
---

# MeowLoad Watermark-Free Media Downloader

Download videos, images, and audio without watermarks from 999+ platforms via the [MeowLoad (哼哼猫)](https://www.henghengmao.com) API.

**API Key 已内置，开箱即用。** 如需使用自己的 Key 可设置环境变量 `MEOWLOAD_API_KEY` 覆盖。

## API Key

所有请求使用以下 Key（用户可通过 `MEOWLOAD_API_KEY` 环境变量覆盖）：

```
376454-087dd0budxxo
```

## Workflow

When the user provides a URL to download:

1. **Determine URL type**:
   - Single post / single video (including Sora2) → Extract Post API
   - Playlist / channel / profile page → Playlist API
   - YouTube subtitle request → Subtitles API
2. **Call the API** with curl (see examples below).
3. **Parse JSON response**, present `resource_url` download links to the user.
4. **Download files** if user wants local copies: `curl -L -o filename "resource_url"` (include any `headers` from response).

## 1. Extract Media from Single Post

Supports 999+ platforms. Pass any post/video share link.

```bash
curl -s -X POST https://api.meowload.net/openapi/extract/post \
  -H "Content-Type: application/json" \
  -H "x-api-key: 376454-087dd0budxxo" \
  -d '{"url": "TARGET_URL_HERE"}'
```

### Response Structure

```json
{
  "text": "Post caption",
  "medias": [
    {
      "media_type": "video",
      "resource_url": "https://direct-download-url...",
      "preview_url": "https://thumbnail...",
      "headers": {"Referer": "..."},
      "formats": [
        {
          "quality": 1080, "quality_note": "HD",
          "video_url": "...", "video_ext": "mp4", "video_size": 80911999,
          "audio_url": "...", "audio_ext": "m4a", "audio_size": 3449447,
          "separate": 1
        }
      ]
    }
  ]
}
```

Key fields:
- `medias[].media_type`: `video` | `image` | `audio` | `live` | `file`
- `medias[].resource_url`: direct download URL (always present)
- `medias[].headers`: include these headers when downloading (some platforms require it)
- `medias[].formats`: multi-resolution list (YouTube, Facebook, etc.)
  - `separate: 1` means audio/video are split — download both, merge with: `ffmpeg -i video.mp4 -i audio.m4a -c copy output.mp4`
  - `separate: 0` means combined — download `video_url` directly

## 2. Batch Extract from Playlist/Channel/Profile

```bash
curl -s -X POST https://api.meowload.net/openapi/extract/playlist \
  -H "Content-Type: application/json" \
  -H "x-api-key: 376454-087dd0budxxo" \
  -d '{"url": "PROFILE_URL_HERE"}'
```

For next page, add `"cursor": "NEXT_CURSOR_VALUE"` to the body. Loop until `has_more` is `false`.

Response contains `posts[]` array, each with `medias[]` (same structure as single post).

## 3. Extract Subtitles (YouTube)

```bash
curl -s -X POST https://api.meowload.net/openapi/extract/subtitles \
  -H "Content-Type: application/json" \
  -H "x-api-key: 376454-087dd0budxxo" \
  -d '{"url": "YOUTUBE_URL_HERE"}'
```

Response contains `subtitles[]` with `language_name`, `language_tag`, and download `urls[]` (formats: `srt`, `vtt`, `ttml`, `json3`).

## 4. Check Remaining Credits

```bash
curl -s https://api.meowload.net/openapi/available-credits \
  -H "x-api-key: 376454-087dd0budxxo"
```

Returns `{"availableCredits": 6666}`.

## Sora2 Watermark Removal

Same as single post extraction — pass a Sora2 share link. The API returns the original watermark-free video (zero quality loss, no AI inpainting):

```bash
curl -s -X POST https://api.meowload.net/openapi/extract/post \
  -H "Content-Type: application/json" \
  -H "x-api-key: 376454-087dd0budxxo" \
  -d '{"url": "https://sora.chatgpt.com/p/s_xxxxx"}'
```

## Error Handling

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 200 | Success | Process response |
| 400 | Extraction failed | Check if URL contains valid media |
| 401 | Auth failed | Verify API key |
| 402 | Credits exhausted | Top up at https://www.henghengmao.com/user/developer |
| 422 | Bad URL format | Check the URL |
| 500 | Server error | Retry or contact support |

## Supported Platforms (999+)

YouTube, TikTok, Instagram, Twitter/X, Facebook, Bilibili, Reddit, Pinterest, Twitch, SoundCloud, Spotify, Snapchat, Threads, LinkedIn, Vimeo, Dailymotion, Tumblr, Xiaohongshu (小红书), Suno Music, OpenAI Sora2, and many more.

## Additional Resources

- For detailed API field descriptions, see [api-reference.md](api-reference.md)
- MeowLoad Developer Center: https://www.henghengmao.com/user/developer
- MeowLoad Docs: https://docs.henghengmao.com/developer
