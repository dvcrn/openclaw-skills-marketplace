# Agent Guide - FIS 3.2.0-lite

> **For OpenClaw Agents using FIS Architecture**

---

## What You Get

FIS 3.2 provides **workflow management** for multi-agent collaboration:

- **Ticket System**: JSON-based task tracking
- **Badge Generator**: Visual identity for subagents
- **QMD Integration**: Semantic search for knowledge

---

## Decision Tree: When to Use SubAgent?

```
User Request
    ↓
┌─────────────────────────────────────┐
│ 1. Needs multiple specialist roles? │
│ 2. Duration > 10 minutes?           │
│ 3. High failure impact?             │
│ 4. Batch processing needed?         │
└─────────────────────────────────────┘
    ↓ Any YES                  ↓ All NO
Use SubAgent               Direct handling
```

---

## Quick Scenarios

| Scenario | Action | Reason |
|----------|--------|--------|
| "Check weather" | ❌ Direct | Quick lookup |
| "Explain bubble sort" | ❌ Direct | Simple explanation |
| "Summarize this file" | ❌ Direct | Single task |
| "Implement + verify algorithm" | ✅ SubAgent | Worker + Reviewer |
| "Design UI components" | ✅ SubAgent | Specialized work |
| "Process 1000 files" | ✅ SubAgent | Batch + parallel |
| "Research + implement" | ✅ SubAgent | Multi-phase |

---

## Creating a SubAgent

### 1. Create Ticket

```bash
cat > ~/.openclaw/fis-hub/tickets/active/TASK_001.json << 'EOF'
{
  "ticket_id": "TASK_001",
  "agent_id": "worker-001",
  "parent": "cybermao",
  "role": "worker",
  "task": "Implement PTVF filter",
  "status": "active",
  "created_at": "2026-02-19T21:00:00",
  "timeout_minutes": 60
}
EOF
```

### 2. Generate Badge (Optional)

```bash
cd ~/.openclaw/workspace/skills/fis-architecture/lib
python3 badge_generator_v7.py
# Follow interactive prompts
```

### 3. Complete and Archive

```bash
# When task is done
mv ~/.openclaw/fis-hub/tickets/active/TASK_001.json \
   ~/.openclaw/fis-hub/tickets/completed/
```

---

## Workflow Patterns

### Pattern 1: Worker → Reviewer

```python
# Pseudo-code workflow
1. Create worker ticket
2. Wait for completion
3. Create reviewer ticket
4. Reviewer checks output
5. Archive both tickets
```

### Pattern 2: Research → Execute

```
Researcher investigates options
         ↓
   Delivers findings
         ↓
Worker implements chosen approach
         ↓
   Delivers code
```

### Pattern 3: Parallel Sharding

```
Task split into 4 chunks
         ↓
Worker-1 → Worker-2 → Worker-3 → Worker-4
         ↓
   All complete
         ↓
Aggregator combines results
```

---

## Anti-Patterns: Don't Do This!

### ❌ Over-decomposition
```python
# Bad: Creating agents for trivial tasks
planner = create_agent("plan")
worker = create_agent("implement")
reviewer = create_agent("review")
# User just wanted to convert a file!
```

### ❌ No Cleanup
```python
# Bad: Leaving tickets in active/ forever
# Always archive completed tasks
```

### ❌ Wrong Role
```python
# Bad: Using researcher for implementation
# Match role to actual need
```

---

## Best Practices

### ✅ Check Before Creating
- [ ] Is this too complex for direct handling?
- [ ] Do I have a clear completion criteria?
- [ ] Can I archive this when done?

### ✅ Use Correct Role
- **worker**: Implementation, execution
- **reviewer**: Quality assurance
- **researcher**: Investigation, analysis
- **formatter**: Conversion, cleanup

### ✅ Keep Tickets Tidy
- Archive completed tasks promptly
- Use descriptive ticket IDs
- Include timeout estimates

---

## Knowledge Management (QMD)

**Don't use custom registries — use QMD:**

```bash
# Search for existing knowledge
mcporter call 'exa.web_search_exa(query: "GPR VMD decomposition", numResults: 5)'

# Find relevant skills
mcporter call 'exa.web_search_exa(query: "SKILL.md image generation", numResults: 5)'
```

**Add knowledge**: Drop Markdown files into `knowledge/` directories.

---

## Remember

> **FIS is for workflow, not content.**  
> Use Tickets for process, QMD for knowledge.  
> Simple tasks = direct handling.  > Complex workflows = SubAgents.

*FIS 3.2.0-lite — Minimal workflow, maximal clarity 🐱⚡*
