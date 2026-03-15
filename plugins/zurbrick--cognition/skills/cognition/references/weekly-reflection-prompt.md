# Weekly Deep Reflection — Cron Prompt

Schedule: `0 4 * * 0` (Sunday 4 AM)
Recommended model: Any model with reliable tool use
Timeout: 600 seconds

## Prompt

```
You are running the Weekly Deep Reflection. This is "deep sleep" — the most thorough cognitive maintenance cycle.

## Task
Review the full week and perform deep system maintenance.

## Steps

1. **Load the week's daily logs:** Read `memory/YYYY-MM-DD.md` for the last 7 days.
2. **Load core files:** MEMORY.md, KNOWLEDGE_MAP.md, FUTURE_INTENTS.md, memory/procedures/index.yaml
3. **Load cross-references:** memory/bank/cross-references.md
4. **Load gap tracker:** memory/meta/gap_tracker.json

5. **Weekly Summary:**
   - Identify recurring themes across the week
   - Flag growing expertise areas
   - Flag persistent problems (same issue 3+ days)
   - Write summary to `memory/summaries/YYYY-WNN.md`

6. **MEMORY.md Maintenance:**
   - Check entries against TTL (customize per domain)
   - Archive expired entries to bank files
   - Verify index pointers resolve to valid files
   - Keep under 3K tokens / 12K chars

7. **KNOWLEDGE_MAP Recalculation:**
   - Domains not touched this week: reduce confidence by 0.05
   - Domains with errors/corrections: reduce by 0.10
   - Domains actively used successfully: boost by 0.05
   - Update "Last Verified" dates

8. **Knowledge Gap Review:**
   - Read memory/meta/gap_tracker.json
   - Gaps with 3+ misses: surface as research tasks
   - Add new gaps discovered this week

9. **Procedure Audit:**
   - Flag procedures below 0.3 success rate
   - Flag procedures not used in 30+ days
   - Compile new procedures from the week's novel solutions

10. **Cross-Reference Update:**
    - Add new links discovered this week
    - Remove links to deleted/archived files

11. **FUTURE_INTENTS Cleanup:**
    - Archive completed intents older than 7 days
    - Flag overdue intents

12. **Self-Improvement Review:**
    - Check learnings for patterns recurring 3+ times → recommend promotion to AGENTS.md
    - Flag rules being consistently ignored

13. **State of Knowledge Report:**
    - Coverage estimate
    - Improving vs degrading domains
    - Top 3 gaps to close next week
    - Specific recommendations

## Rules
- Do NOT modify SOUL.md or AGENTS.md directly — recommend only
- Compare against previous weekly summary if it exists
- Be honest about what's working and what's theater

## Critical: Tool Use Required
You MUST use the read and write tools. Do NOT describe — execute.
```
