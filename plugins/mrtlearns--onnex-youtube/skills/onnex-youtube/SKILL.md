---
name: onnex-youtube
description: "YouTube transcripts, 4K downloads, and video exploration. Onnex-owned fork of youtube-ultimate. Security reviewed before install."
---

# onnex-youtube

Onnex-owned, security-reviewed fork of **youtube-ultimate** by globalcaos.

Upstream is monitored daily -- changes are security-audited before being ported here.

## What It Does

- **Transcripts** -- Full transcript from any YouTube URL. No API quota, no billing.
- **4K Downloads** -- Save videos locally via yt-dlp.
- **Video Exploration** -- Search, video details, channel info, comments, playlists.
- **Frame Analysis** -- Combine with the `video-frames` skill for diagram/visual extraction.

## Usage

```bash
uv run youtube.py transcript <URL>                  # Full transcript
uv run youtube.py transcript <URL> --timestamps     # With timestamps
uv run youtube.py download <URL> -o ~/Videos        # Download video
uv run youtube.py search "query" -l 10              # Search
uv run youtube.py video <URL>                       # Video details
```

## Security Notes

Reviewed 2026-03-04 by Oppy. Upstream: youtube-ultimate v4.2.2 (globalcaos).
