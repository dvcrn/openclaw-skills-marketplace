---
name: copper
description: "Copper CRM integration — manage people, companies, opportunities, projects, tasks, and activities via the Copper REST API. Google Workspace native CRM with relationship intelligence. Built for AI agents — Python stdlib only, zero dependencies. Use for CRM management, deal tracking, relationship mapping, project management, and sales pipeline automation."
homepage: https://www.agxntsix.ai
---

# 🟤 Copper CRM

Copper CRM integration — manage people, companies, opportunities, projects, tasks, and activities via the Copper REST API.

## Features

- **People management** — contacts with full CRUD and search
- **Company tracking** — organizations, details, relationships
- **Opportunity pipeline** — deals, stages, values, win rates
- **Project management** — track projects with stages and tasks
- **Task management** — create, assign, complete tasks
- **Activity logging** — calls, meetings, notes on any record
- **Relationship mapping** — see connections between records
- **Search** across all entity types
- **Custom fields** — read and write custom field values
- **Pipeline reports** — value, velocity, conversion metrics

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `COPPER_API_KEY` | ✅ | API key/token for Copper CRM |
| `COPPER_EMAIL` | ✅ | Your Copper account email |

## Quick Start

```bash
# List people/contacts
python3 {baseDir}/scripts/copper.py people --limit 20
```

```bash
# Get person details
python3 {baseDir}/scripts/copper.py person-get 12345
```

```bash
# Create a person
python3 {baseDir}/scripts/copper.py person-create '{"name":"Jane Doe","emails":[{"email":"jane@example.com"}]}'
```

```bash
# Update a person
python3 {baseDir}/scripts/copper.py person-update 12345 '{"title":"VP Sales"}'
```



## Commands

### `people`
List people/contacts.
```bash
python3 {baseDir}/scripts/copper.py people --limit 20
```

### `person-get`
Get person details.
```bash
python3 {baseDir}/scripts/copper.py person-get 12345
```

### `person-create`
Create a person.
```bash
python3 {baseDir}/scripts/copper.py person-create '{"name":"Jane Doe","emails":[{"email":"jane@example.com"}]}'
```

### `person-update`
Update a person.
```bash
python3 {baseDir}/scripts/copper.py person-update 12345 '{"title":"VP Sales"}'
```

### `companies`
List companies.
```bash
python3 {baseDir}/scripts/copper.py companies --limit 20
```

### `company-create`
Create a company.
```bash
python3 {baseDir}/scripts/copper.py company-create '{"name":"Acme Corp"}'
```

### `opportunities`
List opportunities.
```bash
python3 {baseDir}/scripts/copper.py opportunities --limit 20
```

### `opportunity-create`
Create opportunity.
```bash
python3 {baseDir}/scripts/copper.py opportunity-create '{"name":"Acme Deal","monetary_value":50000}'
```

### `projects`
List projects.
```bash
python3 {baseDir}/scripts/copper.py projects --limit 20
```

### `tasks`
List tasks.
```bash
python3 {baseDir}/scripts/copper.py tasks --limit 20 --status open
```

### `task-create`
Create a task.
```bash
python3 {baseDir}/scripts/copper.py task-create '{"name":"Follow up","due_date":"2026-03-01"}'
```

### `activities`
List activities for a record.
```bash
python3 {baseDir}/scripts/copper.py activities --person 12345
```

### `search`
Search across all records.
```bash
python3 {baseDir}/scripts/copper.py search "Acme"
```

### `pipelines`
List pipelines.
```bash
python3 {baseDir}/scripts/copper.py pipelines
```

### `pipeline-report`
Pipeline summary report.
```bash
python3 {baseDir}/scripts/copper.py pipeline-report
```


## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
# JSON (default, for programmatic use)
python3 {baseDir}/scripts/copper.py people --limit 5

# Human-readable
python3 {baseDir}/scripts/copper.py people --limit 5 --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/copper.py` | Main CLI — all Copper CRM operations |

## Data Policy

This skill **never stores data locally**. All requests go directly to the Copper CRM API and results are returned to stdout. Your data stays on Copper CRM servers.

## Credits
---
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
