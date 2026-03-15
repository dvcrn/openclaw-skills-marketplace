# Parallel Agents - Correct Usage Guide

**Last Updated:** 2026-02-08  
**Status:** ✅ TESTED AND WORKING

---

## 🎯 TL;DR

**DO THIS** ✅
```python
# From within your OpenClaw agent session
from tools import sessions_spawn

agent1 = sessions_spawn(task="...", runTimeoutSeconds=90, cleanup="delete")
agent2 = sessions_spawn(task="...", runTimeoutSeconds=90, cleanup="delete")
agent3 = sessions_spawn(task="...", runTimeoutSeconds=90, cleanup="delete")

# All 3 running in parallel!
```

**NOT THIS** ❌
```bash
# Won't work - tools module unavailable in subprocess
python3 ai_orchestrator.py
```

---

## Why The Orchestrator Fails as Standalone Script

The `ai_orchestrator.py` code tries to:
```python
from tools import sessions_spawn  # ❌ Only available in agent runtime!
```

This works when you're an OpenClaw agent (like Scout), but fails when run as:
- Subprocess via `exec`
- Standalone script via `python3`
- Any context outside OpenClaw agent runtime

**The `tools` module is injected by OpenClaw into agent sessions**, not available globally.

---

## ✅ Proven Working Pattern (Tested 2026-02-08)

### Scenario
Jake needed research on 3 different aspects of his Savannah trip.

### Implementation
```python
# Called from Scout's main session (has tools access)
from tools import sessions_spawn

# Research agent 1: Gay-friendly bars
result1 = sessions_spawn(
    task="""You are an educational content writer. Research and provide: 
Top 3 gay-friendly bars in Savannah, GA. Include names, addresses, 
and brief descriptions. Return as JSON:
{
  "bars": [
    {"name": "Bar Name", "address": "Address", "description": "Brief description"}
  ]
}""",
    runTimeoutSeconds=90,
    cleanup="delete"
)

# Research agent 2: Birthday dinner restaurants  
result2 = sessions_spawn(
    task="""You are an educational content writer. Research and provide:
Best 3 restaurants in Savannah for a birthday dinner. Include names,
addresses, price range, and why they're special. Return as JSON:
{
  "restaurants": [
    {"name": "Name", "address": "Address", "price": "$$", "why_special": "Reason"}
  ]
}""",
    runTimeoutSeconds=90,
    cleanup="delete"
)

# Research agent 3: Photo spots
result3 = sessions_spawn(
    task="""You are an educational content writer. Research and provide:
Top 3 photography spots in Savannah, GA. Include location names,
what makes them photogenic, and best time of day. Return as JSON:
{
  "spots": [
    {"name": "Location", "why_photogenic": "Reason", "best_time": "Time of day"}
  ]
}""",
    runTimeoutSeconds=90,
    cleanup="delete"
)

# All 3 agents now running in parallel!
print(f"Spawned 3 agents:")
print(f"  Agent 1: {result1['childSessionKey']}")
print(f"  Agent 2: {result2['childSessionKey']}")
print(f"  Agent 3: {result3['childSessionKey']}")
```

### Results
- ✅ All 3 agents spawned successfully
- ✅ Ran simultaneously (true parallelism)
- ✅ Each visible in `sessions_list()`
- ✅ Sessions isolated and independent

---

## Collecting Results

After spawning agents, check their status and outputs:

```python
from tools import sessions_list, sessions_history

# Check which agents are still running
sessions = sessions_list(limit=20)

for session in sessions['sessions']:
    if 'subagent' in session['key']:
        print(f"Agent: {session['key']}")
        print(f"  Status: {'Running' if session['totalTokens'] == 0 else 'Complete'}")
        print(f"  Tokens: {session['totalTokens']}")

# Get output from completed agent
history = sessions_history(sessionKey="agent:main:subagent:...")
final_message = history['messages'][-1]  # Last assistant message
output = final_message['content']  # JSON response
```

---

## Helper Function Pattern

You can create a helper function to make this cleaner:

```python
def spawn_research_agents(topics):
    """Spawn multiple research agents in parallel."""
    from tools import sessions_spawn
    
    agents = []
    for topic in topics:
        result = sessions_spawn(
            task=f"Research and summarize: {topic}. Return as JSON.",
            runTimeoutSeconds=90,
            cleanup="delete"
        )
        agents.append({
            'topic': topic,
            'session_key': result['childSessionKey'],
            'run_id': result['runId']
        })
    
    return agents

# Usage
agents = spawn_research_agents([
    "Gay-friendly bars in Savannah",
    "Best birthday dinner spots in Savannah",
    "Top photo locations in Savannah"
])

print(f"✅ Spawned {len(agents)} parallel research agents")
```

