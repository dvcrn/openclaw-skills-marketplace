---
name: deep-search
description: "Three-tier AI search routing — quick facts (sonar), research comparisons (sonar-pro), and deep analysis (sonar-reasoning-pro). Auto-selects model tier based on query complexity. Focus modes: internet, academic, news, youtube, reddit. Use for research, fact-checking, competitive analysis, or any web search task."
homepage: https://www.agxntsix.ai
---

# Deep Search 🔍

Multi-tier Perplexity-powered search with automatic Langfuse observability tracing.

## When to Use

- Quick facts and simple lookups → `quick` tier
- Standard research, comparisons, how-to → `pro` tier
- Deep analysis, market research, complex questions → `deep` tier
- Academic paper search, news monitoring, Reddit/YouTube research

## Usage

```bash
# Quick search (sonar, ~2s)
python3 {baseDir}/scripts/deep_search.py quick "what is OpenClaw"

# Pro search (sonar-pro, ~5-8s)
python3 {baseDir}/scripts/deep_search.py pro "compare Claude vs GPT-4o for coding"

# Deep research (sonar-reasoning-pro, ~10-20s)
python3 {baseDir}/scripts/deep_search.py deep "full market analysis of AI agent frameworks"

# Focus modes
python3 {baseDir}/scripts/deep_search.py pro "query" --focus academic
python3 {baseDir}/scripts/deep_search.py pro "query" --focus news
python3 {baseDir}/scripts/deep_search.py pro "query" --focus youtube
python3 {baseDir}/scripts/deep_search.py pro "query" --focus reddit
```

## Tiers

| Tier | Model | Speed | Best For |
|------|-------|-------|----------|
| quick | sonar | ~2s | Simple facts, quick lookups |
| pro | sonar-pro | ~5-8s | Research, comparisons |
| deep | sonar-reasoning-pro | ~10-20s | Deep analysis, complex questions |

## Environment

- `PERPLEXITY_API_KEY` — Required. Perplexity API key.
- `OPENROUTER_API_KEY` — Optional. For Langfuse tracing model pricing.

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
