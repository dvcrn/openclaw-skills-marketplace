---
name: railway
description: "Railway deployment platform — projects, services, deployments, variables. App hosting CLI."
homepage: https://www.agxntsix.ai
---

# 🚂 Railway

App deployment — projects, services, deployments, and variables.

## Features

- **Projects** — create, list, get
- **Services** — list project services
- **Deployments** — view deployment status
- **Variables** — manage env vars

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `RAILWAY_API_TOKEN` | ✅ | API key/token for Railway |

## Quick Start

```bash
python3 {baseDir}/scripts/railway.py projects
python3 {baseDir}/scripts/railway.py project <id>
python3 {baseDir}/scripts/railway.py services <project-id>
python3 {baseDir}/scripts/railway.py me
```

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
