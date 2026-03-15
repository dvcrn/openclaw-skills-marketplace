---
name: uploadthing
description: "Uploadthing file hosting — upload, list, and manage files via the Uploadthing API. Simple file uploads with automatic CDN delivery, file metadata, and usage tracking. Built for AI agents — Python stdlib only, zero dependencies. Use for file uploads, file hosting, CDN delivery, media management, and file storage for web apps."
homepage: https://www.agxntsix.ai
---

# 📤 Uploadthing

Uploadthing file hosting — upload, list, and manage files via the Uploadthing API.

## Features

- **File upload** — upload files with metadata
- **File listing** — list uploaded files with filtering
- **File deletion** — remove files by key
- **URL generation** — get CDN URLs for files
- **Usage tracking** — storage and bandwidth usage
- **File metadata** — name, size, type, upload date
- **Bulk operations** — delete multiple files
- **App info** — application configuration

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `UPLOADTHING_SECRET` | ✅ | API key/token for Uploadthing |

## Quick Start

```bash
# List uploaded files
python3 {baseDir}/scripts/uploadthing.py files --limit 50
```

```bash
# Upload a file
python3 {baseDir}/scripts/uploadthing.py upload document.pdf
```

```bash
# Delete files
python3 {baseDir}/scripts/uploadthing.py delete --keys file_key1,file_key2
```

```bash
# Get usage stats
python3 {baseDir}/scripts/uploadthing.py usage
```



## Commands

### `files`
List uploaded files.
```bash
python3 {baseDir}/scripts/uploadthing.py files --limit 50
```

### `upload`
Upload a file.
```bash
python3 {baseDir}/scripts/uploadthing.py upload document.pdf
```

### `delete`
Delete files.
```bash
python3 {baseDir}/scripts/uploadthing.py delete --keys file_key1,file_key2
```

### `usage`
Get usage stats.
```bash
python3 {baseDir}/scripts/uploadthing.py usage
```

### `app-info`
Get app configuration.
```bash
python3 {baseDir}/scripts/uploadthing.py app-info
```

### `url`
Get file URL.
```bash
python3 {baseDir}/scripts/uploadthing.py url file_key
```

### `rename`
Rename a file.
```bash
python3 {baseDir}/scripts/uploadthing.py rename file_key "new-name.pdf"
```


## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
# JSON (default, for programmatic use)
python3 {baseDir}/scripts/uploadthing.py files --limit 5

# Human-readable
python3 {baseDir}/scripts/uploadthing.py files --limit 5 --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/uploadthing.py` | Main CLI — all Uploadthing operations |

## Data Policy

This skill **never stores data locally**. All requests go directly to the Uploadthing API and results are returned to stdout. Your data stays on Uploadthing servers.

## Credits
---
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
