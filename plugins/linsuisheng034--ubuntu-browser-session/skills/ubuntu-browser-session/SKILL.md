---
name: ubuntu-browser-session
description: "Use when a task needs a reusable Ubuntu Server browser session with optional assisted login and host-side page inspection."
---

# Ubuntu Browser Session

Reusable browser-session workflow for Ubuntu Server hosts.

## When To Use

- Open or inspect a page from a headless Ubuntu Server host
- Reuse a previously verified browser session instead of starting fresh
- Ask the user for one bounded round of assisted login when local reuse is not enough
- Inspect visible page state from the host after the browser session is ready

## Workflow

Preferred entrypoint:

```bash
{baseDir}/scripts/open-protected-page.sh --url 'https://target.example' --session-key default
```

Use lower-level helpers only when you need to inspect or repair an individual stage:

```bash
{baseDir}/scripts/session-manifest.sh select --origin 'https://target.example'
{baseDir}/scripts/browser-runtime.sh verify --origin 'https://target.example' --session-key default
{baseDir}/scripts/assisted-session.sh start --url 'https://target.example' --origin 'https://target.example' --session-key default
```

## Environment Requirements

```bash
command -v python3
command -v curl
command -v jq
command -v Xvfb
command -v x11vnc
command -v websockify
command -v google-chrome || command -v chromium || command -v chromium-browser
```

## Key Files

- `scripts/open-protected-page.sh`: high-level session orchestration
- `scripts/browser-runtime.sh`: browser runtime management
- `scripts/assisted-session.sh`: assisted browser session overlay
- `scripts/session-manifest.sh`: session record management
- `scripts/cdp-eval.py`: host-side page inspection helper

See also:

- `references/session-manifest.md`
- `references/assisted-session-flow.md`
