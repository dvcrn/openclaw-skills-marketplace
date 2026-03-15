# MusiClaw — OpenClaw Skill Setup

## How the Suno cookie works (no more pasting keys in chat!)

```
┌─────────────────────────────────────────────────────────┐
│  Agent stores suno_cookie via update-agent-settings      │
│  ┌───────────────────────────────────┐                  │
│  │ suno_cookie: "session=abc..."─────┼──┐               │
│  │ (from Suno Pro/Premier)           │  │               │
│  └───────────────────────────────────┘  │               │
│                                         ▼               │
│  MusiClaw stores cookie securely per-agent              │
│                                         │               │
│  Agent generates ──► suno_cookie sent as header         │
│  (never in prompt, never logged)                        │
└─────────────────────────────────────────────────────────┘
```

## Install (3 steps)

### 1. Copy skill to your agent's workspace

```bash
# Into your agent's workspace (per-agent)
cp -r skills/musiclaw <workspace>/skills/musiclaw

# OR into shared skills (all agents on this machine)
cp -r skills/musiclaw ~/.openclaw/skills/musiclaw
```

### 2. Store your Suno cookie

During the first conversation, the agent will ask for your Suno Pro/Premier cookie. It stores it securely via the `update-agent-settings` endpoint.

To get your cookie: Log into suno.com → DevTools (F12) → Application → Cookies → copy the cookie value.

**Suno Pro or Premier plan is required** for commercial licensing rights. Free plan cookies will be rejected.

### 3. Start a new session

The skill loads on session start. Your agent will see MusiClaw in its available skills and can immediately start making beats.

## What changed from the legacy approach

| | Legacy (manual) | OpenClaw Skill |
|---|---|---|
| **Suno cookie** | Human pastes in chat | Stored securely via update-agent-settings |
| **Cookie security** | Visible in prompts/logs | Never in conversation |
| **Loading** | Copy-paste instructions each session | Auto-loaded on session start |
| **Updates** | Manual re-paste | Edit SKILL.md, auto-reloads (watcher) |
| **Multi-agent** | Must paste for each agent | Shared via `~/.openclaw/skills` or per-workspace |

## Gating

The skill requires:
- A registered MusiClaw agent with stored `suno_cookie`
- `curl` — must be on PATH (used for all API calls)

If either is missing, the agent will guide you through setup.

## Verify it's working

Start a session and ask your agent:

> "What skills do you have?"

It should list **musiclaw** with the 🦞 emoji. Then:

> "Make me a beat"

The agent will use the stored Suno cookie automatically without ever asking you for it.
