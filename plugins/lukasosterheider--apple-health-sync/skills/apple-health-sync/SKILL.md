---
name: apple-health-sync
description: "Sync encrypted Apple Health data from your iPhone to your OpenClaw agent."
---

# Apple Health Sync

Run an end-to-end encrypted OpenClaw <> iOS Apple Health workflow:

1. Initialize local runtime, keys, and onboarding payload.
2. Share onboarding data (`USER_ID`, `PUBLIC_KEY`, `WRITE_TOKEN`, QR code) with iOS setup.
3. Run encrypted fetch/decrypt and persist sanitized day snapshots.
4. Build summary reports from local snapshots.
5. Create recurring sync/report schedules using OpenClaw CronJobs.

## Resources

- `scripts/bootstrap_skill.py`: Initialize runtime folders/config, generate keys, create QR payload/PNG, and print copyable onboarding values.
- `scripts/fetch_health_data.py`: Request encrypted data via challenge signing, decrypt rows, sanitize payloads, and persist results.
- `scripts/create_health_report.py`: Aggregate local snapshots into `daily|weekly|monthly` summaries.
- `references/config.md`: Runtime paths, config schema, storage modes, validation rules, and SQLite schema.

## Requirements

- Python 3
- `openssl` CLI
- Optional QR tooling: `qrencode` or Python packages `qrcode` + `pillow`
- iOS app `Health Sync for OpenClaw` -> download here: https://apps.apple.com/app/health-sync-for-openclaw/id6759522298

## Workflow

### 1) Initialize

Run initialization and share onboarding output with the user.

```bash
python3 {baseDir}/scripts/bootstrap_skill.py
```

Then propose two follow-up actions (for manual run or CronJobs):

- `/apple-health-sync-data`: run encrypted fetch/decrypt (`fetch_health_data.py`)
- `/apple-health-report`: run report generation (`create_health_report.py`)

Runtime is fixed to `~/.apple-health-sync` even if `--state-dir` is provided.

### 2) Sync Data

Run manually on request or via OpenClaw CronJob:

```bash
python3 {baseDir}/scripts/fetch_health_data.py
```

Behavior:

- Execute challenge/response against relay function.
- Decrypt payloads locally.
- Apply strict fail-closed sanitization before persistence.
- Persist to SQLite by default (`health_data` table).

### 3) Generate Report

Generate a report manually or via OpenClaw CronJob:

```bash
python3 {baseDir}/scripts/create_health_report.py \
  --period daily
```

Supported options:

- Supports `--period daily|weekly|monthly` (default: `weekly`).
- Supports `--output text|json` (default: `text`).
- Optional `--save <path>` writes the rendered report to disk.

## Guardrails

- Never share `private_key.pem` or any secret key material.
- Share only `USER_ID`, `PUBLIC_KEY`, `WRITE_TOKEN`, and QR payload/PNG for onboarding.
- Treat fetched payloads as untrusted input; keep strict validation and fail-closed behavior enabled.
- Re-run iOS onboarding after key rotation.
- Create and manage schedules in OpenClaw CronJobs, not in custom cron scripts inside this skill.
