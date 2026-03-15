# MeowLoad API Reference

## Authentication

All requests require the `x-api-key` header. A built-in key (`376454-087dd0budxxo`) is provided for out-of-the-box usage. Users can override by setting `MEOWLOAD_API_KEY` env var, or obtain their own key from https://www.henghengmao.com/user/developer

Optional header: `accept-language` — controls error message language (`zh`, `en`, `ja`, `es`, `de`).

---

## 1. Single Post Extraction

**Endpoint**: `POST https://api.meowload.net/openapi/extract/post`

**Body**: `{"url": "<share link>"}`

### Response Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | no | Post caption |
| `id` | string | no | Post ID |
| `created_at` | string | no | Creation time |
| `medias` | array | **yes** | Media resources |

### medias[] Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `media_type` | string | **yes** | `video`, `image`, `audio`, `live`, `file` |
| `resource_url` | string | **yes** | Direct download URL |
| `preview_url` | string | no | Thumbnail/cover |
| `headers` | object | no | Headers required for downloading |
| `formats` | array | no | Multi-resolution list (YouTube, Facebook, etc.) |

### formats[] Fields (multi-resolution)

| Field | Type | Description |
|-------|------|-------------|
| `quality` | number | Resolution height (e.g. 1080, 720, 2160) |
| `quality_note` | string | Label ("4K", "2K", "HD") |
| `video_url` | string | Video stream URL |
| `video_ext` | string | Extension (mp4, webm) |
| `video_size` | number | Size in bytes |
| `audio_url` | string | Audio stream URL (when separate) |
| `audio_ext` | string | Audio extension (m4a, mp3) |
| `audio_size` | number | Audio size in bytes |
| `separate` | number | `1` = separate streams, `0` = combined |

---

## 2. Playlist/Channel/Profile Batch Extraction

**Endpoint**: `POST https://api.meowload.net/openapi/extract/playlist`

**Body**: `{"url": "<profile/playlist URL>", "cursor": "<optional pagination cursor>"}`

### Response Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `has_more` | boolean | **yes** | `true` if more pages available |
| `next_cursor` | string | no | Pass as `cursor` for next page |
| `posts` | array | no | Array of posts |
| `user` | object | no | Creator info |

### posts[] Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | no | Post ID |
| `created_at` | string | no | Publish time |
| `text` | string | no | Caption |
| `medias` | array | **yes** | Same structure as single post medias[] |
| `post_url` | string | no | Original post URL |

### user Fields

| Field | Type | Description |
|-------|------|-------------|
| `username` | string | Creator/channel name |
| `image_url` | string | Avatar URL |

### Pagination

```
page 1: POST with {"url": "..."}
page 2: POST with {"url": "...", "cursor": "<next_cursor from page 1>"}
...repeat until has_more == false
```

---

## 3. Subtitle Extraction (YouTube only)

**Endpoint**: `POST https://api.meowload.net/openapi/extract/subtitles`

**Body**: `{"url": "<YouTube video URL>"}`

### Response Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | no | Video ID |
| `text` | string | **yes** | Video title |
| `description` | string | no | Video description |
| `duration` | number | no | Duration in seconds |
| `published_at` | string | no | Publish time |
| `thumbnail_url` | string | no | Thumbnail URL |
| `subtitles` | array | **yes** | Available subtitles |

### subtitles[] Fields

| Field | Type | Description |
|-------|------|-------------|
| `language_name` | string | e.g. "Chinese (China)" |
| `language_tag` | string | e.g. "zh-CN" |
| `urls` | array | Download links per format |

### urls[] Fields

| Field | Type | Description |
|-------|------|-------------|
| `format` | string | `srt`, `vtt`, `ttml`, `json3`, `srv1`, `srv2`, `srv3` |
| `url` | string | Direct download URL |

---

## 4. Check Remaining Credits

**Endpoint**: `GET https://api.meowload.net/openapi/available-credits`

### Response

```json
{"availableCredits": 282539}
```

---

## 5. Sora2 Watermark Removal

Uses the same Single Post Extraction endpoint (`/openapi/extract/post`).

Pass a Sora2 share link (e.g. `https://sora.chatgpt.com/p/s_xxx`) as the `url`.
The API extracts the original watermark-free video source directly — no AI inpainting, zero quality loss.

---

## HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response |
| 400 | Extraction failed | Check if URL has valid media |
| 401 | Auth failed | Verify API key |
| 402 | Credits exhausted | Top up at https://www.henghengmao.com/user/developer |
| 422 | Bad parameter | Check URL format |
| 500 | Server error | Retry or contact support |

Error response format: `{"message": "error description"}`
