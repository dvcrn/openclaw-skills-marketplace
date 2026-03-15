# Cognition — Protocol Blocks for AGENTS.md

Copy-paste these into your AGENTS.md.

---

## Memory Protocol

```markdown
## Memory Protocol
- Before answering questions about past work: search memory first
- Before starting any new task: check memory/today's date for active context
- When you learn something important: write it to the appropriate file immediately
- When corrected on a mistake: add the correction as a rule to MEMORY.md
- When a session is ending or context is large: summarize to memory/YYYY-MM-DD.md

### Importance Tagging
Tag significant moments in daily logs for consolidation priority:
- `[REPLAY_PRIORITY: HIGH]` — Corrections, policy changes, new procedures, explicit decisions
- `[REPLAY_PRIORITY: MEDIUM]` — New facts, project milestones, config changes
- `[REPLAY_PRIORITY: LOW]` — Routine operations (default — no tag needed)

### GWT Broadcasting
When important information enters the session, broadcast to all relevant stores:
- New user preference → semantic memory (bank file) + MEMORY.md index
- Novel problem solution → `memory/procedures/` (compile the skill)
- Future commitment → `memory/FUTURE_INTENTS.md`
- Correction → fix the wrong entry + add rule if systemic
- Knowledge gap discovered → note in KNOWLEDGE_MAP.md
```

---

## Retrieval Protocol

```markdown
## Retrieval Protocol
Before doing non-trivial work:
1. `memory_search` for the project/topic/user preference
2. Follow cross-references from `memory/bank/cross-references.md` to load related context
3. `memory_get` the referenced file chunk if needed
4. If search returns zero useful results: note the gap in `memory/meta/gap_tracker.json`
5. Then proceed with the task
```
