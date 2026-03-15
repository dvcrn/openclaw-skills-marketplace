---
name: neon
description: "Neon serverless Postgres — manage projects, branches, databases, roles, endpoints, and compute via the Neon API. Create database branches for development, manage connection endpoints, scale compute, and monitor usage. Built for AI agents — Python stdlib only, zero dependencies. Use for serverless Postgres, database branching, database management, development workflows, and cloud database automation."
homepage: https://www.agxntsix.ai
---

# 💚 Neon

Neon serverless Postgres — manage projects, branches, databases, roles, endpoints, and compute via the Neon API.

## Features

- **Project management** — create, list, delete projects
- **Branch management** — create, restore, delete branches
- **Database operations** — create and manage databases
- **Role management** — database users and permissions
- **Endpoint management** — connection endpoints and pooling
- **Compute scaling** — auto-suspend, compute size control
- **Connection strings** — generate connection URIs
- **Operations history** — track async operations
- **Consumption metrics** — compute hours, storage, transfer
- **Branch restore** — point-in-time restore from history

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `NEON_API_KEY` | ✅ | API key/token for Neon |

## Quick Start

```bash
# List projects
python3 {baseDir}/scripts/neon.py projects --limit 20
```

```bash
# Get project details
python3 {baseDir}/scripts/neon.py project-get proj-abc123
```

```bash
# Create a project
python3 {baseDir}/scripts/neon.py project-create '{"project":{"name":"my-app","region_id":"aws-us-east-1"}}'
```

```bash
# Delete a project
python3 {baseDir}/scripts/neon.py project-delete proj-abc123
```



## Commands

### `projects`
List projects.
```bash
python3 {baseDir}/scripts/neon.py projects --limit 20
```

### `project-get`
Get project details.
```bash
python3 {baseDir}/scripts/neon.py project-get proj-abc123
```

### `project-create`
Create a project.
```bash
python3 {baseDir}/scripts/neon.py project-create '{"project":{"name":"my-app","region_id":"aws-us-east-1"}}'
```

### `project-delete`
Delete a project.
```bash
python3 {baseDir}/scripts/neon.py project-delete proj-abc123
```

### `branches`
List branches.
```bash
python3 {baseDir}/scripts/neon.py branches --project proj-abc123
```

### `branch-create`
Create a branch.
```bash
python3 {baseDir}/scripts/neon.py branch-create --project proj-abc123 '{"branch":{"name":"dev","parent_id":"br-main"}}'
```

### `branch-delete`
Delete a branch.
```bash
python3 {baseDir}/scripts/neon.py branch-delete --project proj-abc123 br-dev
```

### `branch-restore`
Restore branch to point in time.
```bash
python3 {baseDir}/scripts/neon.py branch-restore --project proj-abc123 br-main --timestamp '2026-02-01T00:00:00Z'
```

### `databases`
List databases.
```bash
python3 {baseDir}/scripts/neon.py databases --project proj-abc123 --branch br-main
```

### `database-create`
Create database.
```bash
python3 {baseDir}/scripts/neon.py database-create --project proj-abc123 --branch br-main '{"database":{"name":"mydb","owner_name":"neondb_owner"}}'
```

### `roles`
List roles.
```bash
python3 {baseDir}/scripts/neon.py roles --project proj-abc123 --branch br-main
```

### `endpoints`
List endpoints.
```bash
python3 {baseDir}/scripts/neon.py endpoints --project proj-abc123
```

### `connection-string`
Get connection string.
```bash
python3 {baseDir}/scripts/neon.py connection-string --project proj-abc123 --branch br-main --database mydb
```

### `consumption`
Get consumption metrics.
```bash
python3 {baseDir}/scripts/neon.py consumption --from 2026-01-01 --to 2026-02-01
```

### `operations`
List operations.
```bash
python3 {baseDir}/scripts/neon.py operations --project proj-abc123 --limit 10
```


## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
# JSON (default, for programmatic use)
python3 {baseDir}/scripts/neon.py projects --limit 5

# Human-readable
python3 {baseDir}/scripts/neon.py projects --limit 5 --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/neon.py` | Main CLI — all Neon operations |

## Data Policy

This skill **never stores data locally**. All requests go directly to the Neon API and results are returned to stdout. Your data stays on Neon servers.

## Credits
---
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
