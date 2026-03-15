# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A CLI tool for managing AI agent teams. It's packaged as a "skill" for ClawHub/ClawDBot - a system for installing and running CLI tools as AI agent capabilities.

## Commands

```bash
# Run team management
python3 scripts/team.py list
python3 scripts/team.py update --agent-id "id" --name "Name" --role "Role" --enabled true --tags "tag1,tag2" --expertise "skill1" --not-good-at "weakness1"
python3 scripts/team.py reset

# Run tests
python3 -m pytest tests/ -v
```

## Architecture

A CLI module for team member management:

- `scripts/team.py` - Team member CRUD (stores in `~/.agent-team/team.json`)

Uses argparse subcommands, outputs YAML format for list commands, and supports `--data-file` for custom storage paths.

## Data File Paths

Default: `~/.agent-team/team.json`

Directory is auto-created. The script handles missing/invalid files gracefully.