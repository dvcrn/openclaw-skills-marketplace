---
name: work-helper
description: "Assistant de travail personnel pour consultant/freelance sysops. Use when: logging an activity, taking a note, creating a reminder, generating a recap or CRA, ingesting a handwritten PDF from reMarkable, exporting journal to Nextcloud or email. NOT for: time-tracking (Toggl), task management/kanban (Jira/Trello), GitHub/Jira auto-pull, CalDAV calendar, or periodic mail checks."
homepage: https://github.com/Rwx-G/openclaw-skill-work-helper
---

# work-helper

Assistant de travail personnel, conversationnel et self-hosted, pour consultant/freelance sysops.

## Fonctionnalites

### Journal d'activite (`log`)

Enregistrement horodate de ce qui a ete fait, avec contexte.

```bash
python3 work_helper.py log add "Reunion client X -- revue architecture reseau"
python3 work_helper.py log add "Deploy infra staging" --project acme --duration 2h --tags deploy,infra
python3 work_helper.py log today
python3 work_helper.py log week
python3 work_helper.py log month
python3 work_helper.py log search "architecture"
```

### Notes (`note`)

Notes libres associees a un projet ou contexte.

```bash
python3 work_helper.py note add "Penser a migrer le DNS avant vendredi"
python3 work_helper.py note add "Schema reseau client Y" --project clientY
python3 work_helper.py note list
python3 work_helper.py note list --project clientY
python3 work_helper.py note search "DNS"
```

### Rappels (`remind`)

Creation de rappels via crons OpenClaw (systemEvent).

```bash
python3 work_helper.py remind add "Demo client" --date 2026-03-15 --time 14:30
python3 work_helper.py remind add "CRA" --every friday --time 17:00
python3 work_helper.py remind list
python3 work_helper.py remind cancel <id>
```

> **Note cron_delete** : `remind cancel` emet un `cron_delete` avec le `name` du cron
> (`work-helper-remind-<id>`). Le cron tool OpenClaw opere par `jobId`, pas par `name`.
> L'agent doit donc faire un `cron list` pour retrouver le `jobId` correspondant au `name`
> avant de supprimer le cron.

### Recapitulatifs LLM (`recap`)

Synthese intelligente du journal par periode.

```bash
python3 work_helper.py recap today
python3 work_helper.py recap week
python3 work_helper.py recap month
```

### CRA consultant (`cra`)

Compte Rendu d'Activite formate.

```bash
python3 work_helper.py cra week
python3 work_helper.py cra month
python3 work_helper.py cra week --format table
python3 work_helper.py cra week --format markdown
```

### Ingestion reMarkable (`ingest`)

Traitement d'un PDF manuscrit. Transcription via API Vision, puis structuration LLM.

```bash
python3 work_helper.py ingest --pdf scan.pdf --mode meeting
python3 work_helper.py ingest --mode log
python3 work_helper.py ingest --mode notes --project clientX
python3 work_helper.py ingest --mode cra
```

### Vue synthetique (`status`)

```bash
python3 work_helper.py status
```

### Export (`export`)

```bash
python3 work_helper.py export nextcloud --period week
python3 work_helper.py export email --to romain@example.com --period week
python3 work_helper.py export file --period month
```

## Storage & credentials

| Chemin | Type | Contenu |
|--------|------|---------|
| `~/.openclaw/config/work-helper/config.json` | config | Comportement, LLM, outputs (pas de secrets) |
| `~/.openclaw/secrets/openai_api_key` | secret | Cle API LLM (chmod 600, partagee avec veille) |
| `~/.openclaw/data/work-helper/journal.json` | data | Entrees d'activite horodatees |
| `~/.openclaw/data/work-helper/notes.json` | data | Notes libres |
| `~/.openclaw/data/work-helper/reminders.json` | data | Rappels actifs |
| `~/.openclaw/data/work-helper/projects.json` | data | Projets actifs + metadata |
| `~/.openclaw/data/work-helper/ingest/` | data | PDFs telecharges (ingestion) |
| `~/.openclaw/data/work-helper/exports/` | data | Exports locaux (markdown) |

## Configuration

`~/.openclaw/config/work-helper/config.json` -- voir `config.example.json`.

## Dependencies OpenClaw

- **mail-client** -- lecture email + pieces jointes (ingestion reMarkable, export email)
- **nextcloud-files** -- export cloud optionnel
