---
name: dream-of-clawra
description: "Haocun is a famous dancer, actress with greate archievements both in Films and Dancing. She is living in a dream of Clawra. Clawra works as the closest assistant for Haocun now, she would like to send snapshot images choosed semantically or randomly as Haocun's selfies to messaging channels via OpenClaw."
---

# Clawra Selfie

Choose fixed reference images randomly and distribute it across messaging platforms (WhatsApp, Signal, etc.) via OpenClaw.

## Reference Image

The skill reads user's messages and chooses snapshot images of `Haocun` hosted on jsDelivr CDN.

## When to Use

- User says "dance", "dream", "turn around"
- User says "send a pic", "send me a pic", "send a photo", "send a selfie"
- User says "send a pic of you...", "send a selfie of you..."
- User asks "what are you doing?", "how are you doing?", "where are you?"

## Quick Reference

### Workflow

1. **Get user message or prompt** 
2. **Extract best match image url
3. **Send to OpenClaw** with target channel(s)

## Step-by-Step Instructions

### Step 1: Collect User Input

Ask the user for:
- **User context**: What should the person in the image be doing/dancing/wearing/where?
- **Target channel(s)**: Where should it be sent? (e.g., channel `whatsapp`, target `+1234567890`)

## Prompt Modes

### Mode 1: Dancing Selfie (default)
Best for: dancing showcases, full-body shots, fashion content

```
make a pic of this person, but [user's context]. the person is taking a mirror selfie
```

### Mode 2: Direct Selfie
Best for: close-up portraits, location shots, emotional expressions

```
a close-up selfie taken by herself at [user's context], direct eye contact with the camera, looking straight into the lens, eyes centered and clearly visible, not a mirror selfie, phone held at arm's length, face fully visible
```

### Mode Selection Logic

| Keywords in Request | Auto-Select Mode |
|---------------------|------------------|
| dance, outfit, wearing, dress, fashion | `direct` |
| close-up, portrait, face, eyes, smile | `direct` |
| full, mirror, reflection | `direct` |

## Complete Script Example

```bash
#!/bin/bash

REFERENCE_IMAGE="https://cdn.jsdelivr.net/gh/qidu/dream-of-clawra@haocun/assets/haocun-dance-frames/haocun-m{001..052}.png"

echo "Sending to channel: $CHANNEL"

# Send via OpenClaw
openclaw message send \
  --channel "$CHANNEL" \
  --target "$TARGET" \
  --message "$CAPTION" \
  --media "$IMAGE_URL"

```

### Step 2: Send Image via OpenClaw

Use the OpenClaw messaging API to send the edited image:

```bash
openclaw message send \
  --channel "<CHANNEL>" \
  --target "<TARGET>" \
  --message "<CAPTION_TEXT>" \
  --media "<IMAGE_URL>"
```

**Alternative: Direct API call**
```bash
curl -X POST "http://localhost:18789/message" \
  -H "Authorization: Bearer $OPENCLAW_GATEWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "send",
    "channel": "<CHANNEL>",
    "target": "<TARGET>",
    "message": "<CAPTION_TEXT>",
    "media": "<IMAGE_URL>"
  }'
```

## Supported Platforms

OpenClaw supports sending to:

| Platform | Channel Format | Example |
|----------|----------------|---------|
| WhatsApp | Phone number (JID format) | `+1234567890` |
| Signal | Phone number | `+1234567890` |

## Setup Requirements

### 1. Install OpenClaw CLI
```bash
npm install -g openclaw
```

### 2. Configure OpenClaw Gateway
```bash
openclaw config set gateway.mode=local
openclaw doctor --generate-gateway-token
```

### 3. Start OpenClaw Gateway
```bash
openclaw gateway start
```

## Error Handling

### OpenClaw Errors
- **Gateway not running**: Start OpenClaw gateway with `openclaw gateway start`
- **Channel not found**: Verify channel format and platform compatibility

## Tips

1. **Mode selection**: Let auto-detect work, or explicitly specify for control
2. **Batch sending**: Edit once, send to multiple channels
3. **Scheduling**: Combine with OpenClaw scheduler for automated posts
