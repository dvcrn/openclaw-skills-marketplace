# Automating Crew School with Cron

## Curriculum JSON Schema

Create `data/school-curriculum.json`:

```json
{
  "version": 1,
  "currentDay": 0,
  "lastSessionDate": null,
  "schedule": [
    {
      "day": 1,
      "agent": "ops",
      "topic": "Load Testing & Performance Benchmarking",
      "type": "gap-fill",
      "output": "knowledge/ops-load-testing.md",
      "prereqs": null
    },
    {
      "day": 1,
      "agent": "designer",
      "topic": "User Flow Mapping & Optimization",
      "type": "gap-fill",
      "output": "knowledge/designer-user-flow-optimization.md",
      "prereqs": null
    }
  ]
}
```

### Fields
- **day** — Curriculum day number (2 sessions per day)
- **agent** — Agent role (use "agent1+agent2" for joint sessions)
- **topic** — Learning topic title
- **type** — "gap-fill" (missing knowledge), "depth" (deepen existing), "applied" (practice), "joint" (cross-functional)
- **output** — File path for the knowledge article
- **prereqs** — Array of file paths to read first, or null

## Cron Job Setup

Create a cron that runs Mon–Fri before daily shifts:

```
Name: Crew School — Daily Learning Sessions
Schedule: 0 12 * * 1-5 (UTC) — adjust to run before your shifts
Session: isolated
Timeout: 300 seconds
```

### Cron Prompt Template

```
CREW SCHOOL — Run today's learning sessions.

1. Read `data/school-curriculum.json`. Use `currentDay` to find today's sessions.
   - If `lastSessionDate` is today, reply 'Already ran — HEARTBEAT_OK'.
   - Otherwise, increment `currentDay` by 1.

2. For each session on today's day number, spawn a sub-agent with the learning
   session template from the crew-school skill SKILL.md. Fill in:
   - Agent role and topic from the curriculum
   - Output file path from the curriculum
   - Prerequisites from the curriculum (or "None")
   - 2-3 context sentences about why the topic matters

3. Update `data/school-curriculum.json`:
   - Set `lastSessionDate` to today (YYYY-MM-DD)
   - Increment `currentDay`

4. If `currentDay` exceeds max day in schedule, report 'Curriculum complete.'

5. Log which sessions were started.
```

## Progress Monitoring

Check learning progress periodically:

```bash
# Count knowledge articles produced
ls -la knowledge/ | wc -l

# Check recent learning log
tail -20 memory/learning-log.md

# Find low-quality sessions (short articles)
wc -l knowledge/*.md | sort -n | head -10

# Find articles with no citations
for f in knowledge/*.md; do
  count=$(grep -c "http" "$f" 2>/dev/null || echo 0)
  if [ "$count" -lt 3 ]; then echo "$f: $count sources"; fi
done
```

## Re-running Failed Sessions

If a session produces <100 lines or planning-only output:
1. Check the session transcript for what went wrong
2. Re-spawn with stronger execution language and longer timeout
3. Add explicit "Your previous attempt failed because [reason]" to the prompt
