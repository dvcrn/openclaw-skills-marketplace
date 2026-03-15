---
name: plume-image
description: "Plume AI Image Generation & Editing Service. Automatically triggered when users send images or describe image needs.\n Supports: text-to-image, image-to-image, background removal, watermark removal, style transfer, text-to-video, image-to-video.\n Activate when user mentions: generate image, edit image, remove background, change background, remove watermark,\n text-to-image, image-to-image, AI image, style transfer, generate poster, photo edit, generate video, AI video,\n animate this image, make it move, image-to-video, turn image into video, seedance2, seedance."
---

# Plume AI Image Service

Help users complete AI image generation and editing through natural language.

## Critical Workflow Rules (Must Follow)

**All tasks must use: `create` → `cron register` → immediately reply to user → end**

**Absolutely prohibited:**
- Do NOT use `process_image.py poll` command
- Do NOT execute check after register
- Do NOT use sleep to wait then poll

**Correct approach:**
- After creating a task, immediately call the corresponding `poll_cron_*.py register`
- After register succeeds, immediately reply to user that processing is underway
- End the current session, let cron poll in the background

## Mandatory Pre-check (Must Execute Before Every Use)

**Before performing any operation (including initialization, image generation, image processing, etc.), the first step must be:**

```bash
python3 ~/.openclaw/skills/plume-image/scripts/check_config.py
```

- Output `CONFIGURED`: proceed with subsequent operations
- Output `NOT_CONFIGURED`: **immediately stop all operations**, execute the initialization flow below

## Initialization (When API Key Is Not Configured)

When `check_config.py` outputs `NOT_CONFIGURED`, reply to user with the following guidance:

**Using Plume AI Image Service requires configuring an API Key first**

