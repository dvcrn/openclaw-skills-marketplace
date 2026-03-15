# prompt-token-counter

[中文](README.zh.md)

An **OpenClaw skill** for counting tokens and estimating API costs.

## What This Skill Does

When loaded, the agent can:

| Capability | Use case |
|------------|----------|
| **Count tokens** | "How many tokens in this prompt?", "Token length of X" |
| **Estimate cost** | "How much for this text on GPT-4?", "API cost for Claude" |
| **Audit OpenClaw workspace** | "How many tokens does my workspace use?", "Which memory/persona/skills consume tokens?" |
| **Compare models** | "Compare token cost across models", "Which model is cheaper?" |

### OpenClaw Token Audit

The skill helps identify token consumption of workspace components:

- **Memory & persona**: AGENTS.md, SOUL.md, IDENTITY.md, USER.md, MEMORY.md, TOOLS.md, etc.
- **Skills**: Each SKILL.md under `~/.openclaw/skills/` or `workspace/skills/`

Example audit:
```bash
python -m scripts.cli -m gpt-4o -c -f AGENTS.md -f SOUL.md -f MEMORY.md
```

## When to Trigger

- User asks about token count, prompt length, API cost
- User mentions OpenClaw context size or workspace token usage
- Agent needs to audit token consumption before/after changes

## Quick Reference

```bash
python -m scripts.cli -m gpt-4 "Hello, world!"
python -m scripts.cli -f input.txt -m claude-3-opus -c
python -m scripts.cli -l   # list 300+ models
```

MIT
