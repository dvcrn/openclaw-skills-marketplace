---
name: openrouter-toolkit
description: "The definitive OpenRouter skill — intelligent model routing by task type, cost tracking with budget alerts, automatic fallback chains, side-by-side model comparison, and savings recommendations. Use for optimizing AI model selection, controlling costs, and building resilient LLM pipelines."
homepage: https://www.agxntsix.ai
---

# 🔀 OpenRouter Toolkit

The definitive OpenRouter skill for OpenClaw agents. Intelligent model routing, cost tracking, fallback chains, and model comparison — all in one toolkit.

## Features

- **Smart Routing** — Automatically pick the best model for code, reasoning, creative, fast, or cheap tasks
- **Cost Tracking** — Log every API call with cost, track daily/weekly/monthly spend
- **Fallback Chains** — If primary model fails or times out, auto-retry with fallbacks
- **Model Comparison** — Send the same prompt to N models, compare quality and cost side-by-side
- **Budget Alerts** — Set spending limits and get warned before you blow your budget
- **Live Model Data** — Pulls real pricing and capabilities from OpenRouter's API

## Requirements

- `OPENROUTER_API_KEY` — Your OpenRouter API key
- Python 3.10+ with `requests` (included in most environments)

## Usage

### Smart Routing
```bash
python3 {baseDir}/scripts/openrouter_toolkit.py route --task code
python3 {baseDir}/scripts/openrouter_toolkit.py route --task reasoning
python3 {baseDir}/scripts/openrouter_toolkit.py route --task creative
python3 {baseDir}/scripts/openrouter_toolkit.py route --task fast
python3 {baseDir}/scripts/openrouter_toolkit.py route --task cheap
```

### Model Comparison
```bash
python3 {baseDir}/scripts/openrouter_toolkit.py compare --prompt "Explain recursion" --models "anthropic/claude-sonnet-4,openai/gpt-4o-mini"
```

### Fallback Chain
```bash
python3 {baseDir}/scripts/openrouter_toolkit.py fallback --prompt "Hello" --chain "anthropic/claude-opus-4,anthropic/claude-sonnet-4,openai/gpt-4o-mini"
```

### Cost Tracking
```bash
python3 {baseDir}/scripts/openrouter_toolkit.py cost --period daily
python3 {baseDir}/scripts/openrouter_toolkit.py cost --period weekly
python3 {baseDir}/scripts/openrouter_toolkit.py cost --period monthly
```

### Budget Alerts
```bash
python3 {baseDir}/scripts/openrouter_toolkit.py budget --set 50.00
python3 {baseDir}/scripts/openrouter_toolkit.py budget --check
```

### List Models
```bash
python3 {baseDir}/scripts/openrouter_toolkit.py models --top 20
python3 {baseDir}/scripts/openrouter_toolkit.py models --search claude
python3 {baseDir}/scripts/openrouter_toolkit.py models --best code
```

## How Smart Routing Works

The router scores models based on task type using these heuristics:

| Task | Prioritizes | Example Models |
|------|------------|----------------|
| code | High context, code benchmarks | Claude Opus, GPT-4o |
| reasoning | Thinking/reasoning capability | Claude Opus, o1 |
| creative | Creative writing quality | Claude Sonnet, GPT-4o |
| fast | Low latency, good enough quality | Claude Haiku, GPT-4o-mini |
| cheap | Lowest cost per token | Gemini Flash, GPT-4o-mini |

## Data Storage

Cost logs are stored in SQLite at `{baseDir}/data/openrouter_costs.db`.

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
