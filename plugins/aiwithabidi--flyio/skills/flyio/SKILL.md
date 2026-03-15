---
name: flyio
description: "Fly.io edge deployment platform — manage apps, machines, volumes, secrets, and certificates via the Fly.io Machines API. Deploy containers globally, scale to zero, manage persistent storage, and configure networking. Built for AI agents — Python stdlib only, zero dependencies. Use for edge deployment, container management, global distribution, serverless scaling, and infrastructure automation."
homepage: https://www.agxntsix.ai
---

# ✈️ Fly.io

Fly.io edge deployment platform — manage apps, machines, volumes, secrets, and certificates via the Fly.io Machines API.

## Features

- **App management** — create, list, configure apps
- **Machine operations** — start, stop, restart machines
- **Volume management** — persistent storage provisioning
- **Secret management** — secure environment secrets
- **Certificate management** — SSL/TLS auto-provisioning
- **Scaling** — scale machines up/down, auto-stop
- **Region selection** — deploy to specific global regions
- **Health checks** — monitor machine health
- **Network config** — IP allocation, private networking
- **Deployment** — rolling deploys with canary support

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `FLY_API_TOKEN` | ✅ | API key/token for Fly.io |

## Quick Start

```bash
# List apps
python3 {baseDir}/scripts/flyio.py apps --limit 20
```

```bash
# Get app details
python3 {baseDir}/scripts/flyio.py app-get my-app
```

```bash
# Create an app
python3 {baseDir}/scripts/flyio.py app-create '{"app_name":"my-service","org_slug":"personal"}'
```

```bash
# List machines
python3 {baseDir}/scripts/flyio.py machines --app my-app
```



## Commands

### `apps`
List apps.
```bash
python3 {baseDir}/scripts/flyio.py apps --limit 20
```

### `app-get`
Get app details.
```bash
python3 {baseDir}/scripts/flyio.py app-get my-app
```

### `app-create`
Create an app.
```bash
python3 {baseDir}/scripts/flyio.py app-create '{"app_name":"my-service","org_slug":"personal"}'
```

### `machines`
List machines.
```bash
python3 {baseDir}/scripts/flyio.py machines --app my-app
```

### `machine-get`
Get machine details.
```bash
python3 {baseDir}/scripts/flyio.py machine-get --app my-app mach_abc123
```

### `machine-start`
Start a machine.
```bash
python3 {baseDir}/scripts/flyio.py machine-start --app my-app mach_abc123
```

### `machine-stop`
Stop a machine.
```bash
python3 {baseDir}/scripts/flyio.py machine-stop --app my-app mach_abc123
```

### `machine-create`
Create a machine.
```bash
python3 {baseDir}/scripts/flyio.py machine-create --app my-app '{"config":{"image":"nginx:latest","guest":{"cpus":1,"memory_mb":256}}}'
```

### `volumes`
List volumes.
```bash
python3 {baseDir}/scripts/flyio.py volumes --app my-app
```

### `volume-create`
Create a volume.
```bash
python3 {baseDir}/scripts/flyio.py volume-create --app my-app '{"name":"data","size_gb":10,"region":"ord"}'
```

### `secrets`
List secrets.
```bash
python3 {baseDir}/scripts/flyio.py secrets --app my-app
```

### `secret-set`
Set a secret.
```bash
python3 {baseDir}/scripts/flyio.py secret-set --app my-app "DATABASE_URL" "postgres://..."
```

### `certs`
List certificates.
```bash
python3 {baseDir}/scripts/flyio.py certs --app my-app
```

### `regions`
List available regions.
```bash
python3 {baseDir}/scripts/flyio.py regions
```

### `status`
App status overview.
```bash
python3 {baseDir}/scripts/flyio.py status --app my-app
```


## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
# JSON (default, for programmatic use)
python3 {baseDir}/scripts/flyio.py apps --limit 5

# Human-readable
python3 {baseDir}/scripts/flyio.py apps --limit 5 --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/flyio.py` | Main CLI — all Fly.io operations |

## Data Policy

This skill **never stores data locally**. All requests go directly to the Fly.io API and results are returned to stdout. Your data stays on Fly.io servers.

## Credits
---
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
