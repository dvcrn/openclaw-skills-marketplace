#!/usr/bin/env python3
"""Generate the reverse-direction Antigravity skill for OpenClaw delegation.

Creates .agent/skills/openclaw-bridge/SKILL.md in your project, teaching
Antigravity how to delegate tasks to OpenClaw agents.
"""
# SECURITY MANIFEST:
# Environment variables accessed: HOME (only)
# External endpoints called: none
# Local files read: ~/.openclaw/antigravity-bridge.json
# Local files written: <project>/.agent/skills/openclaw-bridge/SKILL.md

import json
import os
import sys
from pathlib import Path

CONFIG_PATH = os.path.expanduser("~/.openclaw/antigravity-bridge.json")

SKILL_MD = '''---
description: >-
  Delegate tasks to OpenClaw agents running on the same machine.
  Use when: (1) you need background work done while continuing your session,
  (2) tasks that don't require IDE access (monitoring, notifications, API calls),
  (3) parallel coding via Claude Code sub-agents,
  (4) cross-system knowledge sync,
  (5) user says "delegate to openclaw", "send to clawd", or "background task".
---

# OpenClaw Bridge

Delegate tasks to OpenClaw agents for parallel or background execution.

## Quick Delegation

Send a task to OpenClaw via terminal:

```bash
curl -s http://localhost:18789/api/message \\
  -H "Content-Type: application/json" \\
  -d '{"message": "<task description>"}'
```

## File-Based Handoff

For complex tasks with context:

```bash
cat > ~/.openclaw/workspace/inbox/task-$(date +%s).md << 'TASK'
# Task from Antigravity

<detailed task description>

## Context
- Source: Antigravity session
- Branch: $(git branch --show-current)
- Priority: <high/medium/low>
- Related files: <list of files>

## Expected Output
- <what OpenClaw should produce>
TASK
```

OpenClaw picks up inbox tasks via heartbeat polling.

## Task Types to Delegate

| Task | Why OpenClaw? |
|---|---|
| Run E2E tests | Headless sub-agents, no IDE needed |
| Monitor deployment | Has Cloudflare + kubectl integrations |
| Send notifications | Telegram/email/Slack channels configured |
| Update docs | Parallel work while you code |
| Security audit | Healthcheck skill built-in |
| Sync knowledge | Updates both agent systems |
| Research | Web search + Context7 + browser relay |

## Triggering Knowledge Sync

Sync both Antigravity and OpenClaw knowledge:

```bash
curl -s http://localhost:18789/api/message \\
  -H "Content-Type: application/json" \\
  -d '{"message": "Run antigravity bridge self-improve"}'
```

## Receiving Results

OpenClaw writes results to:
- `.agent/sessions/openclaw-result-<timestamp>.md` (for next Antigravity session)
- `.agent/memory/lessons-learned-*.md` (if learnings captured)
- Telegram notification to the user (if configured)

## When NOT to Delegate

- Tasks requiring IDE UI interaction (use Antigravity directly)
- Tasks needing Antigravity's Gemini model specifically
- Quick edits that are faster to do in-session
'''


def main():
    config_path = CONFIG_PATH
    if not os.path.exists(config_path):
        print(f"Error: Config not found at {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    # Create in project's .agent/skills/
    agent_dir = Path(os.path.expanduser(config["agent_dir"]))
    skill_dir = agent_dir / "skills" / "openclaw-bridge"
    skill_dir.mkdir(parents=True, exist_ok=True)

    skill_path = skill_dir / "SKILL.md"
    skill_path.write_text(SKILL_MD)
    print(f"✅ Antigravity skill created: {skill_path}")

    # Also create globally if knowledge dir exists
    knowledge_dir = Path(os.path.expanduser(config["knowledge_dir"]))
    if knowledge_dir.exists():
        global_skill_dir = knowledge_dir.parent / "skills" / "openclaw-bridge"
        global_skill_dir.mkdir(parents=True, exist_ok=True)
        global_skill_path = global_skill_dir / "SKILL.md"
        global_skill_path.write_text(SKILL_MD)
        print(f"✅ Global skill created: {global_skill_path}")

    print("\\n🌉 Antigravity can now delegate tasks to OpenClaw!")
    print("   Use in Antigravity: 'delegate this to OpenClaw' or run the curl command.")


if __name__ == "__main__":
    main()
