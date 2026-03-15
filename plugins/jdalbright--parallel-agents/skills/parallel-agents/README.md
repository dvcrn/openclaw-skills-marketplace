# Parallel Agents - Real AI Parallel Execution for OpenClaw

🚀 **Execute tasks with ACTUAL AI-powered parallel agents using OpenClaw's sessions_spawn.**

> ✅ **STATUS**: Production-ready with auto-retry (tested 2026-02-08)

## What Is This?

A skill that enables **true parallel AI agent execution** within OpenClaw. Spawn multiple AI agents simultaneously, each running as an independent AI session with full capabilities.

**Not simulation.** Each agent is a real spawned AI session that thinks, reasons, and generates output independently.

## Quick Start

### From Within an OpenClaw Agent Session

```python
from tools import sessions_spawn

# Spawn 3 research agents in parallel
agent1 = sessions_spawn(
    task="Research gay-friendly bars in Savannah. Return JSON.",
    runTimeoutSeconds=90,
    cleanup="delete"
)

agent2 = sessions_spawn(
    task="Research best restaurants in Savannah. Return JSON.",
    runTimeoutSeconds=90,
    cleanup="delete"
)

agent3 = sessions_spawn(
    task="Research top photo spots in Savannah. Return JSON.",
    runTimeoutSeconds=90,
    cleanup="delete"
)

# All 3 now running in parallel!
```

### With Smart Model Hierarchy (Recommended)

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / '.openclaw/skills/parallel-agents'))
from helpers import spawn_with_retry

# Automatically tries: Haiku → Kimi → Opus
# Starts with cheapest/fastest, escalates if needed
result = spawn_with_retry(
    task="Research gay bars in Savannah. Return JSON.",
    use_hierarchy=True  # default
)

# Model used is returned in result
print(f"Completed with: {result.get('model_used', 'default')}")
```

### Model Hierarchy Explained

**Cost-Optimized Escalation:**
1. **Haiku** (fastest, ~15% cost) - Tries first
2. **Kimi** (default, 100% cost) - Fallback if Haiku fails  
3. **Opus** (powerful, ~1500% cost) - Last resort

**Why This Matters:**
- Most simple tasks succeed with Haiku (big savings!)
- Complex tasks automatically escalate to better models
- You only pay for the power you need

## Key Features

- ✅ **True parallelism** - Multiple AI agents running simultaneously
- ✅ **Smart model hierarchy** - Haiku → Kimi → Opus (cost optimization)
- ✅ **Auto-retry** - Agents automatically escalate to better models on failure
- ✅ **20+ agent types** - Content writers, developers, reviewers, meta-agents
- ✅ **Production-ready** - Error handling, timeouts, cleanup
- ✅ **Full AI capabilities** - Each agent has same tools/access as host

## Documentation

| File | Purpose |
|------|---------|
| **[SKILL.md](SKILL.md)** | Complete skill documentation |
| **[USAGE-GUIDE.md](USAGE-GUIDE.md)** | Practical examples and patterns |
| **[helpers.py](helpers.py)** | Auto-retry helper functions |
| **[ai_orchestrator.py](ai_orchestrator.py)** | Core orchestrator code |

## Use Cases

| Scenario | Pattern |
|----------|---------|
| **Multi-topic research** | Spawn N agents with different topics |
| **Code review team** | Quality, security, performance agents |
| **Content variations** | Different styles/tones for same content |
| **Parallel data gathering** | Independent API calls or searches |

## Requirements

- Must run **inside an OpenClaw agent session** (tools module required)
- OpenClaw gateway must be running
- Cannot be run as standalone script (subprocess lacks tools access)

## Available Agent Types (20+)

### Content Writers (5)
- `content_writer_creative` - Imaginative, artistic
- `content_writer_funny` - Humorous, witty
- `content_writer_educational` - Teaching content
- `content_writer_trendy` - Viral, trend-focused
- `content_writer_controversial` - Thought-provoking

### Development (5)
- `frontend_developer` - React/Vue/Angular
- `backend_developer` - FastAPI/Flask/Django
- `database_architect` - Schema design
- `api_designer` - REST/GraphQL specs
- `devops_engineer` - CI/CD pipelines

### QA & Review (5)
- `code_reviewer` - Code quality
- `security_reviewer` - Vulnerability scanning
- `performance_reviewer` - Optimization
- `accessibility_reviewer` - WCAG compliance
- `test_engineer` - Test coverage

### Documentation (1)
- `documentation_writer` - Technical docs

### Meta-Agents (4)
- `agent_creator` - Designs new AI agents
- `agent_design_reviewer` - Validates designs
- `agent_refiner` - Improves agent designs
- `agent_orchestrator` - Coordinates workflows

## Example: Multi-Topic Research

```python
from helpers import spawn_parallel_with_retry

tasks = [
    "Research top attractions in Savannah, GA",
    "Research gay-friendly venues in Savannah",
    "Research best restaurants for birthday dinner"
]

results = spawn_parallel_with_retry(tasks, max_retries=2)
# Spawns all 3, waits, auto-retries failures
```

## Why Auto-Retry Matters

**Real example (2026-02-08):**
- Spawned 3 research agents
- Agent 1 (bars): ✅ Success
- Agent 2 (restaurants): ❌ Failed (no output)
- Agent 3 (photos): ✅ Success

**Without retry:** 33% failure rate, incomplete results  
**With retry:** Auto-fixes failures → 100% success

## Installation

This skill is included with OpenClaw. No additional installation required.

## Contributing

Found a bug? Have an idea? Open an issue or submit a PR!

## License

Part of the OpenClaw skill ecosystem.

---

**Built with real AI sessions, not simulation. 🚀**
