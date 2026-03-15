---
name: render
description: "Render cloud platform — manage services, deployments, databases, environment groups, and custom domains via the Render API. Deploy web services, static sites, cron jobs, and databases with automatic scaling. Built for AI agents — Python stdlib only, zero dependencies. Use for cloud deployment, service management, database provisioning, CI/CD automation, and infrastructure management."
homepage: https://www.agxntsix.ai
---

# 🚀 Render

Render cloud platform — manage services, deployments, databases, environment groups, and custom domains via the Render API.

## Features

- **Service management** — web services, static sites, cron jobs
- **Deployment tracking** — deploy history, rollbacks, status
- **Database management** — PostgreSQL provisioning and management
- **Environment variables** — manage env vars and env groups
- **Custom domains** — add and configure custom domains
- **Auto-deploy** — trigger deploys from API
- **Scaling** — manage instance count and plan
- **Logs** — access service logs
- **Bandwidth metrics** — monitor usage and costs
- **Blueprint sync** — infrastructure as code

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `RENDER_API_KEY` | ✅ | API key/token for Render |

## Quick Start

```bash
# List services
python3 {baseDir}/scripts/render.py services --limit 20
```

```bash
# Get service details
python3 {baseDir}/scripts/render.py service-get srv-abc123
```

```bash
# Create a service
python3 {baseDir}/scripts/render.py service-create '{"type":"web_service","name":"my-api","repo":"https://github.com/user/repo","branch":"main","runtime":"python"}'
```

```bash
# List deployments
python3 {baseDir}/scripts/render.py deploys --service srv-abc123 --limit 10
```



## Commands

### `services`
List services.
```bash
python3 {baseDir}/scripts/render.py services --limit 20
```

### `service-get`
Get service details.
```bash
python3 {baseDir}/scripts/render.py service-get srv-abc123
```

### `service-create`
Create a service.
```bash
python3 {baseDir}/scripts/render.py service-create '{"type":"web_service","name":"my-api","repo":"https://github.com/user/repo","branch":"main","runtime":"python"}'
```

### `deploys`
List deployments.
```bash
python3 {baseDir}/scripts/render.py deploys --service srv-abc123 --limit 10
```

### `deploy`
Trigger a deploy.
```bash
python3 {baseDir}/scripts/render.py deploy --service srv-abc123
```

### `deploy-rollback`
Rollback to previous deploy.
```bash
python3 {baseDir}/scripts/render.py deploy-rollback --service srv-abc123 --deploy dep-xyz
```

### `databases`
List databases.
```bash
python3 {baseDir}/scripts/render.py databases
```

### `database-create`
Create PostgreSQL database.
```bash
python3 {baseDir}/scripts/render.py database-create '{"name":"my-db","plan":"starter"}'
```

### `env-vars`
List environment variables.
```bash
python3 {baseDir}/scripts/render.py env-vars --service srv-abc123
```

### `env-set`
Set environment variable.
```bash
python3 {baseDir}/scripts/render.py env-set --service srv-abc123 "DATABASE_URL" "postgres://..."
```

### `env-delete`
Delete environment variable.
```bash
python3 {baseDir}/scripts/render.py env-delete --service srv-abc123 DATABASE_URL
```

### `domains`
List custom domains.
```bash
python3 {baseDir}/scripts/render.py domains --service srv-abc123
```

### `domain-add`
Add custom domain.
```bash
python3 {baseDir}/scripts/render.py domain-add --service srv-abc123 api.example.com
```

### `logs`
Get service logs.
```bash
python3 {baseDir}/scripts/render.py logs --service srv-abc123 --limit 100
```

### `suspend`
Suspend a service.
```bash
python3 {baseDir}/scripts/render.py suspend --service srv-abc123
```


## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
# JSON (default, for programmatic use)
python3 {baseDir}/scripts/render.py services --limit 5

# Human-readable
python3 {baseDir}/scripts/render.py services --limit 5 --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/render.py` | Main CLI — all Render operations |

## Data Policy

This skill **never stores data locally**. All requests go directly to the Render API and results are returned to stdout. Your data stays on Render servers.

## Credits
---
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
