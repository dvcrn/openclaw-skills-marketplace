# SMTools Image Generation Skill

OpenClaw skill for generating images from text prompts using AI models.

## Providers

| Provider | Type | Models | Required key |
|----------|------|--------|--------------|
| **OpenRouter** (default) | Synchronous | `google/gemini-3.1-flash-image-preview`, `google/imagen-4`, `stabilityai/stable-diffusion-3` | `OPENROUTER_API_KEY` |
| **Kie.ai** | Async (task-based) | `flux-ai`, `midjourney`, `google-4o-image`, `ghibli-ai` | `KIE_API_KEY` |

---

## Installation

### Option A — via ClawHub (recommended)

```bash
clawhub install smtools-image-generation
```

That's it. OpenClaw will pick up the skill automatically.

### Option B — manually from GitHub

**Step 1.** Clone the repository:

```bash
git clone https://github.com/bzSega/SMTools-ImageGenerationSkill.git
```

**Step 2.** Copy it to the OpenClaw skills directory:

```bash
cp -r SMTools-ImageGenerationSkill ~/.openclaw/skills/smtools-image-generation
```

**Step 3.** Run the setup script (installs Python dependencies and creates `config.json`):

```bash
cd ~/.openclaw/skills/smtools-image-generation
bash setup.sh
```

---

## API Keys

The skill needs at least one API key to work.

### OpenRouter (default provider)

1. Create an account at [openrouter.ai](https://openrouter.ai)
2. Go to **Keys** → **Create key**
3. Copy the key and set it in your environment:

```bash
# Add to ~/.zshrc or ~/.bashrc so it persists across sessions
export OPENROUTER_API_KEY="sk-or-..."
```

Or put it in the `.env` file inside the skill directory:

```
~/.openclaw/skills/smtools-image-generation/.env
```

```env
OPENROUTER_API_KEY=sk-or-...
```

### Kie.ai (optional, for Midjourney / Flux / Ghibli models)

1. Create an account at [kie.ai](https://kie.ai)
2. Go to **API** → **Generate key**
3. Add it alongside the OpenRouter key:

```env
OPENROUTER_API_KEY=sk-or-...   # main provider
KIE_API_KEY=kie-...            # optional, for Kie models
```

> **Tip:** If both keys are set, OpenRouter is used by default. To switch providers, either ask explicitly ("generate with Kie.ai") or change `default_provider` in `config.json`.

---

## Usage

Once installed, the skill activates automatically in OpenClaw when you ask to generate an image:

> *"Draw a cat in space"*
> *"Generate a cyberpunk cityscape, 4k"*
> *"Create a Studio Ghibli style forest with Kie.ai"*

### Manual CLI usage

```bash
# Default: OpenRouter + gpt-image-1
bash scripts/run.sh -p "A cat in space"

# Choose a specific model
bash scripts/run.sh -p "Cyberpunk cityscape" -m "google/imagen-4"

# Use Kie.ai provider
bash scripts/run.sh -p "Studio Ghibli forest" --provider kie -m ghibli-ai

# Save to a custom path
bash scripts/run.sh -p "A red fox" -o /tmp/fox.png

# List available models for a provider
bash scripts/run.sh --provider openrouter --list-models
```

### Output

```json
{
  "status": "ok",
  "image_path": "/absolute/path/to/output/img_20260314_153000.png",
  "model": "google/gemini-3.1-flash-image-preview",
  "provider": "openrouter"
}
```

---

## Configuration

`config.json` is created by `setup.sh`. You can edit it to change defaults:

```json
{
  "default_provider": "openrouter",
  "output_dir": "output",
  "providers": {
    "openrouter": {
      "default_model": "google/gemini-3.1-flash-image-preview"
    },
    "kie": {
      "default_model": "google-4o-image",
      "poll_interval": 5,
      "max_wait": 300
    }
  }
}
```

Environment variables take priority over `config.json`:

| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | OpenRouter API key |
| `KIE_API_KEY` | Kie.ai API key |
| `IMAGE_DEFAULT_PROVIDER` | Override default provider (`openrouter` or `kie`) |
| `IMAGE_OUTPUT_DIR` | Override output directory |

---

## Diagnostics

If something isn't working, run:

```bash
bash check.sh
```

This checks Python version, dependencies, API key presence, and network connectivity.

---

## Project Structure

```
├── SKILL.md                    # OpenClaw skill definition
├── README.md
├── setup.sh                    # First-time setup
├── check.sh                    # Diagnostics
├── requirements.txt
├── assets/
│   └── config.example.json
├── scripts/
│   ├── generate.py             # CLI entry point
│   ├── config_manager.py       # Config loading
│   └── providers/
│       ├── __init__.py
│       ├── base_provider.py    # Abstract base class
│       ├── openrouter_provider.py
│       └── kie_provider.py
└── output/                     # Generated images (gitignored)
```

## Adding a New Provider

1. Create `scripts/providers/your_provider.py` implementing `BaseImageProvider`
2. Register it in `scripts/providers/__init__.py` `PROVIDERS` dict
3. Add config section in `assets/config.example.json`
4. Add env var mapping in `scripts/config_manager.py` `get_api_key()`
