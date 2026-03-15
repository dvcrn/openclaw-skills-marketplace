---
name: grantai-memory
description: "GrantAi Memory"
---

# GrantAi Memory

Give your OpenClaw agents persistent memory that works across sessions. GrantAi uses exact-recall architecture (not RAG/vectors) for sub-second retrieval, 100% local with AES-256 encryption.

## Setup

Install GrantAi:

```bash
curl -fsSL https://solonai.com/install.sh | bash
```

Add to mcporter:

```bash
mcporter config add grantai ~/.grantai/bin/grantai-mcp
mcporter tools grantai
```

## skill.json Example

```json
{
  "name": "research-assistant",
  "mcpServers": ["grantai"],
  "systemPrompt": "You have persistent memory via GrantAi. Query grantai_infer before searching files."
}
```

## Available Tools

- **grantai_infer** — Query memory. Use before searching files or re-reading context.
- **grantai_teach** — Store facts, decisions, and learnings for future sessions.
- **grantai_learn** — Import files or code into memory.
- **grantai_summarize** — Save a session summary before ending.
- **grantai_project** — Track project state across sessions.
- **grantai_snippet** — Save reusable code patterns.

## When to Use Each Tool

| Situation | Tool |
|---|---|
| Starting a session | `grantai_infer` — check what's already known |
| User corrects or updates facts | `grantai_teach` |
| Onboarding a new codebase | `grantai_learn` |
| End of session | `grantai_summarize` |
| Tracking feature/sprint state | `grantai_project` |
| Reusable code pattern found | `grantai_snippet` |

## Multi-Agent Coordination

Agents share memory automatically — a researcher, writer, and reviewer agent can all read and write the same GrantAi brain without extra configuration.

## Notes

- 30-day free trial, no credit card needed.
- Docs: https://solonai.com/grantai/integrations/openclaw
- Support: support@solonai.com
