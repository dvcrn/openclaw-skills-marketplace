# Daily Memory Save

A cron skill that gives your AI agent persistent memory by periodically reviewing conversations and writing structured memory files.

## The Problem

AI agents wake up fresh each session with no memory of previous interactions. Important context — decisions, preferences, project state — is lost.

## The Solution

This skill runs every 2 hours during waking hours, reviewing recent conversations and writing two types of memory files:

1. **Daily notes** (`memory/YYYY-MM-DD.md`) — Raw daily logs of what happened
2. **Long-term memory** (`MEMORY.md`) — Curated insights that persist

## What Gets Captured

- 🎯 Decisions made
- 💡 Preferences expressed
- 📋 Project updates and status changes
- 📚 Lessons learned
- 🧠 Things the user explicitly asked to remember
- 💭 Emotional context worth noting

## Setup

1. Create a `memory/` directory in your workspace
2. Set up a cron job with the prompt from `SKILL.md`
3. Target the **main session** (not isolated) so it has access to conversation history

## Key Design Points

- **Silent** — never messages the user about saves
- **Selective** — captures signal, not noise; skips quiet periods
- **Dual-layer** — daily notes for raw context, MEMORY.md for distilled wisdom
- **Future-oriented** — writes like future-you will need this context

## Requirements

- OpenClaw with cron and system event support
- Writable workspace directory

## License

MIT