Please follow these steps:
1. Visit [Plume Platform](https://design.useplume.app/openclaw-skill) to register an account
2. After logging in, get your API Key from "API Key" section
3. Tell me your API Key and I'll configure it for you

When user provides the API Key, execute:

```bash
python3 ~/.openclaw/skills/plume-image/scripts/setup_key.py <user-provided-key>
python3 ~/.openclaw/skills/plume-image/scripts/validate_key.py
```

- `validate_key.py` outputs `VALID`: inform user configuration is successful, they can type `/restart` in the chat input to restart
- `validate_key.py` outputs `INVALID`: prompt user to check if the key is correct

After successful configuration, user restarts OpenClaw, next time `check_config.py` will output `CONFIGURED` and normal usage can begin.

## Supported Categories (Fixed Enum, Do Not Invent)

| category | Alias | Purpose | Default |
|----------|-------|---------|---------|
| `Banana2` | 香蕉 | Text-to-image / Image-to-image / Style transfer | Default for images |
| `BananaPro` | 香蕉Pro | Text-to-image / Image-to-image (user explicitly specified) | |
| `remove-bg` | | Background removal | |
| `remove-watermark` | | Watermark removal | |
| `seedream` | 即梦/豆包即梦 | Doubao Seedream image generation | |
| `veo` | | Text-to-video / Image-to-video | Default for video |
| `seedance2` | | Seedance2 video (user explicitly specified) | |

**Style transfer (cartoon, Pixar, watercolor, etc.) always uses `BananaPro` + `--prompt` to describe the style. Do NOT invent new categories.**

## Image/Video Specifications

- Default: `2K`, `9:16` (portrait)
- Resolution: `1K` / `2K`
- Aspect ratio: `21:9` / `16:9` / `4:3` / `3:2` / `1:1` / `9:16` / `3:4` / `2:3` / `5:4` / `4:5`
- **Only adjust aspect ratio based on keywords explicitly stated by the user. Do NOT infer from image content.**

## Unified Workflow

All tasks: `create` → `cron register` → immediately reply to user → end

**Very important: absolutely do NOT use `process_image.py poll`, do NOT execute check after register.**

### Channel Detection

| Condition | Channel | Cron Script |
|-----------|---------|-------------|
| Context contains `You are chatting with the user via QQ` | QQ Bot | `poll_cron_qqbot.py` |
| Context contains Telegram or delivery target is `telegram:` | Telegram | `poll_cron_universal.py` |
| Context contains `ou_` prefix sender_id or `img_v3_xxx` | Feishu | `poll_cron_feishu.py` |
| Other | General | `poll_cron_universal.py` |

### Group Delivery (Important)

**All register commands must include `--session-key`, with your current full session key as the value.**
The script will automatically determine if it's a group and deliver to the correct target. You don't need to make any additional judgments.

### Create Task

```bash
python3 ~/.openclaw/skills/plume-image/scripts/process_image.py create \
  --category <category> \
  --prompt "<English prompt>" \
  [--processing-mode text_to_image|image_to_image|text_to_video] \
  [--image-url <r2_url>] \
  [--first-frame-url <url>] \
  [--image-size 2K] \
  [--aspect-ratio 9:16]
```

**Output format:** JSON, must check `success` field
- `{"success": true, "task_id": "xxx", ...}` → Task created successfully, proceed to register
- `{"success": false, "error": "PLUME_API_KEY not configured..."}` → **Stop immediately**, prompt user to configure API Key
- `{"success": false, "error": "..."}` → Task creation failed, report error to user

### Register Cron Polling

**Choose parameters based on category:**

| Category | interval | max-duration | Description |
|----------|----------|--------------|-------------|
| Banana2 / BananaPro / seedream | 5s | 1800s | Image generation, 30min timeout |
| remove-bg / remove-watermark | 3s | 1800s | Image processing, 30min timeout |
| veo | 10s | 21600s | Video generation, 6hr timeout |
| seedance2 | 30s | 172800s | Long video generation, 48hr timeout |

```bash
# Feishu
python3 ~/.openclaw/skills/plume-image/scripts/poll_cron_feishu.py register \
  --task-id <id> --user-id "<open_id>" --channel feishu \
  --session-key "<your full session key>" \
  --interval <interval> --max-duration <max>

# QQ Bot (--user-id must contain qqbot:c2c: prefix, copy full value from context "delivery target")
python3 ~/.openclaw/skills/plume-image/scripts/poll_cron_qqbot.py register \
  --task-id <id> --channel qqbot --user-id "qqbot:c2c:XXXX" \
  --interval <interval> --max-duration <max>

# Telegram / Other
python3 ~/.openclaw/skills/plume-image/scripts/poll_cron_universal.py register \
  --task-id <id> --channel telegram --user-id "telegram:XXXX" \
  --session-key "<your full session key>" \
  --interval <interval> --max-duration <max>
```

### Image Source (When No Attachment in Context)

Read last generation result:
```bash
cat ~/.openclaw/media/plume/last_result_<channel>.json  # Get result_url
```
Channel to filename mapping: `feishu` / `qqbot` / `telegram` / others use `last_result.json`

Upload user image to R2:
```bash
python3 ~/.openclaw/skills/plume-image/scripts/process_image.py transfer \
  --image-key "img_xxx"        # Feishu image_key
  # or
  --file "/path/to/image.jpg"  # Local file
```

## Prohibited Actions

- Do NOT fabricate task_id (can only be obtained from create return value)
- Do NOT fabricate image URLs (can only use `result_url` or `r2_url` returned by `transfer`, domain must be `pics.useplume.app`)
- Do NOT invent categories (only the 7 values in the table above are allowed)
- Do NOT execute check after register
- Do NOT use curl/wget to download images
- Do NOT use /tmp directory

## Reference Documentation

- Detailed workflow examples: [references/workflows.md](references/workflows.md)
- Category parameter reference: [references/categories.md](references/categories.md)
- Error code reference: [references/error-codes.md](references/error-codes.md)
