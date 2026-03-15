---
name: cognitive-recall
description: "Cross-session memory recall via Cognitive Brain - injects user context from PostgreSQL memory store"
metadata:
  {
    "openclaw":
      {
        "emoji": "🧠",
        "events": ["message:preprocessed"],
        "requires": { "bins": ["node"] }
      }
  }
---

# Cognitive Recall Hook

Automatically recalls user context from Cognitive Brain's PostgreSQL memory store when processing messages, enabling cross-session memory continuity.

## What It Does

1. Triggers on every inbound message after preprocessing
2. Queries Cognitive Brain for user preferences, important facts, recent episodes
3. Injects memory context into the message for the agent to see

## Requirements

- Cognitive Brain skill must be installed
- PostgreSQL must be running with `cognitive_brain` database
- Redis (optional, for caching)

## Configuration

The hook reads Cognitive Brain's config from:
`~/.openclaw/workspace/skills/cognitive-brain/config.json`

Default connection:
- PostgreSQL: localhost:5432/cognitive_brain
- User: postgres
- Password: cognitive123
