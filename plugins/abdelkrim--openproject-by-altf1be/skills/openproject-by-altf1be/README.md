# openclaw-skill-openproject

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/Node.js-%3E%3D18-green.svg)](https://nodejs.org/)
[![OpenProject](https://img.shields.io/badge/OpenProject-API%20v3-blue.svg)](https://www.openproject.org/)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-orange.svg)](https://clawhub.ai)
[![ClawHub](https://img.shields.io/badge/ClawHub-openproject--by--altf1be-orange)](https://clawhub.ai/skills/openproject-by-altf1be)
[![GitHub last commit](https://img.shields.io/github/last-commit/ALT-F1-OpenClaw/openclaw-skill-openproject)](https://github.com/ALT-F1-OpenClaw/openclaw-skill-openproject/commits/main)
[![GitHub issues](https://img.shields.io/github/issues/ALT-F1-OpenClaw/openclaw-skill-openproject)](https://github.com/ALT-F1-OpenClaw/openclaw-skill-openproject/issues)
[![GitHub stars](https://img.shields.io/github/stars/ALT-F1-OpenClaw/openclaw-skill-openproject)](https://github.com/ALT-F1-OpenClaw/openclaw-skill-openproject/stargazers)

OpenClaw skill for OpenProject — CRUD work packages, projects, time entries, comments, attachments, and more via OpenProject API v3. Supports both cloud and self-hosted instances.

By [Abdelkrim BOUJRAF](https://www.alt-f1.be) / ALT-F1 SRL, Brussels 🇧🇪 🇲🇦

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Setup](#setup)
- [Commands](#commands)
- [Security](#security)
- [ClawHub](#clawhub)
- [License](#license)
- [Author](#author)
- [Contributing](#contributing)

## Features

- **Work Packages** — Create, read, update, delete, list with filters (status, assignee, type)
- **Projects** — List, read, create
- **Comments** — List and add comments on work packages
- **Attachments** — List, upload, and delete
- **Time Entries** — CRUD time tracking with hours, dates, and activity types
- **Statuses & Transitions** — List statuses, update work package status
- **Reference Data** — Types, priorities, members, versions, categories
- **Security** — `--confirm` required for deletes, no secrets to stdout, rate-limit retry with backoff
- **Auth** — API token (works with cloud and self-hosted)

## Quick Start

```bash
# 1. Clone
git clone https://github.com/ALT-F1-OpenClaw/openclaw-skill-openproject.git
cd openclaw-skill-openproject

# 2. Install
npm install

# 3. Configure
cp .env.example .env
# Edit .env with your OpenProject URL and API token

# 4. Use
node scripts/openproject.mjs project-list
node scripts/openproject.mjs wp-list --project my-project
node scripts/openproject.mjs wp-create --project my-project --subject "My first task"
```

## Setup

1. Log in to your OpenProject instance
2. Go to **My Account → Access Tokens → + Add**
3. Create an API token and copy it
4. Copy `.env.example` to `.env` and fill in:
   - `OP_HOST` — your OpenProject URL (e.g. `https://projects.xflowdata.com`)
   - `OP_API_TOKEN` — the API token you just created
   - `OP_DEFAULT_PROJECT` — (optional) default project identifier

## Commands

See [SKILL.md](./SKILL.md) for full command reference.

### 27 commands across 7 entities:

| Entity | Commands |
|--------|----------|
| Work Packages | `wp-list`, `wp-create`, `wp-read`, `wp-update`, `wp-delete` |
| Projects | `project-list`, `project-read`, `project-create` |
| Comments | `comment-list`, `comment-add` |
| Attachments | `attachment-list`, `attachment-add`, `attachment-delete` |
| Time Entries | `time-list`, `time-create`, `time-update`, `time-delete` |
| Statuses/Transitions | `status-list` + `wp-update --status` |
| Reference Data | `type-list`, `priority-list`, `member-list`, `version-list`, `category-list` |

## Security

- API token auth (Basic auth with `apikey` as username)
- No secrets or tokens printed to stdout
- All delete operations require explicit `--confirm` flag
- Path traversal prevention for file uploads
- Built-in rate limiting with exponential backoff retry
- Lazy config validation (only checked when a command runs)

## ClawHub

Published as: `openproject-by-altf1be`

```bash
clawhub install openproject-by-altf1be
```

## License

MIT — see [LICENSE](./LICENSE)

## Author

Abdelkrim BOUJRAF — [ALT-F1 SRL](https://www.alt-f1.be), Brussels 🇧🇪 🇲🇦
- GitHub: [@abdelkrim](https://github.com/abdelkrim)
- X: [@altf1be](https://x.com/altf1be)

## Contributing

Contributions welcome! Please open an issue or PR.
