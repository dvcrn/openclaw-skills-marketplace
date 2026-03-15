---
name: model-intel
description: "Live LLM model intelligence from OpenRouter. Compare pricing, search models by name, find the best model for any task — code, reasoning, creative, fast, cheap, vision, long-context. Real-time data from 200+ models. Use when choosing models, comparing costs, or auditing your AI stack."
homepage: https://www.agxntsix.ai
---

# Model Intel 🧠💰

Live LLM model intelligence — pricing, capabilities, and comparisons from OpenRouter.

## When to Use

- Finding the best model for a specific task (coding, reasoning, creative, fast, cheap)
- Comparing model pricing and capabilities
- Checking current model availability and context lengths
- Answering "what's the cheapest model that can do X?"

## Usage

```bash
# List top models by provider
python3 {baseDir}/scripts/model_intel.py list

# Search by name
python3 {baseDir}/scripts/model_intel.py search "claude"

# Side-by-side comparison
python3 {baseDir}/scripts/model_intel.py compare "claude-opus" "gpt-4o"

# Best model for a use case
python3 {baseDir}/scripts/model_intel.py best fast
python3 {baseDir}/scripts/model_intel.py best code
python3 {baseDir}/scripts/model_intel.py best reasoning
python3 {baseDir}/scripts/model_intel.py best cheap
python3 {baseDir}/scripts/model_intel.py best vision

# Pricing details
python3 {baseDir}/scripts/model_intel.py price "gemini-flash"
```

## Use Cases

| Command | When |
|---------|------|
| `best fast` | Need lowest latency |
| `best cheap` | Budget-constrained |
| `best code` | Programming tasks |
| `best reasoning` | Complex logic/math |
| `best vision` | Image understanding |
| `best long-context` | Large document processing |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
