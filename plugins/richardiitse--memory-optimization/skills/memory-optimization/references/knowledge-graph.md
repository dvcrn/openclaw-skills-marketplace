# Knowledge Graph Schema and Usage Guide

Complete guide for using the Knowledge Graph component of the memory optimization system.

## Schema Overview

### Entity Types

| Type | Purpose | Required Fields | Optional Fields |
|------|---------|-----------------|-----------------|
| **Decision** | Important choices | title, rationale, made_at, confidence | context, alternatives, impact, status |
| **Finding** | Discovered insights | title, content, discovered_at, type, confidence | evidence, implications, source |
| **LessonLearned** | Learning from experience | title, lesson, learned_at, mistake_or_success, application | context, related_findings |
| **Commitment** | Promises made | description, source, created_at, committed_to | due_date, priority, status |
| **ContextSnapshot** | Session snapshots | title, captured_at, content_summary | compression_ratio, key_entities |

### Relations

| Relation | From | To | Purpose |
|----------|------|----|---------|
| led_to_decision | Finding | Decision | Finding leads to decision |
| decision_created | Decision | Commitment | Decision creates commitment |
| fulfilled_by | Commitment | Task | Commitment fulfilled by task |
| lesson_from | LessonLearned | Entity | Lesson derived from |
| depends_on | Task | Task | Task dependency |
| has_task | Project | Task | Project contains tasks |

## Usage

### Creating Entities

**Decision:**
```bash
python3 scripts/memory_ontology.py create --type Decision --props '{
  "title": "Use Knowledge Graph",
  "rationale": "Based on Moltbook community best practices for better query efficiency",
  "made_at": "2026-03-12T23:00:00+08:00",
  "context": "Need to improve memory management after context compression",
  "alternatives_considered": ["File search", "Vector DB", "SQL DB"],
  "choice": "Knowledge Graph",
  "impact": "high",
  "confidence": 0.9,
  "status": "final",
  "tags": ["#decision", "#memory", "#architecture"]
}'
```

**Finding:**
```bash
python3 scripts/memory_ontology.py create --type Finding --props '{
  "title": "Context compression causes slow recovery",
  "content": "Current context recovery after compression takes 3-5 minutes",
  "discovered_at": "2026-03-12T22:00:00+08:00",
  "type": "process",
  "evidence": "Measured 180-300 seconds to read 10+ files",
  "implications": "Need TL;DR, Knowledge Graph, and structured memory",
  "confidence": "confirmed",
  "tags": ["#finding", "#performance", "#memory"],
  "source": "Session performance analysis"
}'
```

**LessonLearned:**
```bash
python3 scripts/memory_ontology.py create --type LessonLearned --props '{
  "title": "Record decisions immediately",
  "lesson": "Important decisions should be recorded immediately after making them, not waiting until context compression or daily summary",
  "learned_at": "2026-03-12T23:30:00+08:00",
  "context": "From Moltbook community discussion",
  "mistake_or_success": "best_practice",
  "application": "Set up trigger mechanism: write to KG immediately after creating/updating Decision entity",
  "tags": ["#lesson", "#best_practice", "#decision_making"]
}'
```

### Creating Relationships

```bash
python3 scripts/memory_ontology.py relate --from find_xxx --rel led_to_decision --to dec_xxx
python3 scripts/memory_ontology.py relate --from dec_xxx --rel decision_created --to commit_xxx
```

### Querying

**By Type:**
```bash
python3 scripts/memory_ontology.py query --type Decision
```

**By Tags:**
```bash
python3 scripts/memory_ontology.py query --tags "#memory" "#decision"
```

**By Status:**
```bash
python3 scripts/memory_ontology.py query --type Commitment --status pending
```

**Verbose Output:**
```bash
python3 scripts/memory_ontology.py query --type Decision --verbose
```

### Getting Related Entities

```bash
python3 scripts/memory_ontology.py related --id dec_xxx
python3 scripts/memory_ontology.py related --id dec_xxx --verbose
```

### Validation

```bash
python3 scripts/memory_ontology.py validate
```

Checks:
- All entities have valid types
- All relations reference existing entities
- Schema constraints satisfied
- Temporal consistency

### Statistics

```bash
python3 scripts/memory_ontology.py stats
```

Shows:
- Total entities by type
- Total relations by type
- Graph health status
- Validation results

## Schema Files

- `memory-schema.yaml` - Complete schema definition
- `entity-templates.md` - Template for each entity type
- `graph.jsonl` - Actual graph data (JSON Lines format)

## Data Storage

**Format**: JSON Lines (one JSON object per line)
**Location**: `memory/ontology/graph.jsonl`

Each line is either:
- Entity: `{"type": "entity", "id": "xxx", "entity_type": "Decision", ...}`
- Relation: `{"type": "relation", "from": "xxx", "relation": "led_to_decision", "to": "xxx", ...}`

## Best Practices

1. **Record Immediately** - Don't wait for context compression
2. **Include Rationale** - Document "why" not just "what"
3. **Use Confidence** - Mark confidence level (0-1 or confirmed/partial/speculative)
4. **Establish Relations** - Don't leave entities isolated
5. **Use Tags** - Makes searching easier
6. **Validate Regularly** - Run validation to catch errors

## Integration with MEMORY.md

Add KG index to MEMORY.md:

```markdown
## 🧠 Knowledge Graph Index

### Recent Decisions
| ID | Title | Date | Status |
|----|-------|------|--------|
| dec_xxx | Decision Title | YYYY-MM-DD | final |

### Pending Commitments
| ID | Description | Due Date |
|----|-------------|----------|
| commit_xxx | Description | YYYY-MM-DD |
```

## Integration with Daily Logs

Add to daily log:

```markdown
## 📊 Knowledge Graph Updates

### Entities Created
- **dec_xxx**: Decision - Title
- **find_xxx**: Finding - Title

### Relationships Added
- find_xxx → led_to_decision → dec_xxx
```