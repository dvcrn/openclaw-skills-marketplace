---
name: freshsales
description: "Freshsales CRM integration — manage contacts, leads, deals, accounts, tasks, and sales sequences via the Freshsales API. Track deal pipelines, automate lead assignments, log activities, and generate sales reports. Built for AI agents — Python stdlib only, no dependencies. Use for sales CRM, contact management, deal tracking, pipeline reporting, and sales automation."
homepage: https://www.agxntsix.ai
---

# 🟢 Freshsales

Freshsales CRM integration — manage contacts, leads, deals, accounts, tasks, and sales sequences via the Freshsales API.

## Features

- **Manage contacts** — create, update, search, and segment
- **Lead tracking** — capture, qualify, assign, and convert
- **Deal pipeline** — stages, values, forecasting, and won/lost
- **Account management** — company profiles and hierarchies
- **Task management** — create, assign, and track sales tasks
- **Activity logging** — calls, emails, meetings, and notes
- **Sales sequences** — view and manage outreach campaigns
- **Search** across contacts, leads, deals, and accounts
- **Reports** — pipeline value, conversion rates, activity metrics
- **Filters** — custom views with field-level filtering

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `FRESHSALES_API_KEY` | ✅ | API key/token for Freshsales |
| `FRESHSALES_DOMAIN` | ✅ | Your Freshsales domain (e.g. yourorg.freshsales.io) |

## Quick Start

```bash
# List contacts
python3 {baseDir}/scripts/freshsales.py contacts --limit 20
```

```bash
# Get contact details
python3 {baseDir}/scripts/freshsales.py contact-get 12345
```

```bash
# Create a contact
python3 {baseDir}/scripts/freshsales.py contact-create '{"first_name":"Jane","last_name":"Doe","email":"jane@example.com"}'
```

```bash
# Update a contact
python3 {baseDir}/scripts/freshsales.py contact-update 12345 '{"lead_score":85}'
```



## Commands

### `contacts`
List contacts.
```bash
python3 {baseDir}/scripts/freshsales.py contacts --limit 20
```

### `contact-get`
Get contact details.
```bash
python3 {baseDir}/scripts/freshsales.py contact-get 12345
```

### `contact-create`
Create a contact.
```bash
python3 {baseDir}/scripts/freshsales.py contact-create '{"first_name":"Jane","last_name":"Doe","email":"jane@example.com"}'
```

### `contact-update`
Update a contact.
```bash
python3 {baseDir}/scripts/freshsales.py contact-update 12345 '{"lead_score":85}'
```

### `leads`
List leads.
```bash
python3 {baseDir}/scripts/freshsales.py leads --limit 20 --sort updated_at
```

### `lead-create`
Create a lead.
```bash
python3 {baseDir}/scripts/freshsales.py lead-create '{"first_name":"John","company":"Acme"}'
```

### `deals`
List deals.
```bash
python3 {baseDir}/scripts/freshsales.py deals --limit 20
```

### `deal-create`
Create a deal.
```bash
python3 {baseDir}/scripts/freshsales.py deal-create '{"name":"Acme Upgrade","amount":50000}'
```

### `deal-update`
Update deal stage.
```bash
python3 {baseDir}/scripts/freshsales.py deal-update 789 '{"deal_stage_id":3}'
```

### `accounts`
List accounts.
```bash
python3 {baseDir}/scripts/freshsales.py accounts --limit 20
```

### `tasks`
List tasks.
```bash
python3 {baseDir}/scripts/freshsales.py tasks --limit 10 --status open
```

### `task-create`
Create a task.
```bash
python3 {baseDir}/scripts/freshsales.py task-create '{"title":"Follow up with Acme","due_date":"2026-03-01"}'
```

### `search`
Search across all entities.
```bash
python3 {baseDir}/scripts/freshsales.py search "Acme"
```

### `activities`
List recent activities.
```bash
python3 {baseDir}/scripts/freshsales.py activities --limit 20
```

### `pipeline`
Pipeline summary.
```bash
python3 {baseDir}/scripts/freshsales.py pipeline
```


## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
# JSON (default, for programmatic use)
python3 {baseDir}/scripts/freshsales.py contacts --limit 5

# Human-readable
python3 {baseDir}/scripts/freshsales.py contacts --limit 5 --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/freshsales.py` | Main CLI — all Freshsales operations |

## Data Policy

This skill **never stores data locally**. All requests go directly to the Freshsales API and results are returned to stdout. Your data stays on Freshsales servers.

## Credits
---
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
