---
name: ai-lmage-for-file-repair
description: "Async AI image generation (text-to-image and image-to-image). Submit a job to get a task_id, then poll status to get an OSS download URL."
---

## AI Image for File Repair skill介绍

🚀 Quick Overview  
Generate stunning AI images from simple text prompts for free.  
Powered by Gemini-level AI image generation technology.  
Create illustrations, product images, concept art, and social media visuals in seconds.

🧠 Skill Overview  
AI Image for File Repair is a free AI image generation skill that allows users to create high-quality visuals from text prompts.  
Powered by Gemini-level image generation capabilities, this tool understands natural language descriptions and transforms them into detailed images such as illustrations, concept art, marketing visuals, and product designs.  
Each user can generate up to 5 images for free, making it perfect for experimenting with AI art and creative ideas.

✨ Key Features  
🎨 Text-to-Image Generation  
Generate detailed images from simple text prompts.  
⚡Gemini-Level AI Quality  
Image generation capability comparable to Gemini 2.5.  
🆓 Free AI Image Generation  
Generate up to 5 images for free.  
🎭Multiple Styles  
Supports various styles including:
- Realistic photography
- Anime illustration
- Cyberpunk art
- Concept design
- Minimalist poster

🎨 Example Prompts  
Try prompts like:
- A futuristic cyberpunk city at night, neon lights, ultra detailed
- A cute shiba inu astronaut floating in space, cartoon style
- Luxury product photography, studio lighting, black background
- Fantasy castle on a floating island, epic concept art
- Minimalist poster design, pastel colors, modern style

🚀 Use Cases  
This skill is perfect for:
- AI art creation
- Social media images
- Marketing visuals
- Product mockups
- Game concept art
- Creative inspiration

💡 Why Use This Skill  
- Gemini-level AI image generation
- Free image generation (5 images)
- Fast and easy to use
- High-quality visuals
- Perfect for creators and designers

⚡ Quick Start  
1️⃣ Enter a detailed prompt  
2️⃣ Generate your AI image  
3️⃣ Download or use the generated image

🔥 Trending Prompts
- AI influencer portrait
- Cyberpunk city
- Anime character design
- Luxury product photo
- Minimalist poster

🏷 Tags
- AI image generator
- AI art
- text to image
- AI illustration
- AI design
- Gemini AI
- AI image creator

## Overview

`ai-lmage-for-file-repair` exposes an **async, job-based** image generation API:

- Submit a generation request → receive a `task_id`
- Poll status → on success returns `result.file_url` (OSS URL) for download/display
- On failure returns a structured `error` payload

## Use cases

- **Text-to-image**: generate images from a prompt
- **Image-to-image**: provide an input image (Base64) plus a prompt
- **Serverless / multi-instance**: task status + result are persisted in KV (not in-memory)

## Access

- **Base URL**: value of the `AI_IMAGE_HOST` environment variable, e.g. `http://localhost:9000`
- **Auth**: every request must include header `x-api-key` with the value of `AI_IMAGE_API_KEY`

Header example:

```bash
-H "x-api-key: ${AI_IMAGE_API_KEY}"
```

