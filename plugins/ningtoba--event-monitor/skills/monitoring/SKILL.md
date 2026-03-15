---
name: monitoring
description: "Monitors system CPU and Memory usage, saves metrics to SQLite database, and generates Excel reports."
---

# Monitoring Skill

This skill allows you to monitor system resources and track historical usage patterns.

## Security & Permissions

| Category | Details |
|----------|---------|
| **System Access** | Reads process list via `psutil` (read-only) |
| **File Writes** | Creates `monitoring.db` (SQLite) and `system_report.xlsx` in skill directory only |
| **Network** | None - fully offline, no external connections |
| **APIs** | None - no external API calls |
| **Credentials** | None required |
| **Shell Commands** | None - pure Python execution |

### Why These Permissions?

- **psutil**: Industry-standard library for reading system metrics (used by VS Code, PyCharm, etc.)
- **SQLite**: Local embedded database, no server needed
- **openpyxl**: Standard Excel library, no macros or VBA

This skill is **benign** - it only reads public system information and writes to its own directory.

## Commands

### /collect-metrics
Triggers a collection of the top 10 CPU and Memory consuming processes.
The results are saved to a local SQLite database `monitoring.db` in the skill directory.

### /generate-report
Generates an Excel report of the latest captured metrics from the database.

### /show-metrics [limit=10]
Displays the most recent metrics from the database.

## Database

- **Location:** `{skillDir}/monitoring.db`
- **Tables:** `cpu_usage_table`, `memory_usage_table`
- **Format:** SQLite 3

## Usage

```bash
# Collect current metrics
python {skillDir}/monitoring.py --collect

# Generate Excel report
python {skillDir}/monitoring.py --report

# Show recent metrics
python {skillDir}/monitoring.py --show --limit 10
```

## Data Retention

Metrics include timestamp, day of week, week of month, month, and working day classification for trend analysis.