---

## The Orchestrator's Role

The `ai_orchestrator.py` code is still useful for:
- **Reference implementation** - Shows agent patterns and structures
- **Agent registry** - AGENT_PROMPTS dict with system prompts
- **Data structures** - AgentTask and AgentResult models
- **Convenience functions** - create_content_team(), create_dev_team(), etc.

But you must **call it from within agent code**, not run it standalone.

### Future Enhancement Ideas

1. **Agent-friendly wrapper functions** that work in agent context:
   ```python
   # Import into agent context
   from parallel_agents.helpers import parallel_spawn
   
   results = parallel_spawn([
       {'type': 'research', 'topic': 'bars'},
       {'type': 'research', 'topic': 'restaurants'},
       {'type': 'research', 'topic': 'photos'},
   ])
   ```

2. **Result polling helpers**:
   ```python
   from parallel_agents.helpers import poll_until_complete
   
   outputs = poll_until_complete(agent_session_keys, timeout=120)
   ```

3. **Structured agent builders**:
   ```python
   from parallel_agents.builders import ResearchTeam
   
   team = ResearchTeam(['topic1', 'topic2', 'topic3'])
   results = team.execute()  # Spawns + polls automatically
   ```

---

## Key Takeaways

1. ✅ **Parallel spawning works perfectly** from agent sessions
2. ❌ **Cannot run orchestrator as standalone script** (tools unavailable)
3. 💡 **Use direct sessions_spawn calls** for now
4. 📚 **Reference orchestrator code** for patterns and prompts
5. 🚀 **Future: Add helper functions** that work in agent context

---

## Example Use Cases

### 1. Multi-Topic Research
```python
topics = ["Topic A", "Topic B", "Topic C"]
agents = [
    sessions_spawn(task=f"Research: {topic}", runTimeoutSeconds=90, cleanup="delete")
    for topic in topics
]
```

### 2. Code Review Team
```python
code = open('app.py').read()

reviews = [
    sessions_spawn(task=f"Review for quality: {code}", runTimeoutSeconds=120, cleanup="delete"),
    sessions_spawn(task=f"Review for security: {code}", runTimeoutSeconds=120, cleanup="delete"),
    sessions_spawn(task=f"Review for performance: {code}", runTimeoutSeconds=120, cleanup="delete"),
]
```

### 3. Content Variations
```python
topic = "Monday motivation"
styles = ['funny', 'inspirational', 'educational']

content = [
    sessions_spawn(
        task=f"Write {style} post about {topic}",
        runTimeoutSeconds=60,
        cleanup="delete"
    )
    for style in styles
]
```

---

*This skill is actively being improved. Honest feedback welcome!*

---

## 🔄 Auto-Restart Pattern (Recommended)

Agents can fail for various reasons (timeout, network issues, errors). Use auto-retry for reliability:

### Using Helper Functions (Easiest)

```python
import sys
sys.path.insert(0, str(Path.home() / '.openclaw/skills/parallel-agents'))
from helpers import spawn_with_retry, spawn_parallel_with_retry

# Single agent with auto-retry
result = spawn_with_retry(
    task="Research gay bars in Savannah. Return JSON.",
    max_retries=2,
    timeout_seconds=90
)

# Multiple agents with auto-retry
tasks = [
    "Research bars in Savannah",
    "Research restaurants in Savannah",
    "Research photo spots in Savannah"
]
results = spawn_parallel_with_retry(tasks, max_retries=2)

# Spawns all 3, waits, checks results, auto-retries any failures!
```

### Manual Retry Pattern

```python
from tools import sessions_spawn, sessions_list, sessions_history
import time

def spawn_with_retry(task, max_retries=2):
    """Spawn agent with automatic retry on failure."""
    for attempt in range(max_retries + 1):
        result = sessions_spawn(
            task=task,
            runTimeoutSeconds=90,
            cleanup="delete"
        )
        
        session_key = result['childSessionKey']
        
        # Wait for completion
        time.sleep(30)
        
        # Check status
        sessions = sessions_list(limit=20)
        session = next((s for s in sessions['sessions'] if s['key'] == session_key), None)
        
        if session and session.get('totalTokens', 0) > 0:
            # Verify it actually has output
            history = sessions_history(sessionKey=session_key)
            if history.get('messages'):
                return result  # Success!
        
        if attempt < max_retries:
            print(f"⚠️ Agent failed, retrying ({attempt + 1}/{max_retries})...")
    
    raise Exception(f"Agent failed after {max_retries} retries")

# Usage
try:
    result = spawn_with_retry("Research task here")
    print(f"✅ Agent succeeded: {result['childSessionKey']}")
except Exception as e:
    print(f"❌ Agent failed permanently: {e}")
```

