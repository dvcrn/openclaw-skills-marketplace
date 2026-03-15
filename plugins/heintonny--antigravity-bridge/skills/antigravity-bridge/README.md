# 🌉 Antigravity Bridge

**Bidirectional knowledge bridge between [OpenClaw](https://github.com/openclaw/openclaw) and [Google Antigravity IDE](https://antigravityide.org/).**

Two AI agents. One shared brain. Zero manual sync.

## What This Does

If you use **Antigravity** (Gemini) for coding and **OpenClaw** (any LLM) as your life/DevOps agent, this skill bridges their knowledge systems so both agents share context:

```
┌─────────────────────┐       ┌─────────────────────┐
│    Antigravity       │       │    OpenClaw          │
│    (Gemini)          │       │    (Any LLM)         │
│                      │       │                      │
│  knowledge/       ◄──┼───────┼──► MEMORY.md         │
│  .agent/tasks.md  ◄──┼───────┼──► coding sub-agents │
│  .agent/memory/   ◄──┼───────┼──► memory/*.md       │
│  .agent/sessions/ ◄──┼───────┼──► session handoffs   │
└─────────────────────┘       └─────────────────────┘
```

## Features

- **📥 Sync Knowledge** — Pull Antigravity's Knowledge Items, tasks, and lessons into OpenClaw
- **📋 Pick Tasks** — Let OpenClaw coding sub-agents pick up tasks from `.agent/tasks.md`
- **🔄 Cross-Agent Self-Improve** — Update both knowledge systems simultaneously
- **📝 Write Knowledge Items** — Write to Antigravity's native KI format programmatically
- **🌉 Reverse Bridge** — Auto-generate an Antigravity skill for delegating tasks to OpenClaw

## Install

### Via ClawHub (recommended)

```bash
clawhub install antigravity-bridge
```

### Manual

```bash
git clone https://github.com/heintonny/antigravity-bridge.git
cp -r antigravity-bridge ~/.openclaw/skills/
```

## Setup

```bash
python3 ~/.openclaw/skills/antigravity-bridge/scripts/configure.py
```

This creates `~/.openclaw/antigravity-bridge.json` pointing to your Antigravity knowledge directory and project.

## Usage

Talk to your OpenClaw agent naturally:

| You say | What happens |
|---|---|
| "Sync with Antigravity" | Pulls all KIs, tasks, memory into context |
| "Pick up next task" | Selects a `[ ]` task, prepares coding brief |
| "Self-improve" | Updates both OpenClaw and Antigravity knowledge |
| "What did Antigravity do?" | Shows task diffs and new learnings |
| "Set up the reverse bridge" | Creates Antigravity skill for OpenClaw delegation |

## Prerequisites

- Google Antigravity IDE with `~/.gemini/antigravity/` directory
- A project with `.agent/` directory (Antigravity standard)
- Python 3.10+
- OpenClaw installed and running

## Architecture

See [references/architecture.md](references/architecture.md) for detailed documentation of Antigravity's knowledge system and how the bridge maps between both systems.

## Security & Privacy

- **100% local.** No external API calls. No cloud sync. No telemetry.
- Scripts only read/write within your configured directories.
- No credentials or tokens required.
- The skill never modifies source code — only knowledge, task, and memory files.

## Contributing

Issues and PRs welcome. This is the first multi-agent knowledge bridge — there's a lot of room to improve.

## License

MIT
