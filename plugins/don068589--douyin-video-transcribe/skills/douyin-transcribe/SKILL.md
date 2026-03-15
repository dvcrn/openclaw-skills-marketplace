---
name: douyin-transcribe
description: "Extract audio from Douyin (抖音/TikTok China) videos and transcribe to text using Whisper. Trigger when user sends a Douyin link (v.douyin.com or www.douyin.com/video/) and asks for transcription, extract text, analyze video content, or summarize."
---

# Douyin Video Transcribe

Extract speech from Douyin videos and convert to text. Supports Chinese/English, cross-platform (Windows/macOS/Linux).

## Core Principle

Douyin has strict anti-scraping. Must:
1. Load page in browser, wait for video stream
2. Extract real CDN URL from DOM or network requests
3. Download with `Referer: https://www.douyin.com/` header (403 without it)
4. Convert audio to 16kHz mono WAV for Whisper

## Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| ffmpeg | Audio extraction | `brew install ffmpeg` / `winget install ffmpeg` / `apt install ffmpeg` |
| whisper | Speech-to-text | `pip install openai-whisper` |
| curl | Download video | Built-in (Windows: `curl.exe`) |

## Workflow

### 1. Resolve Short URL

Douyin share links are usually `v.douyin.com/xxx`, resolve to full URL:

```bash
# macOS/Linux
curl -sL -o /dev/null -w '%{url_effective}' "https://v.douyin.com/xxx/"

# Windows PowerShell
curl.exe -sL -o NUL -w "%{url_effective}" "https://v.douyin.com/xxx/"
```

Output: `https://www.douyin.com/video/7616020798351871284`

Video ID is the 19-digit number in URL.

### 2. Get Video URL

Open video page in browser, wait 3-5 seconds, execute JS:

```javascript
(() => {
  const videos = document.querySelectorAll('video');
  for (const v of videos) {
    const src = v.currentSrc || v.src;
    if (src && src.startsWith('http') && !src.includes('uuu_265')) {
      return src;
    }
  }
  return null;
})()
```

**Key points:**
- Returns `null`: Page not loaded, retry after waiting
- Contains `uuu_265`: Placeholder video, retry after waiting
- Starts with `blob:`: Streaming, wait for real URL
- CDN URLs expire (~2 hours), re-fetch if needed

### 3. Download Video

```bash
# macOS/Linux
curl -L -H "Referer: https://www.douyin.com/" -o video.mp4 "<CDN_URL>"

# Windows
curl.exe -L -H "Referer: https://www.douyin.com/" -o video.mp4 "<CDN_URL>"
```

**Referer header is required, otherwise 403.**

### 4. Extract Audio

```bash
ffmpeg -i video.mp4 -ar 16000 -ac 1 -c:a pcm_s16le audio.wav -y
```

Parameters:
- `-ar 16000`: 16kHz sample rate (Whisper requirement)
- `-ac 1`: Mono channel
- `-c:a pcm_s16le`: 16-bit PCM

### 5. Transcribe

```bash
python -m whisper audio.wav --model small --language zh
```

**Model selection:**

| Model | Size | 5-min video (CPU) | Accuracy | Use case |
|-------|------|-------------------|----------|----------|
| tiny | 75MB | ~30s | Fair | Quick preview |
| base | 142MB | ~1min | Good | Daily use |
| small | 466MB | ~3min | Better | **Recommended** |
| medium | 1.5GB | ~8min | Best | High accuracy |

**Language:**
- Chinese: `--language zh`
- English: `--language en`
- Auto-detect: omit flag (slower)

Output files in current directory: `audio.txt`, `audio.srt`, `audio.json`

## Troubleshooting

| Issue | Detection | Solution |
|-------|-----------|----------|
| Short URL fails | Returns non-douyin.com | Check link completeness, remove share text noise |
| Video URL not found | JS returns null | Wait 3-5s and retry, max 3 times |
| Placeholder video | URL contains `uuu_265` | Page not loaded, wait and retry |
| Download 403 | curl returns 403 | Check Referer header; URL may be expired |
| Whisper hangs | No output for long time | First run downloads model (~460MB for small) |
| Garbled output | Terminal shows gibberish | Normal, read .txt file directly |
| Out of memory | Process killed | Use smaller model (base/tiny) |

## Output Convention

Name files by video ID, save to user-specified directory:

```
output/
├── 7616020798351871284.mp4   # Original video (optional)
├── 7616020798351871284.wav   # Audio (delete after)
├── 7616020798351871284.txt   # Transcript
└── 7616020798351871284.srt   # Subtitles (optional)
```

## Scripts (Optional)

Helper scripts in skill directory:

- `scripts/get_video_url.js`: Browser-side video URL extraction with multiple methods
- `scripts/transcribe.py`: CLI one-click transcription (requires video URL)

Scripts are accelerators, not required. Implement yourself after understanding the workflow.

## Notes

- **Article links** (/article/): Use browser snapshot directly, no transcription needed
- **Douyin AI summary**: Some video pages have AI-generated chapter summaries, extract from snapshot as supplement
- **Other platforms**: This skill is for Douyin only. Use yt-dlp for YouTube/Bilibili
