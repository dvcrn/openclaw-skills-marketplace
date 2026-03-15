# Nightly Consolidation — Cron Prompt

Schedule: `0 2 * * *` (2 AM daily)
Recommended model: Any model with reliable tool use (Sonnet 4+, GPT-5+)
Timeout: 300 seconds

## Prompt

```
You are running the Nightly Memory Consolidation job. This is the cognitive equivalent of hippocampal replay during sleep.

## Task
Process today's experiences into durable knowledge.

## Steps

1. **Read today's daily log:** `memory/YYYY-MM-DD.md` (use today's date)
2. **Read MEMORY.md** — the current knowledge index
3. **Read FUTURE_INTENTS.md** — current commitments
4. **Read KNOWLEDGE_MAP.md** — current confidence scores

5. **Process by priority:** Scan the daily log for `[REPLAY_PRIORITY: HIGH]` entries first, then MEDIUM, then everything else.

6. **Extract and consolidate:**
   - New facts → write to appropriate `memory/bank/` detail file if not already there
   - Corrections → fix the wrong entry in the appropriate file
   - Novel solutions → compile to `memory/procedures/` with steps, preconditions, failure modes. Update `memory/procedures/index.yaml`.
   - Commitments → add to FUTURE_INTENTS.md if not already captured
   - Lessons → append to `.learnings/LEARNINGS.md` (or equivalent)

7. **Deduplicate MEMORY.md:** If any index entry duplicates content in a bank file, slim the index entry to just a pointer.

8. **Update KNOWLEDGE_MAP.md:**
   - Recalculate confidence scores based on today's activity
   - Topics touched = boost confidence, topics with errors = reduce
   - Add any new knowledge gaps discovered
   - Update "Last Verified" dates for domains actively used today

9. **Check FUTURE_INTENTS.md:** Flag any items due tomorrow.

10. **Update procedure registry:** If you created new procedures, add to `memory/procedures/index.yaml`. Update success/failure rates for procedures used today.

11. **Write consolidation log** to `memory/consolidation/YYYY-MM-DD.md`

## Rules
- Do NOT invent information — only extract what's in the daily log
- Do NOT modify SOUL.md or AGENTS.md (flag recommendations instead)
- Keep MEMORY.md under 3K tokens / 12K chars
- If nothing meaningful happened, write a brief "quiet day" log and exit

## Critical: Tool Use Required
You MUST use the read and write tools to actually read files and write output. Do NOT just describe what you would do — actually do it.
```
