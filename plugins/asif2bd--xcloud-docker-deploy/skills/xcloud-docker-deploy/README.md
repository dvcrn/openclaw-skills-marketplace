# xCloud Docker Deploy Skill

> **For AI Agents:** Auto-detect any project stack and deploy it to [xCloud](https://xcloud.host) — native or Docker path, zero config required.

[![Version](https://img.shields.io/badge/version-1.2.0-blue)](https://github.com/Asif2BD/xCloud-Docker-Deploy-Skill/releases)
[![License](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)
[![SkillsMP](https://img.shields.io/badge/SkillsMP-listed-purple)](https://skillsmp.com)
[![ClawHub](https://img.shields.io/badge/ClawHub-published-orange)](https://clawhub.ai/Asif2BD/xcloud-docker-deploy)
[![Platforms](https://img.shields.io/badge/platforms-Claude%20Code%20%7C%20Codex%20%7C%20OpenClaw%20%7C%20Cursor-lightgrey)](#install)

---

## What It Does

Paste a project structure or `docker-compose.yml` and ask the AI to deploy it on xCloud. The skill:

1. **Detects your stack** — WordPress, Laravel, PHP, Node.js, Next.js, NestJS, Nuxt, Python, Go, Rust, or existing Docker
2. **Picks the right path** — xCloud Native deploy vs Docker
3. **Generates all files** — Dockerfile, docker-compose.yml, GitHub Actions CI/CD, .env.example
4. **Gives exact xCloud UI steps** — copy-paste ready

### What It Handles

| Scenario | Signal | Fix |
|----------|--------|-----|
| **Stack detection** | Any project files | Auto-routes to native or Docker path |
| **Build-from-source** | `build: context: .` in compose | GitHub Actions → GHCR; replaces `build:` with `image:` |
| **Proxy conflict** | Caddy/Traefik/nginx-proxy service | Removes it, adds embedded nginx-router |
| **Multi-port** | Multiple `ports:` on different services | Routes through nginx-router, single exposed port |
| **External config** | `./nginx.conf:/etc/nginx/...` | Embeds config inline via `configs:` block |
| **No Docker at all** | WordPress/Laravel/Node.js project | Native xCloud deploy guide |

---

## Install

### Claude Code (CLI)
```bash
# From ClawHub
clawhub install xcloud-docker-deploy

# Or manually
git clone https://github.com/Asif2BD/xCloud-Docker-Deploy-Skill.git
cp -r xCloud-Docker-Deploy-Skill ~/.claude/skills/xcloud-docker-deploy
```

### OpenAI Codex CLI
```bash
git clone https://github.com/Asif2BD/xCloud-Docker-Deploy-Skill.git
cp -r xCloud-Docker-Deploy-Skill ~/.codex/skills/xcloud-docker-deploy
```

### OpenClaw Agent
Drop the skill folder into your agent's `skills/` workspace directory.

### Claude.ai (Projects)
Upload `SKILL.md` to your Project files. The AI will use it as context automatically.

### Cursor / Windsurf / Any AI IDE
Add `SKILL.md` contents to your system prompt or project rules file.

---

## Usage

Once installed, just describe what you want:

```
"Make this docker-compose.yml work on xCloud"
"Deploy my Laravel app to xCloud"
"My Next.js app needs to run on xCloud, help me set it up"
"Convert this Caddy + React + API stack for xCloud"
```

The agent reads DETECT.md first, identifies your stack, then follows the appropriate guide.

---

## Supported Stacks

| Stack | Deploy Path | Files Provided |
|-------|-------------|----------------|
| WordPress | xCloud Native | Step-by-step UI guide |
| Laravel | xCloud Native | Deploy hooks, queue worker config |
| PHP (generic) | xCloud Native | Web root config, Composer hooks |
| Node.js / Express | xCloud Native | PORT env setup |
| Next.js | Docker | `dockerfiles/nextjs.Dockerfile` + `compose-templates/nextjs-postgres.yml` |
| NestJS | Docker | Generated Dockerfile + compose |
| Python / FastAPI | Docker | `dockerfiles/python-fastapi.Dockerfile` + compose with Celery |
| Go | Docker | Generated Dockerfile + compose |
| Existing Docker | Adapt | Scenario A/B/C transformation |

---

## Skill Structure

```
xcloud-docker-deploy/
├── SKILL.md                          ← Main skill instructions (load this)
├── DETECT.md                         ← Stack fingerprinting rules
├── references/
│   ├── xcloud-constraints.md         ← Platform rules (must-read)
│   ├── xcloud-deploy-paths.md        ← Native vs Docker decision matrix
│   ├── xcloud-native-wordpress.md    ← WordPress deploy guide
│   ├── xcloud-native-laravel.md      ← Laravel deploy guide
│   ├── xcloud-native-nodejs.md       ← Node.js deploy guide
│   ├── xcloud-native-php.md          ← PHP deploy guide
│   ├── scenario-build-source.md      ← Scenario A deep-dive
│   ├── scenario-proxy-conflict.md    ← Scenario B deep-dive
│   └── scenario-multi-service-build.md ← Scenario C deep-dive
├── dockerfiles/
│   ├── laravel.Dockerfile            ← PHP 8.3-fpm-alpine, multi-stage
│   ├── nextjs.Dockerfile             ← 3-stage standalone build
│   ├── node-app.Dockerfile           ← Node 20-alpine, non-root
│   ├── php-generic.Dockerfile        ← PHP 8.3-apache + mod_rewrite
│   └── python-fastapi.Dockerfile     ← Python 3.12-slim + uvicorn
├── compose-templates/
│   ├── laravel-mysql.yml             ← PHP-FPM + nginx + MySQL + Redis
│   ├── nextjs-postgres.yml           ← Next.js + PostgreSQL
│   ├── nodejs-api-postgres.yml       ← Node API + PostgreSQL
│   └── python-fastapi-postgres.yml   ← FastAPI + PostgreSQL + Celery
├── assets/
│   └── github-actions-build.yml      ← GitHub Actions GHCR build workflow
└── examples/
    ├── rybbit-analytics.md           ← Caddy + multi-port (Scenario B)
    ├── custom-app-dockerfile.md      ← Build-from-source (Scenario A)
    ├── fullstack-monorepo.md         ← Multi-service (Scenario C)
    ├── laravel-app.md                ← Laravel native deploy
    └── nextjs-app.md                 ← Next.js Docker deploy
```

---

## About xCloud

[xCloud](https://xcloud.host) is a git-push Docker deployment platform. Push your repo, xCloud runs `docker-compose pull && docker-compose up -d`. It handles SSL, reverse proxy, and domain routing automatically — your stack must not duplicate those.

---

## Author

**M Asif Rahman** — [@Asif2BD](https://github.com/Asif2BD)

- ClawHub: [clawhub.ai/Asif2BD/xcloud-docker-deploy](https://clawhub.ai/Asif2BD/xcloud-docker-deploy)
- SkillsMP: [skillsmp.com](https://skillsmp.com)

---

## License

Apache 2.0 — free to use, modify, and distribute.
