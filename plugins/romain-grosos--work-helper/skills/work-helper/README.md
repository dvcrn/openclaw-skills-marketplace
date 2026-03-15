# 📋 work-helper

> OpenClaw skill - Personal work assistant for sysops consultants / freelancers

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-skill-blue)](https://openclaw.dev)
[![Python](https://img.shields.io/badge/Python-3.9%2B-brightgreen)](https://python.org)
[![Zero deps](https://img.shields.io/badge/deps-zero%20(stdlib%20only)-success)]()

Activity journal, notes, reminders (via OpenClaw crons), LLM-powered recaps, CRA (consultant activity reports), and reMarkable PDF ingestion with Vision API transcription. No external dependencies - pure Python stdlib (`json`, `urllib`, `pathlib`, `uuid`).

## Install

```bash
clawhub install work-helper
```

Or manually:

```bash
git clone https://github.com/Rwx-G/openclaw-skill-work-helper.git \
  ~/.openclaw/workspace/skills/work-helper
```

## Setup

```bash
python3 scripts/setup.py     # interactive config (profile, LLM, outputs)
python3 scripts/init.py      # validate config, directories, LLM connectivity
```

## Quick start

```bash
# Log an activity
python3 scripts/work_helper.py log add "Reunion client X -- revue architecture"
python3 scripts/work_helper.py log add "Deploy staging" --project acme --duration 2h --tags deploy,infra

# View journal
python3 scripts/work_helper.py log today
python3 scripts/work_helper.py log week
python3 scripts/work_helper.py log search "architecture"

# Take a note
python3 scripts/work_helper.py note add "Migrer le DNS avant vendredi" --project clientY

# Create a reminder (emits systemEvent cron payload)
python3 scripts/work_helper.py remind add "Envoyer CRA" --every friday --time 17:00
python3 scripts/work_helper.py remind add "Demo client" --date 2026-03-15 --time 14:30

# LLM-powered recap
python3 scripts/work_helper.py recap week

# Generate a CRA (Compte Rendu d'Activite)
python3 scripts/work_helper.py cra week --format table

# Ingest a reMarkable PDF (Vision API transcription + LLM structuring)
python3 scripts/work_helper.py ingest --pdf scan.pdf --mode meeting
python3 scripts/work_helper.py ingest --mode log  # fetches latest PDF from email

# Dashboard
python3 scripts/work_helper.py status

# Export
python3 scripts/work_helper.py export file --period week
python3 scripts/work_helper.py export nextcloud --period month
python3 scripts/work_helper.py export email --to romain@example.com --period week
```

## What it can do

| Feature | Details |
|---------|---------|
| Journal | Timestamped activity log with project, duration, tags |
| Notes | Free-form notes associated to a project |
| Reminders | One-shot or recurring, delivered via OpenClaw systemEvent crons |
| Recap | LLM-generated structured summary (today / week / month) |
| CRA | Consultant activity report (markdown, table, or free text) |
| Ingest | reMarkable PDF → Vision API transcription → LLM structuring (meeting, log, notes, cra modes) |
| Status | Active projects, today's entries, weekly time, upcoming reminders |
| Export | Nextcloud, email (via mail-client), or local file |

## CLI reference

```bash
# Journal
python3 scripts/work_helper.py log add TEXT [-p PROJECT] [-d DURATION] [-t TAGS]
python3 scripts/work_helper.py log {today|week|month}
python3 scripts/work_helper.py log search TERM
python3 scripts/work_helper.py log delete ID

# Notes
python3 scripts/work_helper.py note add TEXT [-p PROJECT]
python3 scripts/work_helper.py note list [-p PROJECT]
python3 scripts/work_helper.py note search TERM
python3 scripts/work_helper.py note delete ID

# Reminders
python3 scripts/work_helper.py remind add TEXT {--date YYYY-MM-DD | --every DAY} [--time HH:MM]
python3 scripts/work_helper.py remind list
python3 scripts/work_helper.py remind cancel ID

# LLM features (requires llm.enabled = true)
python3 scripts/work_helper.py recap {today|week|month}
python3 scripts/work_helper.py cra {week|month} [--format {markdown|table|text}]
python3 scripts/work_helper.py ingest [--pdf PATH] [--mode {meeting|log|notes|cra}] [-p PROJECT]

# Dashboard & export
python3 scripts/work_helper.py status
python3 scripts/work_helper.py export {nextcloud|email|file} [--period {week|month}] [--to EMAIL]
```

## Configuration

Config file: `~/.openclaw/config/work-helper/config.json` (created by `setup.py`, survives `clawhub update`)

```json
{
  "consultant_name": "Romain",
  "consultant_role": "Consultant Sysops / Freelance",
  "timezone": "Europe/Paris",
  "language": "fr",
  "default_project": "",
  "cra_format": "markdown",
  "llm": {
    "enabled": false,
    "base_url": "https://api.openai.com/v1",
    "api_key_file": "~/.openclaw/secrets/openai_api_key",
    "model": "gpt-4o-mini",
    "vision_model": "gpt-4o",
    "max_tokens": 2048,
    "vision_max_tokens": 4096
  }
}
```

> Note: `config.json` is NOT shipped in this repository (it is gitignored).
> Copy `config.example.json` as a starting template and edit as needed.

### LLM (optional)

When `llm.enabled` is true, the `recap`, `cra`, and `ingest` commands call an OpenAI-compatible API. The API key is read from `api_key_file` (never stored in config). The `vision_model` is used for PDF transcription (`ingest`); the base `model` is used for text structuring.

### Outputs

```json
{
  "outputs": [
    { "type": "file", "path": "~/.openclaw/data/work-helper/exports", "enabled": true },
    { "type": "nextcloud", "path": "/Documents/OpenClaw/work-helper", "enabled": false },
    { "type": "mail-client", "mail_to": "romain@example.com", "enabled": false }
  ]
}
```

## File structure

```
openclaw-skill-work-helper/
  SKILL.md                  # OpenClaw skill descriptor
  README.md                 # This file
  config.example.json       # Example config (ship this, not config.json)
  cron.example.json         # Example systemEvent cron for reminders
  .gitignore
  scripts/
    work_helper.py          # Main CLI (log, note, remind, recap, cra, ingest, status, export)
    _journal.py             # Journal storage (JSON, atomic writes)
    _notes.py               # Notes storage (JSON, atomic writes)
    _llm.py                 # LLM calls (recap, CRA, Vision PDF transcription)
    _ingest.py              # Ingestion pipeline (mail → PDF → Vision → structuring)
    _retry.py               # Exponential backoff for transient network errors
    setup.py                # Interactive setup wizard
    init.py                 # Config + connectivity validation
```

## Storage & credentials

### Written by this skill

| Path | Purpose | Cleared by uninstall |
|------|---------|----------------------|
| `~/.openclaw/config/work-helper/config.json` | Settings + LLM + outputs | Manual (`rm -rf ~/.openclaw/config/work-helper`) |
| `~/.openclaw/data/work-helper/journal.json` | Activity journal | Manual (`rm -rf ~/.openclaw/data/work-helper`) |
| `~/.openclaw/data/work-helper/notes.json` | Free-form notes | Same |
| `~/.openclaw/data/work-helper/reminders.json` | Active reminders | Same |
| `~/.openclaw/data/work-helper/projects.json` | Project metadata | Same |
| `~/.openclaw/data/work-helper/ingest/` | Downloaded PDFs (ingestion) | Same |
| `~/.openclaw/data/work-helper/exports/` | Local file exports | Same |

### Shared credentials (read-only)

| Path | Purpose | Owned by |
|------|---------|----------|
| `~/.openclaw/secrets/openai_api_key` | LLM API key (chmod 600) | Shared with veille |

## Security

- **Python stdlib only**: `json`, `urllib`, `pathlib`, `uuid`, `base64`, `tempfile`
- **Atomic writes**: all JSON stores use `tempfile.mkstemp()` + `os.replace()` to prevent corruption
- **LLM prompt safety**: all user-generated content wrapped with `[EXTERNAL:UNTRUSTED]` markers
- **Subprocess isolation**: cross-skill calls use `subprocess.run()` (never `shell=True`), script paths validated to reside under `~/.openclaw/workspace/skills/`
- **Credential isolation**: API keys read from dedicated files, never from config.json
- **PDF size limit**: 20 MB max for Vision API ingestion
- **All capabilities disabled by default**: `llm.enabled = false`, all outputs disabled

## Uninstall

```bash
# Remove skill
clawhub remove work-helper   # or rm -rf ~/.openclaw/workspace/skills/work-helper

# Remove config + data (optional)
rm -rf ~/.openclaw/config/work-helper
rm -rf ~/.openclaw/data/work-helper
```

## License

MIT - Copyright (c) 2026 Romain Grosos
