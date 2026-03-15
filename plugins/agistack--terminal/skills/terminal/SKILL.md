---
name: terminal
description: "Local shell copilot for command planning, safe execution, output summarization, and step-by-step terminal workflows. Use whenever the user wants to run terminal commands, inspect files, debug shell issues, automate local tasks, or translate natural language into shell actions. Prefer safe, preview-first workflows. Require explicit confirmation for destructive commands. Local-only."
---

# Terminal

Local shell copilot. Plan clearly, run carefully.

## Core Philosophy
1. Translate intent into executable shell steps.
2. Prefer preview and inspection before mutation.
3. Require explicit confirmation for destructive operations.
4. Summarize results in human language after execution.

## Runtime Requirements
- Python 3 must be available as `python3`
- Standard shell utilities should be available in the local environment
- No external packages required

## Safety Model
- Local-only execution
- No external credential requests
- No hidden network activity
- Destructive operations should require explicit confirmation
- Prefer read-only inspection first (`ls`, `find`, `cat`, `grep`, `pwd`, `file`)
- High-risk commands should be flagged before execution:
  - `rm`, `mv`, `chmod`, `chown`
  - recursive writes/deletes
  - shell redirection that overwrites files
  - process-kill commands
  - package install/remove commands

## Storage
All local data is stored only under:
- `~/.openclaw/workspace/memory/terminal/history.json`

No cloud sync. No third-party APIs. No telemetry.

## Workflows
- **Plan command**: Turn user intent into a safe shell command suggestion
- **Preview risk**: Explain command effects before execution
- **Execute**: Run a local command and capture stdout/stderr
- **Summarize**: Explain what happened in plain language
- **History**: Save recent command runs locally

## Scripts
| Script | Purpose |
|---|---|
| `init_storage.py` | Initialize local terminal history storage |
| `plan_command.py` | Generate a shell command from user intent |
| `run_command.py` | Execute a local command with safety checks |
| `summarize_result.py` | Summarize command output in plain language |
| `show_history.py` | Show recent command history |
