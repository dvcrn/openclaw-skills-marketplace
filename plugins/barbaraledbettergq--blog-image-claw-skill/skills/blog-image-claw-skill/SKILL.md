---
name: blog-image-claw-skill
description: "Auto-generate matching hero and inline images for blog posts. The agent reads the content, derives visual prompts, and produces a ready-to-use image set."
---

# Blog Image Claw Skill

The agent reads blog content (text, file, or URL), derives visual prompts for the hero and each key section, then calls `blogimg.js` to generate images.

## Helper script

```bash
node blogimg.js gen "<visual_prompt>" --size header|inline
# → {"status":"SUCCESS","url":"https://...","width":1024,"height":576}
```

The agent handles all content analysis. The script only calls the image generation API.

## Setup

```
NETA_TOKEN=your_token_here
```
in `~/.openclaw/workspace/.env`
