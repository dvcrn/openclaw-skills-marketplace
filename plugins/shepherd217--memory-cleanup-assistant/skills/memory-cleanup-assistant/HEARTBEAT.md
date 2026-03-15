## Memory Cleanup Assistant - Heartbeat

### Weekly (Sunday recommended):

```markdown
## Memory Cleanup Check (every Sunday)
If Sunday and not cleaned in 7 days:
  1. Run memory audit
  2. If total_context_size > 50KB:
     - Alert user with savings estimate
     - Suggest running cleanup
  3. If auto_cleanup enabled:
     - Run dry-run first
     - If savings > 10KB and no errors:
       - Execute cleanup
       - Log results to memory/cleanup-log.md
```

### Auto-Cleanup (if enabled):

```markdown
## Auto Memory Cleanup Check (daily)
If memory-cleanup auto-cleanup enabled:
  1. Check if cleanup is due (7 days since last)
  2. If due, run auto-cleanup:
     - Audit context files
     - If savings > thresholdKB (default 50KB):
       - Execute cleanup automatically
       - Update last_cleanup timestamp
       - Notify user of savings
     - If savings < threshold:
       - Skip cleanup
       - Log "skipped due to low savings"
```

### Enable Auto-Cleanup:

```bash
memory-cleanup auto-enable "0 0 * * 0"  # Weekly on Sunday
```

Or add to your agent's HEARTBEAT.md:
```markdown
## Auto Memory Cleanup
Run daily: memory-cleanup auto-run
```

### Daily (optional - for heavy users):

```markdown
## Daily Size Check (if PRO enabled)
If daily_check_enabled:
  1. Check SOUL.md + AGENTS.md + MEMORY.md size
  2. If growth > 5KB since yesterday:
     - Alert: "Rapid context growth detected"
     - Suggest immediate audit
```

### Monthly:

```markdown
## Monthly Archive Review
If 1st of month:
  1. Check memory/archive/ size
  2. If archive > 100MB:
     - Suggest compressing old archives
  3. Generate monthly savings report
```
