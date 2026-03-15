---
name: twitter-video-download
description: "Download videos from Twitter/X posts. Just give it a tweet URL and it will download the video to your specified location."
---

# Twitter Video Download

Download videos from Twitter/X posts using yt-dlp.

## Setup

```bash
# Install yt-dlp
pip install yt-dlp

# Configure proxy (required)
# Twitter/X is overseas, proxy is needed to access
# Please replace with your proxy address
setx PROXY_URL "http://your-proxy-address:port"
```

## Usage in OpenClaw

Just tell me:
> "Download this Twitter video: https://x.com/xxx/status/xxx"

Or specify a save location:
> "Download video to D:\Videos: https://x.com/xxx/status/xxx"

I will automatically call this skill to execute the download.

## Command Line Usage

```bash
# Enter skill directory
cd [skill_directory]\scripts

# Set proxy environment variable (replace with your proxy)
set PROXY_URL=http://your-proxy-address:port

# Download video
node download.mjs "https://twitter.com/username/status/123456789"

# Specify output directory
node download.mjs "https://twitter.com/username/status/123456789" --output "D:\Downloads"

# Specify filename
node download.mjs "https://twitter.com/username/status/123456789" --filename "my_video"
```

## Options

- `-o, --output <path>`: Output directory (default: current directory)
- `-f, --filename <name>`: Custom filename (without extension)
- `-q, --quality <quality>`: Video quality (best/bestvideo/worst)

## Examples

```
node download.mjs "https://x.com/username/status/123456789" --output "D:\Downloads"
```

## Notes

- Supports twitter.com and x.com links
- Supports GIF download (converted to MP4)
- Proxy is required, otherwise SSL connection error will occur
- Videos are saved in MP4 format
