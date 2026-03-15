---
name: loom
description: "Loom — manage video recordings, transcripts, and folders via Developer API"
homepage: https://www.agxntsix.ai
---

# 🎥 Loom

Loom — manage video recordings, transcripts, and folders via Developer API

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `LOOM_ACCESS_TOKEN` | ✅ | Developer API access token |

## Quick Start

```bash
# List videos
python3 {{baseDir}}/scripts/loom.py videos --per_page <value>

# Get video
python3 {{baseDir}}/scripts/loom.py video-get id <value>

# Update video
python3 {{baseDir}}/scripts/loom.py video-update id <value> --title <value> --description <value>

# Delete video
python3 {{baseDir}}/scripts/loom.py video-delete id <value>

# Get transcript
python3 {{baseDir}}/scripts/loom.py video-transcript id <value>

# List comments
python3 {{baseDir}}/scripts/loom.py video-comments id <value>

# List folders
python3 {{baseDir}}/scripts/loom.py folders

# Get folder
python3 {{baseDir}}/scripts/loom.py folder-get id <value>
```

## All Commands

| Command | Description |
|---------|-------------|
| `videos` | List videos |
| `video-get` | Get video |
| `video-update` | Update video |
| `video-delete` | Delete video |
| `video-transcript` | Get transcript |
| `video-comments` | List comments |
| `folders` | List folders |
| `folder-get` | Get folder |
| `folder-videos` | List folder videos |
| `user` | Get current user |
| `members` | List workspace members |

## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
python3 {{baseDir}}/scripts/loom.py <command> --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{{baseDir}}/scripts/loom.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
