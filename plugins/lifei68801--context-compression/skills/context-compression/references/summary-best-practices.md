# Summary Best Practices

## Summary Hierarchy

OpenClaw uses a four-level memory architecture:

```
L1: Current Context (real-time)
    ↓ Compress
L2: Session Summary (every 6 hours)
    ↓ Merge
L3: Weekly Summary (every Sunday)
    ↓ Extract
L4: Long-term Memory (MEMORY.md)
```

## L2 Summary: Session Summary

### Trigger Conditions

- Auto-generated every 6 hours
- Triggered when context >80%
- User manual request

### Summary Format

```markdown
# Session Summary - YYYY-MM-DD

## Meta
- Session: <session-id>
- Turns: XX
- Channel: <channel>
- Time range: HH:MM - HH:MM

## Key Conversations (last 10)
1. [User] Question keywords → [Assistant] Key points
2. [User] Question keywords → [Assistant] Key points
...

## Important Decisions
- Decision 1: Description
- Decision 2: Description

## Task Results
- ✅ Task name: Result
- ❌ Task name: Failure reason

## Pending Items
- [ ] Todo 1
- [ ] Todo 2

---
*Full session: ~/.openclaw/agents/main/sessions/<id>.jsonl*
```

### Summary Principles

1. **Concise**: Each summary <1500 characters
2. **Extract key points**: Only keep critical information
3. **Preserve decisions**: Important decisions affect future
4. **Record results**: Task completion status
5. **Reference original**: Provide full session path

### Generation Commands

```bash
# Auto-generate summary
openclaw session summarize <session-id>

# View summary
cat memory/sessions/daily/qqbot-direct-YYYY-MM-DD.md
```

## L3 Summary: Weekly Summary

### Trigger Conditions

- Auto-merge every Sunday at 23:00
- When L2 summaries exceed 7

### Summary Format

```markdown
# Weekly Summary - YYYY Week WW

## Daily Highlights
- Monday: Highlight 1
- Tuesday: Highlight 2
...

## Important Decisions Summary
- Decision 1 (Monday): Description
- Decision 2 (Wednesday): Description

## User Preference Updates
- New preference: Description
- Modified preference: Description

## Key Task Results
- Task 1: Result
- Task 2: Result

---
*Details in daily/ directory*
```

### Merge Principles

1. **Deduplicate**: Merge same topics
2. **Prioritize**: Sort by importance
3. **Simplify**: Remove outdated info
4. **Connect**: Link related decisions

## L4 Memory: Long-term Memory

### Storage Location

`MEMORY.md` - OpenClaw workspace root

### Content Types

1. **User Information**
   - Basic profile
   - Communication preferences
   - Work habits

2. **Important Decisions**
   - Decisions affecting future
   - Reasons and rationale
   - Execution results

3. **User Preferences**
   - Learned preferences
   - Update history

4. **Key Tasks**
   - Completed important tasks
   - Outstanding issues

### Update Principles

1. **Value-based**: Only store long-term value info
2. **No duplication**: Avoid repeating existing content
3. **Regular cleanup**: Remove outdated info
4. **Structured**: Use clear structure

### Update Timing

- Auto-extract daily at 23:00
- When important decisions occur
- When user preferences change

## Automation Configuration

### Cron Job Configuration

```json
{
  "jobs": [
    {
      "name": "Daily Session Summary",
      "schedule": {
        "kind": "cron",
        "expr": "0 0,4,8,12,16,20 * * *",
        "tz": "Asia/Shanghai"
      }
    },
    {
      "name": "Weekly Summary Merge",
      "schedule": {
        "kind": "cron",
        "expr": "0 23 * * 0",
        "tz": "Asia/Shanghai"
      }
    },
    {
      "name": "Long-term Memory Update",
      "schedule": {
        "kind": "cron",
        "expr": "0 23 * * *",
        "tz": "Asia/Shanghai"
      }
    }
  ]
}
```

## Best Practices

### Summary Quality Checklist

- ✅ Key conversations are representative
- ✅ Decisions are clear and complete
- ✅ Task results are accurate
- ✅ Character count <1500 (L2) or <2000 (L3)

### Avoid

- ❌ Copy-pasting original text
- ❌ Missing important decisions
- ❌ Overly detailed summaries
- ❌ Not recording failed tasks

### Context Recovery

When needing to recover context from a specific day:

1. Read L2 summary: `memory/sessions/daily/`
2. Find L3 summary: `memory/sessions/weekly/`
3. Check long-term memory: `MEMORY.md`
4. For full context: `~/.openclaw/agents/main/sessions/`
