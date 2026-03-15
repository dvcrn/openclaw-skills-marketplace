---
name: make
description: "Make (formerly Integromat) automation platform — manage scenarios, trigger runs, monitor executions, manage connections, and handle data stores via the Make API. Build and manage visual automations, monitor execution logs, manage team resources, and trigger workflows. Built for AI agents — Python stdlib only, zero dependencies. Use for visual workflow automation, scenario management, execution monitoring, integration management, and no-code automation."
homepage: https://www.agxntsix.ai
---

# 🔧 Make (Integromat)

Make (formerly Integromat) automation platform — manage scenarios, trigger runs, monitor executions, manage connections, and handle data stores via the Make API.

## Features

- **Scenario management** — list, activate, deactivate scenarios
- **Trigger runs** — execute scenarios on demand
- **Execution logs** — monitor run history and status
- **Connection management** — view and manage app connections
- **Data store operations** — CRUD on data stores
- **Webhook management** — create and manage webhooks
- **Organization management** — teams and users
- **Template browsing** — discover scenario templates
- **Blueprint export** — export scenario definitions
- **Usage monitoring** — operations and data transfer stats

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `MAKE_API_KEY` | ✅ | API key/token for Make (Integromat) |
| `MAKE_ZONE` | ❌ | API zone (default: us1.make.com) |

## Quick Start

```bash
# List scenarios
python3 {baseDir}/scripts/make.py scenarios --limit 20
```

```bash
# Get scenario details
python3 {baseDir}/scripts/make.py scenario-get 12345
```

```bash
# Trigger a scenario run
python3 {baseDir}/scripts/make.py scenario-run 12345
```

```bash
# Activate a scenario
python3 {baseDir}/scripts/make.py scenario-activate 12345
```



## Commands

### `scenarios`
List scenarios.
```bash
python3 {baseDir}/scripts/make.py scenarios --limit 20
```

### `scenario-get`
Get scenario details.
```bash
python3 {baseDir}/scripts/make.py scenario-get 12345
```

### `scenario-run`
Trigger a scenario run.
```bash
python3 {baseDir}/scripts/make.py scenario-run 12345
```

### `scenario-activate`
Activate a scenario.
```bash
python3 {baseDir}/scripts/make.py scenario-activate 12345
```

### `scenario-deactivate`
Deactivate a scenario.
```bash
python3 {baseDir}/scripts/make.py scenario-deactivate 12345
```

### `executions`
List execution logs.
```bash
python3 {baseDir}/scripts/make.py executions --scenario 12345 --limit 20
```

### `execution-get`
Get execution details.
```bash
python3 {baseDir}/scripts/make.py execution-get exec_abc
```

### `connections`
List connections.
```bash
python3 {baseDir}/scripts/make.py connections --limit 20
```

### `data-stores`
List data stores.
```bash
python3 {baseDir}/scripts/make.py data-stores
```

### `data-store-records`
List data store records.
```bash
python3 {baseDir}/scripts/make.py data-store-records 789 --limit 50
```

### `webhooks`
List webhooks.
```bash
python3 {baseDir}/scripts/make.py webhooks
```

### `webhook-create`
Create a webhook.
```bash
python3 {baseDir}/scripts/make.py webhook-create '{"name":"My Hook"}'
```

### `organizations`
List organizations.
```bash
python3 {baseDir}/scripts/make.py organizations
```

### `users`
List team users.
```bash
python3 {baseDir}/scripts/make.py users
```

### `usage`
Get usage stats.
```bash
python3 {baseDir}/scripts/make.py usage
```


## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
# JSON (default, for programmatic use)
python3 {baseDir}/scripts/make.py scenarios --limit 5

# Human-readable
python3 {baseDir}/scripts/make.py scenarios --limit 5 --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/make.py` | Main CLI — all Make (Integromat) operations |

## Data Policy

This skill **never stores data locally**. All requests go directly to the Make (Integromat) API and results are returned to stdout. Your data stays on Make (Integromat) servers.

## Credits
---
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
