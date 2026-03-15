# Guardian Scripts

Helper scripts for the Guardian skill. Most are invoked via the skill's CLI or cron jobs.

---

## pre_publish_check.py — Pre-Publish Safety Gate

**Purpose:** Prevents accidental data leakage before publishing to ClawHub.
Learned from BL-051: real gateway tokens were shipped in `audit_exports/` data.

### What it checks

| Check | Severity | Description |
|---|---|---|
| `audit_exports/` files included in publish | CRITICAL | Must never be shipped — may contain live tokens/context |
| SQLite `.db` / `.db-shm` / `.db-wal` files | CRITICAL | Database files must never be shipped |
| Long hex strings >24 chars | CRITICAL | Potential hex-encoded secrets/tokens |
| Mixed alphanumeric strings ≥32 chars (no underscores) | CRITICAL | Potential API keys / bearer tokens |
| `gateway_token = "..."` assignments | CRITICAL | Real token value assignments (not mentions/comments) |
| Known secret values from `~/.openclaw/openclaw.json` | CRITICAL | Actual credentials from your local config |
| `.db` / `audit_exports/` files present on disk but excluded | WARNING | Good — just informational |

### Usage

```bash
# From the skill root
python3 scripts/pre_publish_check.py

# Or specify an explicit path
python3 scripts/pre_publish_check.py --path /path/to/skill

# Exit code: 0 = PASSED, 1 = FAILED (critical issues found)
```

### Run before every publish

```bash
# Recommended workflow:
python3 scripts/pre_publish_check.py && clawhub publish
```

If it exits non-zero, **do not publish**. Fix the issues first.

### False positives

If a long string is legitimately safe (e.g., a known-safe test fixture hash), you can:
1. Add it to a Python comment — comment lines are skipped
2. Add the file to `.clawhubignore` if it shouldn't be published at all

### Configuration

Secret values are loaded from `~/.openclaw/openclaw.json` automatically. The check
filters out values that look like config identifiers (snake_case, no digits, etc.)
to reduce false positives.

---

## Other Scripts

| Script | Purpose |
|---|---|
| `guardian.py` | Main Guardian CLI entrypoint |
| `serve.py` | Dashboard HTTP server |
| `onboard.py` | First-run setup / cron installation |
| `runtime_monitor.py` | Real-time session monitoring |
| `egress_scanner.py` | Outbound data exfiltration detection |
| `local_audit.py` | Local audit log queries |
| `audit_export.py` | Export audit data (output goes to `audit_exports/` — never publish) |
| `daily_digest.py` | Daily summary report |
| `dashboard_export.py` | Export dashboard data to JSON |
| `admin.py` | Admin utilities |
| `check_updates.py` | Check for Guardian skill updates |
| `telegram_notify.py` | Telegram notification helper |
| `primary_notify_local.py` | Local notification dispatcher |
| `noc-guardian-threats.py` | NOC dashboard threat feed |
| `noc-email-collector.py` | NOC dashboard email collector |
