# Memory Optimization Templates

Ready-to-use templates for the memory optimization system.

## TL;DR Summary Template

```markdown
## ⚡ TL;DR 摘要

**核心成就**：
- ✅ Achievement 1 (result)
- ✅ Achievement 2 (result)
- ✅ Achievement 3 (result)

**今日关键**：
- Development 1: What happened
- Development 2: What was discovered

**决策**：Decision made
- Context: Why this was needed
- Choice: What was chosen
- Impact: Expected result

**下一步**：Immediate next steps
```

### English Version

```markdown
## ⚡ TL;DR Summary

**Core Achievements**:
- ✅ Achievement 1 (result)
- ✅ Achievement 2 (result)

**Key Developments**:
- Development 1: What happened

**Decisions Made**:
- Decision 1: Choice - Impact

**Next Steps**:
- Immediate action 1
- Immediate action 2
```

## Three-File Pattern Templates

### task_plan.md

```markdown
# Task Plan: [Project Name]

## Objective
Clear statement of what needs to be accomplished

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Key Decisions Made
### Decision 1
- **Context**: Why this decision was needed
- **Options**: A, B, C
- **Choice**: Option B
- **Rationale**: Why B was chosen
- **Impact**: Expected outcome

## Planned Tasks
- [ ] Task 1
- [ ] Task 2

## Related Files
- file1.md
- file2.md
```

### findings.md

```markdown
# Research Findings: [Topic]

## Research Questions
1. Question 1
2. Question 2

## Key Findings

### Finding 1
**Content**: What was discovered
**Source**: Where it came from
**Evidence**: Supporting data
**Implications**: What it means

### Finding 2
**Content**: What was discovered
**Source**: Where it came from
**Confidence**: high/medium/low

## Open Questions
- Question 1
- Question 2

## Next Steps
- [ ] Verify finding 1
- [ ] Apply finding 2
```

### progress.md

```markdown
# Progress: [Project Name]

## Overall Status
- **Completion**: X%
- **Health**: green/yellow/red

## Completed Tasks
- [x] Task 1 (Date, result)
- [x] Task 2 (Date, result)

## In Progress
- [ ] Task 3 (Progress %, Blocker)

## Blocked/Triaged
- [ ] Task 4 (Blocker, Next step)

## Timeline
| Date | Event |
|------|-------|
| YYYY-MM-DD | Started |
| YYYY-MM-DD | Milestone 1 |

## Metrics
- **Time Spent**: X hours
- **Tokens Used**: X
- **Tasks Completed**: X/Y
```

## Rolling Summary Template

```markdown
# Rolling Summary - [Date]

## TL;DR
- Focus: What was the main task
- Win: Biggest achievement
- Decision: Key decision made

## Key Decisions (Today)
| ID | Decision | Rationale | Impact |
|----|----------|-----------|--------|
| D1 | Choice A | Because X | High |

## Key Learnings (Today)
| ID | Learning | Application |
|----|----------|-------------|
| L1 | Insight 1 | Use in X |
| L2 | Insight 2 | Apply to Y |

## Progress (Today)
- Completed: X tasks
- In Progress: Y tasks
- Blocked: Z tasks

## Tomorrow
- Priority 1
- Priority 2

## Notes
- Note 1
- Note 2
```

## Daily Log Template

```markdown
# 心炙日记忆 - YYYY-MM-DD

## ⚡ TL;DR 摘要
[TL;DR content - see template above]

---

## 📅 今日工作日志

### Time Block 1
**Activity**: What was done
**Result**: Outcome
**Learnings**: Insights

### Time Block 2
[Same format]

---

## 🎯 今日任务总结

### ✅ 已完成
- [x] Task 1
- [x] Task 2

### ⏳ 进行中
- [ ] Task 3

### 📝 后续计划
- [ ] Task 4

---

## 💡 今日学习

1. Learning 1
2. Learning 2

---

## 📊 统计

| 指标 | 数值 |
|------|------|
| 完成任务 | X |
| 耗时 | X小时 |
| Token消耗 | X |
```

## Knowledge Graph Entity Templates

### Decision Template

```json
{
  "title": "Decision title",
  "rationale": "Why this decision was made",
  "made_at": "YYYY-MM-DDTHH:MM:SS+08:00",
  "context": "Background situation",
  "alternatives_considered": ["Option A", "Option B"],
  "choice": "Option chosen",
  "impact": "high/medium/low",
  "confidence": 0.9,
  "status": "final/draft/review",
  "tags": ["#decision", "#memory"],
  "memory_ref": "memory/YYYY-MM-DD.md"
}
```

### Finding Template

```json
{
  "title": "Finding title",
  "content": "What was discovered",
  "discovered_at": "YYYY-MM-DDTHH:MM:SS+08:00",
  "type": "process/technical/insight",
  "evidence": "Supporting evidence or data",
  "implications": "What this means",
  "confidence": "confirmed/partial/speculative",
  "tags": ["#finding", "#research"],
  "source": "Where it came from"
}
```

### LessonLearned Template

```json
{
  "title": "Lesson title",
  "lesson": "What was learned",
  "learned_at": "YYYY-MM-DDTHH:MM:SS+08:00",
  "context": "Situation or context",
  "mistake_or_success": "mistake/best_practice",
  "application": "How to apply this",
  "tags": ["#lesson", "#learning"],
  "memory_ref": "memory/YYYY-MM-DD.md"
}
```