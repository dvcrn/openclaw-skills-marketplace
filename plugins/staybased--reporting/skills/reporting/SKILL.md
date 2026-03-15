---
name: reporting
description: "Standardized templates for periodic reports, system audits, revenue tracking, and progress logs.\n All output goes to workspace/artifacts/ directory.\n\n Use when: generating periodic reports, system audits, performance reviews, revenue tracking,\n weekly retrospectives, daily progress logs, full workspace audits.\n\n Don't use when: ad-hoc status updates in chat, quick summaries in Discord,\n one-off answers to \"how's it going?\", real-time dashboards.\n\n Negative examples:\n - \"Give me a quick update\" → No. Just answer in chat.\n - \"What's the weather?\" → No. This is for structured reports.\n - \"Post a status to Discord\" → No. Just send a message.\n\n Edge cases:\n - Mid-week report requested → Use weekly template but note partial week.\n - Audit requested for single subsystem → Use full audit template, mark other sections N/A.\n - Revenue snapshot with $0 revenue → Still generate it. Zeros are data."
---

# Reporting — Standardized Report Templates

All reports output to `workspace/artifacts/` with naming convention:
`{type}-{YYYY-MM-DD}.md`

---

## Report Types

### 1. Weekly Retrospective

**File:** `artifacts/weekly-retro-YYYY-MM-DD.md`
**Cadence:** Sunday evening
**Template:** `templates/weekly-retro.md`

Covers: revenue, agent economy, what shipped, what stalled, service uptime, next week priorities.

### 2. Full System Audit

**File:** `artifacts/full-audit-YYYY-MM-DD.md`
**Cadence:** Monthly or on-demand
**Template:** `templates/full-audit.md`

Covers: executive summary, revenue pipeline, workflow gaps, agent utilization, infrastructure efficiency, tool inventory, cron effectiveness, strategy assessment, content status, recommendations.

### 3. Daily Progress Log

**File:** `artifacts/daily-log-YYYY-MM-DD.md`
**Cadence:** End of day
**Template:** `templates/daily-log.md`

Covers: tasks completed, decisions made, blockers, tomorrow's priorities.

### 4. Revenue Snapshot

**File:** `artifacts/revenue-YYYY-MM-DD.md`
**Cadence:** Weekly or on-demand
**Template:** `templates/revenue-snapshot.md`

Covers: income by stream, expenses, net P&L, progress toward goals, trading performance.

---

## Templates

See `templates/` directory for each template file. All use `{{PLACEHOLDER}}` syntax for variable substitution.

---

## Output Standards

- All reports go to `workspace/artifacts/`
- Use ISO dates in filenames
- Include generation timestamp and author at bottom
- Include "Executive Summary" at top for reports >1 page
- Link to source data where possible
