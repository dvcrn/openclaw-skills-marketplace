# Patterns Reference

## Parallel Coordination

Use parallel dispatch when sub-tasks are **independent** — no shared files, no data dependencies.

**Keep concurrency at 2–3 agents max.** More often triggers rate limiting and increases total time.

### Pattern 1: Data Sharding

Split a large dataset; merge at the end.

```
1000 records → 3 agents × ~333 each

Agent A: records 1–333    → output/batch_a/
Agent B: records 334–666  → output/batch_b/
Agent C: records 667–1000 → output/batch_c/

→ Agent D: merge all batches → output/final/
```

### Pattern 2: Division of Labor

Different task types run simultaneously.

```
Agent A: backend logic  → src/api/
Agent B: frontend UI    → src/pages/
Agent C: test suite     → tests/

→ Orchestrator: integration check
```

### Pattern 3: Serial Pipeline

Use when stages depend on each other.

```
Stage 1 → validate ✅ → Stage 2 → validate ✅ → Stage 3
```

### Pattern 4: Hybrid

Pipeline with a parallel middle stage.

```
Stage 1: Prepare    (serial)    ✅
Stage 2: Process    (parallel)  ✅ ✅ ✅
Stage 3: Merge      (serial)    ✅
```

## Parallel Safety Rules

- Each agent writes to a **different** directory — never share output files
- Each agent maintains its **own** `progress.json`
- One failure doesn't stop others — orchestrator handles recovery
- Avoid > 3 concurrent agents

## Checkpoint / Resume

For batch tasks > 100 items, always implement resume logic:

```python
import json, os

PROGRESS_FILE = "output/progress.json"

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        return json.load(open(PROGRESS_FILE))
    return {"completed": [], "failed": []}

def save_progress(p):
    json.dump(p, open(PROGRESS_FILE, "w"), indent=2)

progress = load_progress()
for item in all_items:
    if item["id"] in progress["completed"]:
        continue
    try:
        process(item)
        progress["completed"].append(item["id"])
    except Exception as e:
        progress["failed"].append({"id": item["id"], "error": str(e)})
    save_progress(progress)
```

## Role Division

| Role | Does |
|------|------|
| Orchestrator | Plan, design, decide, validate, communicate |
| Coding agent | Implement, execute, debug, process |

**Rule:** Give agents a closed spec — exact formula, exact output format. Not open questions.

## Domain Examples

### Data Science

```
Stage 1: Write scoring script  (~3 min)
  In:  candidates.json + formula [from orchestrator]
  Out: scripts/score.py
  ✓:   runs on 5 test cases without errors

Stage 2: Run scoring  (~20 min, background)
  In:  candidates.json
  Out: scored.json  |  Resume: progress.json
  ✓:   N records, no null scores

Stage 3: Report  (~2 min)
  In:  scored.json
  Out: report.md, top50.csv
  ✓:   summary table present
```

### Web Development

```
Stage 1: Auth middleware + routes  (~10 min)
  Out: src/middleware/auth.js, src/routes/auth.js
  ✓:   no lint errors

Stage 2: Tests  (~5 min)
  Out: tests/auth.test.js
  ✓:   all tests pass

Stage 3: Docs  (~2 min)
  Out: README.md, API.md
  ✓:   endpoints documented
```

### Document Processing

```
Parallel (3 agents × ~67 files):
  Agent A: docs/batch_1/ → output/json/batch_1/
  Agent B: docs/batch_2/ → output/json/batch_2/
  Agent C: docs/batch_3/ → output/json/batch_3/

Merge:
  Agent D → output/all.json
  ✓: N records, required fields present
```

## Agent Differences

| Factor | Notes |
|--------|-------|
| PTY | Claude Code requires `pty:true`; others may not |
| Context passing | CLI arg vs stdin vs file — check your agent's docs |
| Completion signal | Exit code, output text, or file creation |
| Rate limits | Check provider limits before running parallel agents |

Keep agent-specific config in your dispatch tasks or project docs — not in this skill.
