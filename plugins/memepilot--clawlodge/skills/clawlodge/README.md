# ClawLodge Skill

Minimal ClawHub upload package for using ClawLodge from an OpenClaw-compatible agent.

## What this skill does

- search published OpenClaw workspaces
- inspect workspace metadata and versions
- download workspace zip archives
- optionally log in and publish a workspace
- optionally favorite, comment on, or report a workspace

## Included files

- `SKILL.md`
- `agents/openai.yaml`

## Runtime requirement

This skill expects the `clawlodge` CLI to be installed and available on `PATH`.

## Recommended install command

```bash
npm install -g clawlodge-cli
```

## Default target

If no origin is specified, the CLI uses:

```text
https://clawlodge.com
```

## Notes

- read actions such as `search`, `show`, `get`, and `download` do not require login
- write actions such as `favorite`, `comment`, `report`, and `publish` require a PAT
- downloaded workspaces should be extracted into a temporary directory first
- do not overwrite `~/.openclaw/workspace` before creating a backup
