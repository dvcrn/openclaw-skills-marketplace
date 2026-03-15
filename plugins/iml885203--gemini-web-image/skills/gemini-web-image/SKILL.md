---
name: gemini-web-image
description: "Generate images via Gemini Web API using Google AI Pro subscription. Uses browser cookies for authentication (no API key needed). Use when: (1) user wants to generate, create, draw, illustrate, or visualize anything, (2) product mockups, diagrams, concept art, (3) phrases like '幫我畫', '生成一張圖', 'make an image of', 'draw', 'create an image'. NOT for: editing or modifying existing images, video generation."
---

# Gemini Web Image (Google AI Pro)

Generate images using Gemini 3 Pro Image via the Gemini Web API.
Uses Google AI Pro subscription cookies instead of an API key — no billing or API quota needed.

## Setup

You need a **Google AI Pro subscription** and Chrome logged into `gemini.google.com`.

**Option A: Automatic (recommended)**
The script reads cookies from Chrome automatically via `browser-cookie3`. Just make sure Chrome is logged into gemini.google.com on the host machine.

**Option B: Manual cookies (headless servers)**
If browser cookie access is unavailable:
```bash
mkdir -p ~/.config/gemini
# Get these values from Chrome DevTools → Application → Cookies → gemini.google.com
cat > ~/.config/gemini/cookies.json << 'EOF'
{"secure_1psid": "YOUR_VALUE", "secure_1psidts": "YOUR_VALUE"}
EOF
chmod 600 ~/.config/gemini/cookies.json
```

### Cookie Security

- ⚠️ **Cookies are sensitive** — they grant access to your Google account session. Only run on trusted machines you control.
- Cookies are **only used locally** to authenticate with `gemini.google.com`. They are never transmitted to third-party servers.
- The script uses `browser-cookie3` (reads Chrome's local cookie store) or the manual JSON file. No cookies leave the machine except to Google's own API.
- **Do not install on shared or untrusted systems.**

### Python Dependencies

The script uses `uv` for automatic dependency management. On first run, `uv` will install:
- `gemini-webapi` — Gemini Web API client
- `browser-cookie3` — Chrome cookie reader
- `Pillow` — Image processing
- `numpy` — Array operations

No manual `pip install` needed — `uv run` handles everything.

## Generate

```bash
uv run {baseDir}/scripts/generate.py --prompt "your image description" --output "output.png"
```

## Edit (with input image)

```bash
uv run {baseDir}/scripts/generate.py --prompt "edit instructions" --output "output.png" --input "/path/to/input.png"
```

## Options

| Flag | Description |
|------|-------------|
| `--prompt` | Image description or edit instructions |
| `--output` | Output file path (default: auto-generated in cwd) |
| `--input` | Input image for editing (optional) |
| `--keep-chat` | Preserve the Gemini conversation thread after generation |

## Notes

- Uses Google AI Pro subscription quota (not API billing)
- Browser cookies are read fresh each run — no manual cookie management needed
- The script prints a `MEDIA:` line for OpenClaw to auto-attach on supported chat providers
- Gemini conversation is auto-deleted after generation to avoid clutter (use `--keep-chat` to preserve)
- Use timestamps in filenames: `yyyy-mm-dd-hh-mm-ss-name.png`
- After sending via message tool, delete the image file to save space

## Watermark Removal

The script includes automatic watermark removal via Reverse Alpha Blending (lossless). This uses bundled reference images (`scripts/bg_48.png`, `scripts/bg_96.png`).

Standalone usage: `uv run {baseDir}/scripts/remove_watermark.py input.png -o clean.png`

⚠️ **Disclaimer**: Watermark removal may violate Google's Terms of Service. This feature is provided as-is for personal use. Users are responsible for compliance with applicable terms and local laws.
