---
name: token-optimizer-pro
description: "Monitor OpenClaw token usage, analyze usage patterns, estimate cost, and provide practical optimization suggestions. Use when reviewing token consumption by agent, model, session, or time range, or when trying to reduce cost without losing useful output quality."
---

# Token Optimizer Pro

Monitor OpenClaw token usage and turn the data into actionable optimization guidance.

## What It Helps With

- track token usage across agents and models
- analyze usage trends over time
- estimate current and projected cost
- identify abnormal spikes or inefficient patterns
- generate concrete token-saving suggestions
- define alert thresholds for high usage

## Typical Commands

```bash
token-optimizer status
token-optimizer report
token-optimizer report --days 7
token-optimizer report --agent code
token-optimizer suggest
token-optimizer alert --daily-limit 100000
token-optimizer alert --session-limit 50000
```

## Example Questions

- Which agent is using the most tokens?
- Which model is the most expensive this week?
- Did usage spike yesterday?
- Where can I reduce token cost by 20%?

## Optimization Areas

- model selection
- context trimming
- session management
- tool usage efficiency
