---
name: smtools-image-generation
description: "Generate images from text prompts using AI models via OpenRouter or Kie.ai. Use when the user asks to generate, create, draw, or illustrate an image."
---

# Image Generation Skill

Generate images from text prompts. Default provider is **OpenRouter** (synchronous). Alternative: **Kie.ai** (async, task-based).

## When to Activate

Activate when the user asks to:
- Generate, create, draw, paint, illustrate, or render an image
- Make a picture, artwork, photo, or illustration
- Visualize something as an image

## How to Use

Run the generation script with an absolute path to avoid directory change prompts:

```bash
bash SKILL_DIR/scripts/run.sh --prompt "PROMPT" [OPTIONS]
```

Replace `SKILL_DIR` with the absolute path to this skill's root directory.

### Options

| Flag | Description |
|------|-------------|
| `-p, --prompt` | Text prompt (required) |
| `--provider` | `openrouter` (default) or `kie` |
| `-m, --model` | Model name (provider-specific) |
| `-o, --output` | Output file path |
| `-c, --config` | Path to config.json |
| `--list-models` | List available models |
| `-v, --verbose` | Debug output to stderr |

### Output

The script outputs JSON to stdout:

```json
{"status": "ok", "image_path": "/absolute/path/to/image.png", "model": "google/gemini-3.1-flash-image-preview", "provider": "openrouter"}
```

After successful generation, show the user the image path and confirm the image was created.

## Provider Selection

- **OpenRouter** (default): Fast, synchronous. Models: `google/gemini-3.1-flash-image-preview`, `google/imagen-4`, `stabilityai/stable-diffusion-3`. Requires `OPENROUTER_API_KEY`.
- **Kie.ai**: Async task-based. Models: `flux-ai`, `midjourney`, `google-4o-image`, `ghibli-ai`. Requires `KIE_API_KEY`. Use when the user explicitly requests Kie.ai or a Kie-specific model.

## Examples

Basic generation:
```bash
bash SKILL_DIR/scripts/run.sh -p "A serene mountain lake at sunset"
```

Specific model:
```bash
bash SKILL_DIR/scripts/run.sh -p "Cyberpunk cityscape" -m "google/imagen-4"
```

Kie.ai provider:
```bash
bash SKILL_DIR/scripts/run.sh -p "Studio Ghibli forest" --provider kie -m ghibli-ai
```

Custom output path:
```bash
bash SKILL_DIR/scripts/run.sh -p "A red fox" -o /tmp/fox.png
```

## Error Handling

| Error | Action |
|-------|--------|
| Missing API key | Tell the user to set the environment variable (`OPENROUTER_API_KEY` or `KIE_API_KEY`) |
| Network/timeout error | Retry once. If still failing, inform the user |
| No image in response | Show the raw error from the JSON output |
| Kie.ai task timeout | Inform user that generation took too long, suggest retrying |

## Setup

If the skill has not been set up yet, run:
```bash
bash SKILL_DIR/setup.sh
```

## Security

- Never display or log API keys
- Never modify config.json without user permission
