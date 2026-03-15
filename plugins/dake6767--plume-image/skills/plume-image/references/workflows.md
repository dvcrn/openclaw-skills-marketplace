# Complete Workflow Reference

## Channel Flow Quick Reference

### Feishu Channel (`poll_cron_feishu.py register`)

```
Scenario A (text-to-image):        create → register(5s/120s) → reply to user → cron auto-push
Scenario B (image-to-image/bg removal): transfer(--image-key) → create → register(3s/60s) → reply to user → cron auto-push
Scenario C (modify last generated):  cat last_result_feishu.json → create(--image-url) → register(5s/120s) → reply to user
Scenario D (text-to-video veo):     create(veo, text_to_video) → register(10s/600s) → reply to user
Scenario E (image-to-video veo):    transfer → create(veo, --first-frame-url) → register(10s/600s) → reply to user
Scenario J (multi-image blend):     check image_registry.json → create(Banana2, --image-urls) → register(5s/120s) → reply to user
Scenario K (seedance2 text-to-video): create(seedance2, text_to_video) → register(30s/86400s) → reply to user
Scenario L (seedance2 image-to-video): transfer → create(seedance2, --first-frame-url) → register(30s/86400s) → reply to user
```

### QQ Bot Channel (`poll_cron_qqbot.py register`)

```
Scenario F (text-to-image):          create → register(5s/120s) → reply to user → cron push <qqimg>
Scenario G (image-to-image):         cat last_result_qqbot.json → create(--image-url) → register(5s/120s) → reply to user
Scenario H (text-to-video veo):      create(veo, text_to_video) → register(10s/600s) → reply to user → cron push <qqvideo>
Scenario H2 (text-to-video seedance2): create(seedance2, text_to_video) → register(30s/86400s) → reply to user
Scenario I (image-to-video veo):     transfer(--file) → create(veo, --first-frame-url) → register(10s/600s) → reply to user
Scenario I2 (image-to-video seedance2): transfer → create(seedance2, --first-frame-url) → register(30s/86400s) → reply to user
```

### Telegram / Other Channels (`poll_cron_universal.py register`)

Same as Feishu flow, `--user-id` format is `telegram:XXXXXXXXX`, image source is `~/.openclaw/media/inbound/`.

---

## Cron Parameter Quick Reference

| Task Type | interval | max-duration |
|-----------|----------|-------------|
| Banana2 / BananaPro / seedream | `5s` | `120s` |
| remove-bg / remove-watermark | `3s` | `60s` |
| veo | `10s` | `600s` |
| seedance2 | `30s` | `86400s` |

---

## QQ Bot Scenario Detailed Examples

### Scenario F: Text-to-Image

```bash
python3 ~/.openclaw/skills/plume-image/scripts/process_image.py create \
  --category Banana2 \
  --prompt "user's image description"

python3 ~/.openclaw/skills/plume-image/scripts/poll_cron_qqbot.py register \
  --task-id <task_id> \
  --channel qqbot \
  --user-id "qqbot:c2c:XXXX" \
  --interval 5s \
  --max-duration 120s
```

### Scenario G: Image-to-Image

> First step is always to read `last_result_qqbot.json`, never guess URLs.

```bash
cat ~/.openclaw/media/plume/last_result_qqbot.json
# Get result_url

python3 ~/.openclaw/skills/plume-image/scripts/process_image.py create \
  --category Banana2 \
  --image-url <result_url> \
  --prompt "cartoon style/Pixar style etc."

python3 ~/.openclaw/skills/plume-image/scripts/poll_cron_qqbot.py register \
  --task-id <task_id> --channel qqbot --user-id "qqbot:c2c:XXXX" \
  --interval 5s --max-duration 120s
```

### Scenario H: Text-to-Video (veo)

```bash
python3 ~/.openclaw/skills/plume-image/scripts/process_image.py create \
  --category veo --processing-mode text_to_video \
  --prompt "user's video description"

python3 ~/.openclaw/skills/plume-image/scripts/poll_cron_qqbot.py register \
  --task-id <task_id> --channel qqbot --user-id "qqbot:c2c:XXXX" \
  --interval 10s --max-duration 600s
```

### Scenario H2: Text-to-Video (seedance2)

```bash
python3 ~/.openclaw/skills/plume-image/scripts/process_image.py create \
  --category seedance2 --processing-mode text_to_video \
  --prompt "user's video description" --model "seedance2-5s" --aspect-ratio "9:16"

python3 ~/.openclaw/skills/plume-image/scripts/poll_cron_qqbot.py register \
  --task-id <task_id> --channel qqbot --user-id "qqbot:c2c:XXXX" \
  --interval 30s --max-duration 86400s
```

### Scenario I: Image-to-Video (veo)

```bash
# Method 1: User sent an image
python3 ~/.openclaw/skills/plume-image/scripts/process_image.py transfer \
  --file ~/.openclaw/qqbot/downloads/<filename>

# Method 2: Use last result
cat ~/.openclaw/media/plume/last_result_qqbot.json  # Get result_url

python3 ~/.openclaw/skills/plume-image/scripts/process_image.py create \
  --category veo --first-frame-url <url> --prompt "animate this image"

python3 ~/.openclaw/skills/plume-image/scripts/poll_cron_qqbot.py register \
  --task-id <task_id> --channel qqbot --user-id "qqbot:c2c:XXXX" \
  --interval 10s --max-duration 600s
```

### Scenario I2: Image-to-Video (seedance2)

```bash
# Get image URL (same as Scenario I)

python3 ~/.openclaw/skills/plume-image/scripts/process_image.py create \
  --category seedance2 --first-frame-url <url> \
  --prompt "cinematic motion" --model "seedance2-5s"

python3 ~/.openclaw/skills/plume-image/scripts/poll_cron_qqbot.py register \
  --task-id <task_id> --channel qqbot --user-id "qqbot:c2c:XXXX" \
  --interval 30s --max-duration 86400s
```

---

## Image Source Priority

### Feishu
1. Message contains `image_key` (`img_v3_xxx`) → `transfer --image-key`
2. No image, user refers to "the last one" → `cat last_result_feishu.json` get `result_url`
3. Neither available → prompt user to send an image

### QQ Bot
1. User sent an image this time (`~/.openclaw/qqbot/downloads/`) → `transfer --file`
2. No attachment, user refers to "this image/the one above" → `cat last_result_qqbot.json` get `result_url`
3. Not found → prompt user to send an image

### Telegram / General
1. User sent an attachment this time (`~/.openclaw/media/inbound/`) → `transfer --file`
2. No attachment, user refers to "this image/just generated" → `cat last_result_telegram.json` get `result_url`
3. Not found → prompt user to send an image

---

## veo imageUrls Slot Description

`imageUrls` has fixed 3 slots, order has semantic meaning:

| Parameter | Slot | Purpose |
|-----------|------|---------|
| `--first-frame-url` (or `--image-url`) | `[0]` | First frame (most common for image-to-video) |
| `--last-frame-url` | `[1]` | Last frame (first-last frame control) |
| `--reference-url` | `[2]` | Reference image (style merge) |

## seedance2 imageUrls Description

Pure URL array (not fixed slots), only pass URLs with values:
- `--first-frame-url` → processing_mode auto-set to `first_frame`
- `--first-frame-url` + `--last-frame-url` → `first_last_frame`
- `--reference-url` → `universal_reference`
