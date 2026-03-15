# ClawOnBoarding 🦞

Welcome new humans to the agent world.

## What it teaches

1. **Agent capabilities** — What agents can do (files, web, commands, email)
2. **Safety practices** — Power comes with responsibility
3. **ClawdHub & Skills** — How to extend agent abilities
4. **Solvr** — Collective knowledge for agents
5. **Essential commands** — `/think`, `/status`, `/remember`
6. **AgentMail** — Agent-to-agent communication
7. **Memory & Continuity** — How agents remember

## Installation

```bash
clawdhub install claw-onboarding
```

## Usage

The skill auto-triggers on:
- First interaction with new user
- "What can you do?"
- "Help me get started"
- Explicit: "onboarding", "tutorial"

## Adaptive Delivery

- Doesn't dump everything at once
- Tracks progress in `memory/onboarding-state.json`
- Supports inline buttons when available

## Integration

Works with:
- `proactive-amcp` — Mentions checkpoints if installed
- `Solvr` — Encourages knowledge sharing
- `AgentMail` — Shows email if configured

---

*Part of the MeuSecretárioVirtual ecosystem*
