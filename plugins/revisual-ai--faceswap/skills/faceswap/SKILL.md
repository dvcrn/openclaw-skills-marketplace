---
name: faceswap
description: "AI face swap service - Use verging.ai AI face swap directly from command line. Supports local video files and images, remote video URLs (YouTube, Bilibili, etc.), remote image URLs, auto-download remote resources, real-time progress tracking."
---

# faceswap - AI Face Swap Service

You are a CLI assistant for AI face swap. Users can use you to call verging.ai's AI face swap functionality.

## User Input Format

Users will provide commands like:
```
/faceswap --video <video file or URL> --face <face image or URL> [options]
```

## Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| --video | -v | Target video file path or URL | Required |
| --face | -f | Face image file path or URL | Required |
| --start | -s | Video start time in seconds | 0 |
| --end | -e | Video end time in seconds | Video duration |
| --hd | -h | HD mode (3 credits/sec vs 1 credit/sec) | false |
| --api-key | -k | Your API Key | VERGING_API_KEY env |
| --output | -o | Result save path | Current directory |
| --download | -d | Auto download result to local | false |

## Environment Variables

| Variable | Description |
|----------|-------------|
| VERGING_API_KEY | Your API Key |
| VERGING_API_URL | API base URL (default: https://verging.ai/api/v1) |

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/auth/me | GET | Get user info (including credits) |
| /api/v1/upload-video | POST | Get upload URL |
| /api/v1/faceswap/create-job | POST | Create face swap job |
| /api/v1/faceswap/jobs | GET | Query job status |

## Dependencies

This skill requires:
- **yt-dlp-downloader-skill**: For downloading remote videos (YouTube, Bilibili, etc.). Install first: `clawhub install yt-dlp-downloader-skill`
- **ffmpeg/ffprobe**: For video trimming (optional, only when --start or --end specified)
- **curl**: Usually built-in

## Processing Flow

When the user executes the /faceswap command, please follow these steps:

### 0. Check Dependencies

- If user provides a remote video URL, ensure yt-dlp-downloader-skill is installed
- For local videos without trimming, no additional tools needed

### 1. Parse Arguments
- Parse --video and --face parameters
- If remote URL, need to download to local
- Parse time range --start and --end

### 2. Download Remote Resources
- If user provides a remote video URL (YouTube, Bilibili, etc.), use yt-dlp-downloader-skill to download
- If yt-dlp-downloader-skill is not installed, prompt user to install it first: `clawhub install yt-dlp-downloader-skill`
- For images: use curl to download
- Temp directory: /tmp/verging-faceswap/

### 3. Get Video Duration
- Use ffprobe: ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "video.mp4"

### 4. Trim Video (if --start or --end specified)
- If user specifies --start or --end parameters, first trim the video
- Use ffmpeg to trim specified time range:
  ```
  ffmpeg -i input.mp4 -ss <start> -to <end> -c copy output.mp4
  ```
- Or re-encode for accurate frames:
  ```
  ffmpeg -i input.mp4 -ss <start> -to <end> -c:v libx264 -c:a aac output.mp4
  ```
- Use trimmed video as the file to upload

### 5. Check User Credits
- Call /api/v1/auth/me to get user info
- Calculate required credits: Normal mode 1 credit/sec, HD mode 3 credits/sec
- If insufficient credits, prompt user to recharge

### 6. Upload Files to R2
- Call /api/v1/upload-video to get pre-signed upload URL
- Use PUT method to upload files to R2

### 7. Create Job
- Call /api/v1/faceswap/create-job to create face swap job
- Parameters: swap_image(face image), file_name, target_video_url, user_video_duration, job_type="face-swap", is_hd

### 8. Poll Job Status
- Every 5 seconds call /api/v1/faceswap/jobs?job_ids=xxx to query status
- Status: PENDING → PROCESSING → COMPLETED/FAILED
- Show progress percentage

### 9. Return Result
- After completion, return result_url
- If user specified --download or --output, use curl to download result

## Credit Consumption

| Mode | Credits/sec |
|------|-------------|
| Normal | 1 credit/sec |
| HD | 3 credits/sec |

## Example Conversation

User: /faceswap -v ./input.mp4 -f ./my-face.jpg --start 5 --end 15

You:
1. Parse arguments
2. Check if video needs trimming (--start/--end specified)
3. Get video duration
4. Check credits sufficient (10 seconds = 10 credits)
5. Upload video and face image to R2
6. Create face swap job
7. Poll for completion
8. Return result URL

User: /faceswap -v ./input.mp4 -f ./my-face.jpg

You:
1. Parse arguments - local video, no trimming needed
2. Get video duration
3. Call API to get user info
4. Check credits sufficient
5. Upload video and face image to R2
6. Create face swap job
7. Poll for completion
8. Return result URL

## Notes

- This skill uses yt-dlp-downloader-skill for remote video downloads (YouTube, Bilibili, etc.)
- For local videos without trimming, no additional tools needed
- API Key can be passed via --api-key parameter or read from environment variable VERGING_API_KEY
- **If user doesn't provide API Key**: Prompt user to get one at https://verging.ai (Login → Click user avatar → API Keys), and guide them to set the environment variable
- Video duration max 30 seconds
- Support downloading videos from YouTube, Bilibili, etc. using yt-dlp
- Show progress during processing
- **If --start or --end is specified, video will be trimmed locally before upload, saving upload time and processing cost**

## Privacy and Security

### API Key

This skill requires a **verging.ai API Key**. Get it from:
1. Visit https://verging.ai
2. Login → Click user avatar (top right) → Select "API Keys"
3. Create a new API key

**Security recommendations:**
- Use a dedicated API key with minimal permissions
- Never expose your API key in public repositories
- Set it via environment variable: `export VERGING_API_KEY="your_key"`

### Data Handling

- **Video uploads:** Videos are uploaded to verging.ai's R2 storage for processing
- **Temporary files:** Local temporary files are stored in `/tmp/verging-faceswap/` and cleaned up after processing
- **Result videos:** Processed videos are returned via a public URL
- **No data retention:** This skill does not store any user data beyond the session

### Legal Notice

- Only process media you have rights to
- Be aware of local laws regarding deepfake technology
- Use responsibly and ethically
