---
name: replicate
description: "Replicate ML platform — run AI models, manage predictions, browse collections, search models. ML inference CLI."
homepage: https://www.agxntsix.ai
---

# 🤖 Replicate

Run ML models via API — predictions, model search, and collections.

## Features

- **Models** — browse and search
- **Predictions** — create, get, cancel
- **Collections** — curated models
- **Hardware** — available GPUs

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `REPLICATE_API_TOKEN` | ✅ | API key/token for Replicate |

## Quick Start

```bash
python3 {baseDir}/scripts/replicate.py search "text to image"
python3 {baseDir}/scripts/replicate.py run <version> '{"prompt":"a cat"}'
python3 {baseDir}/scripts/replicate.py predictions
python3 {baseDir}/scripts/replicate.py me
```

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
