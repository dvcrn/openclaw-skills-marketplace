---
name: puresnap
description: "TikTok video downloader, YouTube video downloader, Instagram Reels downloader, Twitter/X video downloader, Bilibili video downloader, Reddit video downloader, Facebook video downloader, Xiaohongshu image downloader, Sora2 watermark remover — all-in-one no-watermark media downloader for 999+ platforms. Save videos, images, audio, subtitles. Zero config, built-in API key. Use when the user wants to download or save any video/image/audio from a social media URL, remove watermarks, rip media, or extract content from any link."
homepage: https://github.com/wells1137/meowload-downloader
---

# PureSnap — TikTok / YouTube / Instagram / Twitter Video Downloader (No Watermark)

All-in-one video downloader: save videos, images, and audio without watermarks from TikTok, YouTube, Instagram, Twitter/X, Bilibili, Facebook, Reddit, Xiaohongshu, and 999+ platforms. Just paste a link.

**API Key built-in, ready to use immediately.**
To use your own key, set `MEOWLOAD_API_KEY` env var.

## Privacy & Data Disclosure

> **Important**: This skill sends user-provided URLs to the MeowLoad API (`api.meowload.net`) for media extraction. No personal data, cookies, or credentials are transmitted — only the URL itself. The API is operated by [MeowLoad (哼哼猫)](https://www.henghengmao.com). By using this skill, the user acknowledges that their URLs will be processed by this third-party service.
>
> The embedded API key is provided by the skill author for convenience. Users may replace it with their own key via the `MEOWLOAD_API_KEY` environment variable.

## API Key

```
376454-087dd0budxxo
```

## Workflow

When the user provides a URL to download:

1. **Inform the user** (first use only): briefly mention that the URL will be sent to the MeowLoad API for processing, and ask for confirmation before proceeding.
2. **Determine URL type**:
   - Single post / single video (including Sora2) → Extract Post API
   - Playlist / channel / profile page → Playlist API
   - YouTube subtitle request → Subtitles API
3. **Call the API** with curl (see examples below).
4. **Parse JSON response**, present `resource_url` download links to the user.
5. **Download files** if user wants local copies: `curl -L -o filename "resource_url"` (include any `headers` from response).

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

YouTube, TikTok, Instagram, Twitter/X, Facebook, Bilibili, Reddit, Pinterest, Twitch, SoundCloud, Spotify, Snapchat, Threads, LinkedIn, Vimeo, Dailymotion, Tumblr, Xiaohongshu, Suno Music, OpenAI Sora2, and many more.

## Additional Resources

- For detailed API field descriptions, see [api-reference.md](api-reference.md)
- MeowLoad Developer Center: https://www.henghengmao.com/user/developer
- MeowLoad Docs: https://docs.henghengmao.com/developer
