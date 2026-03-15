---
name: research-logger
description: "AI research pipeline with automatic logging. Search via Perplexity, auto-save results to SQLite with topic and project metadata, full Langfuse tracing. Never lose a research session again. Use when conducting research, competitive analysis, or building a knowledge base."
homepage: https://www.agxntsix.ai
---

# Research Logger 📝🔬

Search + auto-save pipeline. Every research query is logged to SQLite with Langfuse tracing.

## When to Use

- Research that you want to save and recall later
- Building a knowledge base from repeated searches
- Reviewing past research on a topic
- Creating an audit trail of research decisions

## Usage

```bash
# Search and auto-log
python3 {baseDir}/scripts/research_logger.py log quick "what is RAG"
python3 {baseDir}/scripts/research_logger.py log pro "compare vector databases" --topic "databases"

# Search past research
python3 {baseDir}/scripts/research_logger.py search "vector databases"

# View recent entries
python3 {baseDir}/scripts/research_logger.py recent --limit 5
```

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
