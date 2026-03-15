---
name: langfuse-observability
description: "Langfuse Observability"
---

# 📡 Langfuse Observability

Complete Langfuse v3 observability toolkit for OpenClaw agents — automatic tracing for LLM calls, API calls, tool executions, and custom events. Cost tracking per model, session grouping, evaluation scoring, dashboard queries, and health monitoring. The central nervous system for agent observability.

**Use for:** logging, tracing, debugging, cost analysis, and audit trails.

## Quick Start

```python
import sys, os
sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace/skills/langfuse-observability/scripts"))
from langfuse_hub import traced, trace_llm, trace_api, trace_tool, trace_event, flush
```

## Scripts

| Script | Purpose |
|--------|---------|
| `langfuse_hub.py` | Universal import — tracing functions, decorators, context managers |
| `langfuse_admin.py` | CLI for dashboard queries (traces, costs, sessions, health) |
| `langfuse_cron.py` | Daily observability report for Telegram |

## Instance

- **Host:** http://langfuse-web:3000
- **Dashboard:** http://langfuse-web:3000 (internal)
- **SDK:** Langfuse Python v3.14.1

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need observability for your AI agents?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
