---
name: terraform-cloud
description: "Terraform Cloud — manage workspaces, runs, plans, state, and variables via REST API"
homepage: https://www.agxntsix.ai
---

# 🏗️ Terraform Cloud

Terraform Cloud — manage workspaces, runs, plans, state, and variables via REST API

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `TFC_TOKEN` | ✅ | API token from app.terraform.io |
| `TFC_ORG` | ✅ | Organization name |

## Quick Start

```bash
# List organizations
python3 {{baseDir}}/scripts/terraform-cloud.py orgs

# List workspaces
python3 {{baseDir}}/scripts/terraform-cloud.py workspaces --search[name] <value>

# Get workspace
python3 {{baseDir}}/scripts/terraform-cloud.py workspace-get id <value>

# Create workspace
python3 {{baseDir}}/scripts/terraform-cloud.py workspace-create --name <value> --auto-apply <value> --terraform-version <value>

# Delete workspace
python3 {{baseDir}}/scripts/terraform-cloud.py workspace-delete id <value>

# Lock workspace
python3 {{baseDir}}/scripts/terraform-cloud.py workspace-lock id <value> --reason <value>

# Unlock workspace
python3 {{baseDir}}/scripts/terraform-cloud.py workspace-unlock id <value>

# List runs
python3 {{baseDir}}/scripts/terraform-cloud.py runs id <value>
```

## All Commands

| Command | Description |
|---------|-------------|
| `orgs` | List organizations |
| `workspaces` | List workspaces |
| `workspace-get` | Get workspace |
| `workspace-create` | Create workspace |
| `workspace-delete` | Delete workspace |
| `workspace-lock` | Lock workspace |
| `workspace-unlock` | Unlock workspace |
| `runs` | List runs |
| `run-get` | Get run |
| `run-create` | Create run |
| `run-apply` | Apply run |
| `run-discard` | Discard run |
| `run-cancel` | Cancel run |
| `plan-get` | Get plan |
| `state-version` | Get current state |
| `variables` | List variables |
| `variable-create` | Create variable |
| `variable-delete` | Delete variable |
| `teams` | List teams |

## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
python3 {{baseDir}}/scripts/terraform-cloud.py <command> --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{{baseDir}}/scripts/terraform-cloud.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
