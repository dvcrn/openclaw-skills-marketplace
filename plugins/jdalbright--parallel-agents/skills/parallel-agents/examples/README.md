# Parallel Agents Examples

## Simple Parallel Research Example

**File:** `simple_parallel_research.py`

Demonstrates the correct way to spawn multiple research agents in parallel.

### Usage

⚠️ **Must be run from within an OpenClaw agent session** (not as standalone script)

```python
# From within OpenClaw agent (like Scout)
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / '.openclaw/skills/parallel-agents/examples'))

import simple_parallel_research
simple_parallel_research.run_example()
```

### What It Does

1. Spawns 3 research agents simultaneously
2. Each agent researches a different topic (coffee shops, hiking trails, gay bars)
3. Waits 45 seconds for completion
4. Collects and displays results from all agents

### Key Concepts Demonstrated

- ✅ Parallel spawning using `sessions_spawn()`
- ✅ Proper task formatting for agents
- ✅ Result collection via `sessions_history()`
- ✅ Running from agent code context

## Why No Other Examples?

Previous versions included many example files that tried to run as standalone scripts. They all failed because the `tools` module is only available in OpenClaw agent runtime.

**The correct pattern is simple:**

```python
from tools import sessions_spawn

result = sessions_spawn(
    task="Your task here. Return JSON.",
    runTimeoutSeconds=90,
    cleanup="delete"
)
```

For production use with auto-retry, see `../helpers.py` and `../USAGE-GUIDE.md`.

## Common Mistake

❌ **Don't do this:**
```bash
python3 simple_parallel_research.py
# Error: ImportError: No module named 'tools'
```

✅ **Do this:**
```python
# Inside OpenClaw agent session
import simple_parallel_research
simple_parallel_research.run_example()
```

## Need More Examples?

See the complete [USAGE-GUIDE.md](../USAGE-GUIDE.md) for:
- Auto-retry patterns
- Multi-agent coordination
- Error handling
- Result collection
- Real-world use cases