### Why Auto-Retry Matters

**Real Example (2026-02-08):**
- Spawned 3 research agents
- Agent 1 (bars): ✅ Succeeded
- Agent 2 (restaurants): ❌ Failed (no output)
- Agent 3 (photos): ✅ Succeeded

**Without retry:** 33% failure rate, incomplete results
**With retry:** Auto-retry agent 2 → 100% success

### Best Practices

1. **Always use retry** for production tasks
2. **Set reasonable timeouts** (60-120s depending on complexity)
3. **Log failures** to diagnose patterns
4. **Use helpers module** for cleaner code
5. **Monitor with sessions_list()** to catch issues early

---

## 📦 Helper Functions Reference

The `helpers.py` module provides production-ready functions:

| Function | Purpose |
|----------|---------|
| `spawn_with_retry()` | Spawn single agent with auto-retry |
| `spawn_parallel_with_retry()` | Spawn multiple agents, retry failures |
| `collect_agent_results()` | Gather outputs from session keys |

**Import pattern:**
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / '.openclaw/skills/parallel-agents'))
from helpers import spawn_with_retry, spawn_parallel_with_retry, collect_agent_results
```

---

*Updated 2026-02-08: Added auto-restart patterns and helpers module*

---

## 🎯 Model Hierarchy (Cost Optimization)

**NEW:** Agents now use smart model escalation to minimize costs while maintaining reliability.

### Default Hierarchy

```
1. Haiku (anthropic/claude-haiku-4-5)
   ├─ Cost: ~15% of Kimi
   ├─ Speed: 3x faster
   └─ Try first for simple tasks

2. Kimi (kimi-coding/k2p5)  
   ├─ Cost: Baseline
   ├─ Speed: Standard
   └─ Fallback if Haiku fails

3. Opus (anthropic/claude-opus-4-5)
   ├─ Cost: ~15x Kimi
   ├─ Power: Maximum reasoning
   └─ Last resort for complex tasks
```

### How It Works

```python
from helpers import spawn_with_retry

# Automatic hierarchy (recommended)
result = spawn_with_retry(
    task="Research restaurants in Savannah",
    use_hierarchy=True  # default
)

# Workflow:
# 1. Tries Haiku first
# 2. If Haiku produces no output → tries Kimi
# 3. If Kimi fails → tries Opus
# 4. Returns first successful result

print(f"Task completed with: {result['model_used']}")
# Output: "Task completed with: anthropic/claude-haiku-4-5"
```

### Cost Savings Example

**3 Research Tasks Without Hierarchy:**
- All use Kimi (default): 3 × $0.10 = **$0.30**

**3 Research Tasks With Hierarchy:**
- 2 succeed with Haiku: 2 × $0.015 = $0.03
- 1 falls back to Kimi: 1 × $0.10 = $0.10
- **Total: $0.13** (57% savings!)

### When to Override

**Use specific model when:**
```python
# Need maximum reasoning (skip hierarchy)
result = spawn_with_retry(
    task="Design complex distributed system architecture",
    model="anthropic/claude-opus-4-5",
    use_hierarchy=False
)

# Want consistent model for testing
result = spawn_with_retry(
    task="Test task",
    model="kimi-coding/k2p5",
    use_hierarchy=False
)
```

### Parallel with Hierarchy

```python
from helpers import spawn_parallel_with_retry

tasks = [
    "Research bars in Savannah",
    "Research restaurants",  
    "Research photo spots"
]

# All start with Haiku, auto-escalate if needed
results = spawn_parallel_with_retry(tasks, use_hierarchy=True)

# Check what models were used
for r in results:
    if r.get('success'):
        model = r['model_used'].split('/')[-1]
        print(f"Used {model}")

# Output might be:
# Used claude-haiku-4-5
# Used k2p5 (escalated from Haiku)
# Used claude-haiku-4-5
```

### Best Practices

1. **Use hierarchy by default** - Let the system optimize costs
2. **Monitor model usage** - Check results to see escalation patterns
3. **Override for specialized tasks** - Use Opus directly for complex reasoning
4. **Test with Haiku first** - Most tasks succeed with the cheapest model

### Model Selection Guidelines

| Task Type | Expected Model | Reasoning |
|-----------|---------------|-----------|
| Simple research | Haiku | Fast data gathering |
| List generation | Haiku | Structured output |
| Basic summaries | Haiku | Quick synthesis |
| Creative writing | Kimi | Better style/tone |
| Code generation | Kimi | Better complexity handling |
| Architecture design | Opus | Deep reasoning required |
| Math proofs | Opus | Maximum capabilities |
| Edge case debugging | Opus | Complex problem solving |

---

*Updated 2026-02-08: Added model hierarchy for cost optimization*
