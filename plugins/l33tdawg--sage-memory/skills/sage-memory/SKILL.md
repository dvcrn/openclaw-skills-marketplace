---
name: sage-memory
description: "Persistent institutional memory for AI agents — BFT consensus-validated, locally hosted, works with any MCP-compatible model"
homepage: https://l33tdawg.github.io/sage
---

# SAGE Memory — Give Your AI a Brain That Persists

SAGE (Sovereign Agent Governed Experience) is an open-source institutional memory layer for AI agents. Every memory goes through BFT consensus validation before it's committed — not a flat file, not a vector database with a search bar. Governed knowledge.

## What It Does

- **Persistent memory across sessions** — your AI remembers what worked, what didn't, and why
- **4 application validators** — Sentinel, Dedup, Quality, Consistency. 3/4 must accept (BFT quorum)
- **13 MCP tools** — sage_inception, sage_turn, sage_remember, sage_recall, sage_reflect, sage_forget, sage_list, sage_status, sage_timeline, sage_task, sage_backlog, sage_register, sage_red_pill
- **Works with any AI** — Claude, ChatGPT, Gemini, DeepSeek, or any MCP-compatible model
- **Runs locally** — no cloud, no API keys, your memories stay on your machine
- **Real consensus** — CometBFT under the hood, Ed25519 signed transactions, deterministic validator keys
- **CEREBRUM Dashboard** — real-time brain visualization, domain stats, memory detail, focus mode

## Quick Start

1. Download from [GitHub Releases](https://github.com/l33tdawg/sage/releases/latest) (macOS DMG, Windows installer, Linux tarball)
2. Run the setup wizard
3. Add the MCP config to your AI tool
4. Call `sage_inception` — your AI wakes up with persistent memory

## MCP Configuration

```json
{
  "mcpServers": {
    "sage": {
      "command": "sage-gui",
      "args": ["mcp"],
      "env": {}
    }
  }
}
```

## Research

Backed by 4 published papers. Key result: agents with SAGE memory achieve Spearman rho=0.716 learning improvement over sequential runs. Without memory: rho=0.040.

- Paper 1: Agent Memory Infrastructure (Byzantine-Resilient Institutional Memory)
- Paper 2: Consensus-Validated Memory Improves Agent Performance
- Paper 3: Institutional Memory as Organizational Knowledge
- Paper 4: Longitudinal Learning in Governed Multi-Agent Systems

## Links

- GitHub: https://github.com/l33tdawg/sage
- Landing Page: https://l33tdawg.github.io/sage
- Author: Dhillon Andrew Kannabhiran (@l33tdawg)
- License: Apache 2.0