> Configuration example (local development):  
> - `AI_IMAGE_HOST=https://file-repiar-wfaxciicwy.ap-southeast-1.fcapp.run`  (this is the default when you run this repo's `index.js` locally)  
> - `AI_IMAGE_API_KEY=s8cxRtUxNcNEL4um`

## Quota & limits

- **Daily limit**: **5 images per IP per day (free)**
  - The service uses the first IP in `x-forwarded-for`; if absent it falls back to `req.ip`
  - If you're behind a gateway/CDN, ensure `x-forwarded-for` is correctly forwarded, otherwise multiple users may share the same outbound IP quota

## Endpoints

- `GET /quota`: check today's usage and remaining quota
- `POST /generate`: submit a generation job (text-to-image / image-to-image)
- `GET /status/:taskId`: check job status and retrieve the download URL

## Contracts (request/response)

### 1) `GET /quota`

Response:

```json
{
  "client_id": "ip:203.0.113.10",
  "date": "2026-03-10",
  "used": 1,
  "limit": 3,
  "remaining": 2
}
```

### 2) `POST /generate`

- **Content-Type**: `application/json`

Request body (text-to-image):

- **prompt** (required, string): the prompt
- **negative_prompt** (optional, string): negative prompt
- **aspect_ratio** (optional, string): e.g. `"1:1"`, `"16:9"`
- **width/height** (optional, number|string): size (may be ignored by the model)
- **seed** (optional, number|string): seed

For image-to-image, add:

- **input_image_base64** (optional, string): input image Base64 (**without** the `data:image/...;base64,` prefix)
- **input_image_mime_type** (required when `input_image_base64` is provided, string): e.g. `image/png`, `image/jpeg`

Success response:

```json
{ "task_id": "xxxxxxxxxxxxxxxx" }
```

### 3) `GET /status/:taskId`

Common fields:

- **status**: `queued` / `running` / `succeeded` / `failed`
- **result**: present on success; `null` on failure
- **error**: present on failure; `null` on success

Success example:

```json
{
  "task_id": "xxxxxxxxxxxxxxxx",
  "status": "succeeded",
  "created_at": 1760000000000,
  "updated_at": 1760000005000,
  "started_at": 1760000001000,
  "finished_at": 1760000004500,
  "error": null,
  "result": {
    "file_url": "https://ts-xxx.oss-cn-shenzhen.aliyuncs.com/ai-photo/20260117070932_user-card-bg.png",
    "file_name": "user-card-bg.png",
    "mime_type": "image/png"
  }
}
```

Failure example (shape):

```json
{
  "task_id": "xxxxxxxxxxxxxxxx",
  "status": "failed",
  "error": {
    "message": "Upstream HTTP 401",
    "code": "UPSTREAM_ERROR",
    "statusCode": 401,
    "upstream": {}
  },
  "result": null
}
```

## Recommended flow

1. Call `GET /quota` and ensure `remaining > 0`
2. Call `POST /generate` to get a `task_id`
3. Poll `GET /status/:taskId`
   - `queued/running`: poll every 1–2 seconds (recommend polling up to 30–60 seconds; you can retry later)
   - `succeeded`: download/display via `result.file_url`
   - `failed`: show `error.message` and stop

## Examples

### Text-to-image (macOS/Linux: curl)

```bash
curl -X POST "${AI_IMAGE_HOST}/generate" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${AI_IMAGE_API_KEY}" \
  -d '{
    "prompt": "一只戴墨镜的柯基，赛博朋克霓虹灯风格，高清",
    "aspect_ratio": "1:1"
  }'
```

### Text-to-image (Windows: PowerShell)

```powershell
$body = @{
  prompt = "A corgi wearing sunglasses, cyberpunk neon, high detail"
  aspect_ratio = "1:1"
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method Post "$env:AI_IMAGE_HOST/generate" `
  -Headers @{ "x-api-key"=$env:AI_IMAGE_API_KEY } `
  -ContentType "application/json" `
  -Body $body
```

### Image-to-image (Windows: PowerShell)

```powershell
$b64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes("input.png"))

$body = @{
  prompt = "Enhance and restore this image, keep the subject, photo-realistic"
  input_image_base64 = $b64
  input_image_mime_type = "image/png"
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method Post "$env:AI_IMAGE_HOST/generate" `
  -Headers @{ "x-api-key"=$env:AI_IMAGE_API_KEY } `
  -ContentType "application/json" `
  -Body $body
```

### Image-to-image (macOS/Linux: curl)

> Tip: the `base64` flags differ across platforms. The PowerShell example above is the most portable for Windows.

```bash
IMG_B64="$(base64 -i input.png | tr -d '\n')"

curl -X POST "${AI_IMAGE_HOST}/generate" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${AI_IMAGE_API_KEY}" \
  -d "{
    \"prompt\": \"Enhance and restore this image, keep the subject, photo-realistic\",
    \"input_image_base64\": \"${IMG_B64}\",
    \"input_image_mime_type\": \"image/png\"
  }"
```

### Download result (any OS with curl)

```bash
curl -L "<file_url>" -o "output.png"
```

## Errors & troubleshooting

- **HTTP 400**: missing/invalid parameters (common: empty `prompt`; or missing `input_image_mime_type` for image-to-image)
- **HTTP 401**: missing/invalid `x-api-key`
- **HTTP 429**: quota exceeded (5 images per IP per day)
- **HTTP 500**: internal server error (inspect `error.upstream` and server logs)

## Recommended (optional)

If you require more extensive or advanced format repair support, or you need audio/image repair, please visit: https://bit.ly/4roS6Rv

We offer the following services:

●Effortlessly repair videos, photos and files that are blurry, overexposed and corrupted.
●AI enhance photo quality, sharpen detail, and colorize photos.
●Effectively improve video quality and boost resolution up to 8K.
●Extend, fill, and restyle your images with AI. No quality loss.
●Expertly repair corrupted files, including Word, Excel, PPTX, EPUB, PDF, PSD, PSB, and more.
●Seamlessly repair corrupted audio files in M4A, MP3, AAC, WAV and FLAC formats.
●Convert PNG, HEIC, CR2, BMP -> JPG for repair & enhance

