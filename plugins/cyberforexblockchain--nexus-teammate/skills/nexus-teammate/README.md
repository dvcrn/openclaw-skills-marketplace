# nexus-teammate

**NEXUS AI Teammate** — A versatile AI partner that adapts to any task — data analysis, debugging, brainstorming, writing, code review, or research. Maintains context across a conversation session.

Part of the [NEXUS Agent-as-a-Service Platform](https://ai-service-hub-15.emergent.host) on Cardano.

## Installation

```bash
clawhub install nexus-teammate
```

## Quick Start

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/teammate \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"task": "Help me design a database schema for a marketplace that supports both fixed-price and auction listings", "task_type": "architecture"}'
```

## Why nexus-teammate?

Unlike single-purpose services, Teammate maintains conversation context via session_id. It can pivot between tasks, remember earlier decisions, and provide holistic advice across multiple turns.

## Pricing

- Pay-per-request in ADA via Masumi Protocol (Cardano non-custodial escrow)
- Free sandbox available with `X-Payment-Proof: sandbox_test`

## Links

- Platform: [https://ai-service-hub-15.emergent.host](https://ai-service-hub-15.emergent.host)
- All Skills: [https://ai-service-hub-15.emergent.host/.well-known/skill.md](https://ai-service-hub-15.emergent.host/.well-known/skill.md)
