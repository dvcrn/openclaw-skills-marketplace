---
name: wip-ldm-os
description: "LDM OS ... shared infrastructure for AI agents. Identity, memory, ownership, collaboration, compatibility, payments. One system across all your AIs."
---

# LDM OS

You use Claude Code, GPT, OpenClaw, others. They don't share memory. They don't know each other. They don't know how to work together.

LDM OS is the shared infrastructure layer. Install it once and every AI you use gets:

- **Identity** ... each AI gets its own behavior, personality, and skills
- **Memory** ... shared memory across all your AIs, secure, sovereign, yours to take anywhere
- **Ownership** ... every interaction, every memory, across every AI you use is yours, portable, encrypted, never locked in
- **Collaboration** ... your AIs communicate, share tools, and work together
- **Compatibility** ... any skill, plugin, or tool works with all your AIs. Install once, use everywhere.
- **Payments** ... your AI hits a paywall, you approve it with Face ID, Apple Pay for your AI

## Platform Compatibility

| Interface | Requires | Examples |
|-----------|----------|----------|
| CLI | Shell access (run bash/node commands) | `ldm init`, `ldm install`, `ldm doctor` |
| Skill | SKILL.md file (works in Claude Code and OpenClaw) | You're reading it right now |

**Built and tested on:**
- **Claude Code CLI** ... full support (shell, CLI)
- **OpenClaw** ... full support (shell, CLI)

## Operating Rules

**Always dry-run first.** Before installing or making changes, run with `--dry-run` so the user can see exactly what will happen. Only proceed when the user explicitly says to.

**Never touch sacred data.** The installer never overwrites: crystal.db, agent data, secrets, state files. Code gets updated. Data stays.

## Install

### Step 1: Install LDM OS

```bash
npm install -g @wipcomputer/wip-ldm-os
ldm init --dry-run
```

Show the user the dry run output. Explain what it creates:
- `~/.ldm/extensions/` ... where tools and plugins live
- `~/.ldm/agents/` ... each AI gets its own identity, personality, and memory here
- `~/.ldm/memory/` ... shared memory across all your AIs
- `~/.ldm/state/` ... configuration and sync state

When the user approves:
```bash
ldm init
```

### Step 2: Install Skills

LDM OS ships with a skill catalog. Show the user what's available:

| Skill | What it is | Status |
|-------|-----------|--------|
| **Memory Crystal** (recommended) | Persistent memory. Search, capture, consolidation. | Stable |
| **AI DevOps Toolbox** | Release, deploy, license, repo management. | Stable |
| **1Password** | 1Password secrets for AI agents. | Stable |
| **Markdown Viewer** | Live markdown viewer for AI pair-editing. | Stable |
| **xAI Grok** | xAI Grok API. Search the web, search X, generate images. | Stable |
| **X Platform** | X Platform API. Read posts, search tweets, post, upload media. | Stable |
| **OpenClaw** | AI agent platform. Run AI agents 24/7 with identity, memory, and tool access. | Stable |
| **Dream Weaver Protocol** | Memory consolidation protocol for AI agents. | Stable |
| **Bridge** | Cross-platform agent bridge. Claude Code to OpenClaw communication. | Stable |

To install a skill:
```bash
ldm install wipcomputer/memory-crystal --dry-run
```

Show the dry run. When approved:
```bash
ldm install wipcomputer/memory-crystal
```

The installer detects what a repo supports (CLI, MCP Server, OpenClaw Plugin, Skill, CC Hook, Module) and deploys each interface to the right location automatically.

**Note:** Skills installed before LDM OS (via `crystal init`, `wip-install`, or manual setup) may not appear in the registry. Run `ldm install <org/repo>` to re-register them.

### Step 3: Verify

```bash
ldm doctor
```

This checks: LDM root exists, version.json valid, registry intact, all extensions deployed, hooks configured, MCP servers registered.

## Commands

| Command | What it does |
|---------|-------------|
| `ldm init` | Scaffold `~/.ldm/` and write version.json |
| `ldm install <org/repo>` | Clone, detect interfaces, deploy, register |
| `ldm install /path/to/repo` | Install from local path |
| `ldm install` | Update all registered extensions |
| `ldm doctor` | Check health of all extensions |
| `ldm status` | Show version and extension list |
| `ldm --version` | Show version |

All commands support `--dry-run` (preview changes) and `--json` (machine-readable output).

## Interface Detection

When you run `ldm install`, it automatically detects what a repo supports:

| Interface | How it's detected | Where it deploys |
|-----------|------------------|-----------------|
| CLI | `package.json` has `bin` entries | `npm install -g` |
| MCP Server | Has `mcp-server.mjs` or `mcp-server.js` | `claude mcp add --scope user` |
| OpenClaw Plugin | Has `openclaw.plugin.json` | `~/.ldm/extensions/` + `~/.openclaw/extensions/` |
| Skill | Has `SKILL.md` or `skills/` directory | `~/.openclaw/skills/` |
| CC Hook | Has `guard.mjs` or `claudeCode.hook` in package.json | `~/.claude/settings.json` |
| Module | Has `main` or `exports` in package.json | Importable via `node_modules` |

No manual configuration needed. Point it at a repo and it figures out the rest.

## Update

If LDM OS is already installed:

```bash
ldm status        # show current version and extensions
ldm install       # update all registered extensions
ldm doctor        # verify everything works
```

Updates deploy new code without touching data. crystal.db, agent files, secrets, and state are never overwritten.

## Part of LDM OS

LDM OS is the runtime. Skills plug into it:

- **Memory Crystal** ... `wipcomputer/memory-crystal`
- **AI DevOps Toolbox** ... `wipcomputer/wip-ai-devops-toolbox`
- **1Password** ... `wipcomputer/wip-1password`
- **Markdown Viewer** ... `wipcomputer/wip-markdown-viewer`
- **xAI Grok** ... `wipcomputer/wip-xai-grok`
- **X Platform** ... `wipcomputer/wip-xai-x`
- **OpenClaw** ... `openclaw/openclaw`
- **Dream Weaver Protocol** ... `wipcomputer/dream-weaver-protocol`
- **Bridge** ... `wipcomputer/wip-bridge`

Run `ldm install` anytime to add more skills.
