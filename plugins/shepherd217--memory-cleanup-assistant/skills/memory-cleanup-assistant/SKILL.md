---
name: memory-cleanup-assistant
description: "Memory Cleanup Assistant"
---

# Memory Cleanup Assistant

## Description
Stop burning tokens on bloated context files. Auto-audit and compress SOUL.md, AGENTS.md, MEMORY.md, and daily memory files. Save $50-200/week in API costs.

## The Problem
Every OpenClaw session reloads ALL context files:
- SOUL.md (grows with personality)
- AGENTS.md (accumulates workflows)  
- MEMORY.md (never gets cleaned)
- memory/YYYY-MM-DD.md (daily files pile up)

**Result:** 73KB → $200/week in token costs

## Quick Start

```bash
# Quick audit
memory-cleanup audit

# Enable auto-cleanup (recommended)
memory-cleanup auto-enable "0 0 * * 0"  # Weekly on Sunday

# Check status
memory-cleanup status
```

## Commands

### Audit
```bash
memory-cleanup audit
```
Shows current file sizes, duplicates, and potential savings.

### Manual Cleanup
```bash
# Dry run (preview changes)
memory-cleanup clean --dry-run

# Execute cleanup
memory-cleanup clean --confirm
```

### Auto-Cleanup (NEW ✨)

```bash
# Enable auto-cleanup with custom schedule
memory-cleanup auto-enable "0 0 * * 0"  # Weekly on Sunday
memory-cleanup auto-enable "0 0 * * *"  # Daily

# Disable auto-cleanup
memory-cleanup auto-disable

# Run auto-cleanup check manually
memory-cleanup auto-run

# Check auto-cleanup status
memory-cleanup status
```

**How Auto-Cleanup Works:**
- Runs automatically based on schedule
- Only cleans if savings > threshold (default 50KB)
- Creates backups before cleaning
- Updates last_cleanup timestamp
- Notifies you of savings

## Configuration

Config stored in `~/.openclaw/workspace/.memory-cleanup-config.json`:

```json
{
  "autoCleanup": true,
  "schedule": "0 0 * * 0",
  "thresholdKB": 50,
  "dailyRetention": 7,
  "enabled": true
}
```

## How It Works

### Compression Strategies

**SOUL.md:**
- Merge duplicate personality traits
- Remove contradictory instructions
- Archive old "experiments" section

**AGENTS.md:**
- Deduplicate error handling patterns
- Remove deprecated workflow steps
- Compress verbose instructions

**MEMORY.md:**
- Identify superseded learnings
- Archive decisions that no longer apply
- Summarize related memories

**Daily Files:**
- Auto-archive after 7 days
- Weekly summarization
- Monthly rollup for long-term storage

### Safety Features

- ✅ Dry-run mode (preview all changes)
- ✅ Automatic backups to `.memory-backup/`
- ✅ Git commit before cleanup (if in repo)
- ✅ Never deletes, only archives
- ✅ Recovery command: `memory-cleanup restore`
- ✅ Auto-cleanup threshold (won't run if savings too low)

## Real User Results

> "Went from 73KB to 31KB. Claude Code is noticeably faster and my weekly API bill dropped from $180 to $85." - @exitliquidity

> "I didn't realize how much cruft had accumulated over 3 months. This should be built into OpenClaw." - @cybercentry

## Pricing

- **FREE:** Audit + dry-run + manual cleanup + auto-cleanup
- **PRO ($5/mo):** Weekly reports + size alerts + priority support
- **TEAM ($15/mo):** Multi-agent workspace cleanup + shared archives

## License

MIT - Stop burning tokens on bloat 🦞
