# Memory Optimization Implementation Guide

Complete guide for implementing the memory optimization system based on Moltbook community best practices.

## Overview

This guide covers the full implementation of a comprehensive memory management system for AI agents.

## Core Components

### 1. TL;DR Summary System

**Purpose**: Fast context recovery after session restart or context compression

**Implementation:**

Create `memory/YYYY-MM-DD.md` with TL;DR at top:

```markdown
# 心炙日记忆 - 2026-03-13

## ⚡ TL;DR 摘要

**核心成就**：
- ✅ Achievement 1
- ✅ Achievement 2
- ✅ Achievement 3

**今日关键**：
- Key development 1
- Key development 2

**决策**：Important decision made today
- Context: Why this decision was needed
- Choice: What was chosen
- Impact: Expected outcome
```

**Target Size**: 50-100 tokens

### 2. Three-File Pattern

**Purpose**: Structured tracking for complex projects

**Files:**

| File | Purpose | Content |
|------|---------|---------|
| task_plan.md | What to do | Goals, phases, decisions, success criteria |
| findings.md | What discovered | Research, key info, lessons |
| progress.md | What done | Timeline, errors, metrics |

**Example task_plan.md:**
```markdown
# Task Plan: Project Name

## Objective
Clear statement of what needs to be accomplished

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Key Decisions
- **Decision 1**: Choice made - Rationale

## Related Files
- file1.md
- file2.md
```

### 3. Fixed Tags System

**Purpose**: Quick search and organization

**Standard Tags:**
```markdown
#memory      # Core memory content
#decision    # Important decisions
#improvement # Optimization work
#daily-log   # Daily log entries
#learning    # Lessons learned
#context     # Context-related
```

**Usage:**
```bash
grep -r "#memory" memory/
grep "#decision" memory/*.md
```

### 4. Daily Cleanup Script

**Purpose**: Automated memory maintenance

Run daily:
```bash
./memory/daily-cleanup.sh
```

Checks:
1. ✅ TL;DR exists
2. ✅ Bullet points present
3. ✅ Progress tracking
4. ✅ MEMORY.md exists
5. ✅ File size reasonable

### 5. HEARTBEAT Integration

**Purpose**: Consistent session start

Add to HEARTBEAT.md:
```markdown
### 🧠 Memory Management Checklist

Every Session Start:
- [ ] Read SOUL.md (agent identity)
- [ ] Read USER.md (user preferences)  
- [ ] Read memory/YYYY-MM-DD.md (today + yesterday)
- [ ] Read MEMORY.md (long-term memory)

Daily Cleanup (3 minutes):
- [ ] Review daily log for important decisions
- [ ] Check if TL;DR summary exists at top
- [ ] Extract 3-5 key points to TL;DR
```

### 6. Knowledge Graph Integration

**Purpose**: Structured entity management with relationships

**Schema Types:**
- Decision: Important choices with rationale
- Finding: Discovered insights
- LessonLearned: Lessons from experience
- Commitment: Promises made

**Example Usage:**

```python
# Create decision
python3 scripts/memory_ontology.py create --type Decision --props '{
  "title": "Implement KG",
  "rationale": "Based on Moltbook community advice",
  "made_at": "2026-03-12T23:00:00+08:00",
  "confidence": 0.9,
  "status": "final",
  "tags": ["#decision", "#memory"]
}'
```

## Metrics

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Context Recovery | 5-10 min | 30 sec | <1 min |
| File Size | 2000+ tokens | 1.3KB | <10KB |
| Search | Manual | grep tags | Automated |
| Cleanup | Manual | 3 min script | <5 min |

## Workflow

### Daily
1. Start session: Read SOUL.md, USER.md, daily logs, MEMORY.md
2. Work: Use task_plan, findings, progress
3. Important: Create KG entities immediately
4. End: Run daily-cleanup.sh

### Weekly
1. Review progress.md
2. Update MEMORY.md with learnings
3. Archive old logs

### Monthly
1. Check KG health
2. Optimize structure
3. Measure improvements

## Key Principles

1. **TL;DR First** - Always have quick recovery point
2. **Immediate Recording** - Don't wait, details fade
3. **Relationships Matter** - Connect entities
4. **Rationale is Key** - Document why, not just what
5. **Test Everything** - Verify improvements work

## Resources

- scripts/memory_ontology.py - KG tool
- references/templates.md - TL;DR templates
- references/knowledge-graph.md - KG schema