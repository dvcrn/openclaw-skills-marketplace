---
name: prusalink-cli
description: "OpenClaw skill: local PrusaLink CLI (curl wrapper) for status/upload/print using Digest auth (user/password) or optional X-Api-Key."
---

# PrusaLink CLI

This skill provides a small, local `curl`-based PrusaLink CLI via `run.sh`.

For safety, this published skill intentionally **does not** include an "arbitrary API request" command (to reduce prompt-injection misuse). It exposes only the fixed, common endpoints (status/job/upload/start/cancel).

## Install Into OpenClaw

Copy this folder to:

- `~/.openclaw/skills/prusalink-cli/`

Then OpenClaw can discover it as a skill.

## Run

Run through the skill wrapper:

```bash
~/.openclaw/skills/prusalink-cli/run.sh --help
```

## Auth

Set either:

- Digest auth: `PRUSALINK_USER` + `PRUSALINK_PASSWORD` (recommended)
- or `PRUSALINK_API_KEY` (sent as `X-Api-Key`, if your PrusaLink supports it)

Avoid shell history leaks:

```bash
~/.openclaw/skills/prusalink-cli/run.sh --password-file /path/to/secret status
```

## Security Notes

- This skill does not download or execute code from the network at runtime.
- It only makes HTTP requests to your configured `PRUSALINK_HOST`.
