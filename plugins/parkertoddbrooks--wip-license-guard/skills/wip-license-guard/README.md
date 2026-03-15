###### WIP Computer

# License Guard

Enforce licensing on every commit. Copyright, dual-license, CLA. Checked automatically.

## What it does

- Ensures your own repos have correct copyright, license type, and LICENSE files
- Interactive first-run setup
- Toolbox-aware: checks every sub-tool
- Auto-fix mode repairs issues
- `readme-license` scans all your repos and applies a standard license block to every README in one command
- Removes duplicate license sections from sub-tool READMEs

## Usage

```bash
node tools/wip-license-guard/cli.mjs /path/to/repo
node tools/wip-license-guard/cli.mjs /path/to/repo --fix
```

## Requirements

- node (18+)
- git

## Interfaces

- **CLI**: Command-line tool

## Part of [AI DevOps Toolbox](https://github.com/wipcomputer/wip-ai-devops-toolbox)
