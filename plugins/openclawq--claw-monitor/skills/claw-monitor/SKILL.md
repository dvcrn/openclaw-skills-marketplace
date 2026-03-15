---
name: claw-monitor
description: "Use the `clawmonitor` CLI to monitor OpenClaw sessions (last user/assistant messages, run state via locks, delivery failures, Telegram thread-binding routing)."
homepage: https://github.com/openclawq/clawmonitor
---

# ClawMonitor (OpenClaw monitoring)

Use this skill when the user asks questions like:

- “Did my agent finish? Why no feedback?”
- “Which session/thread received the last message, and when?”
- “Is the agent working, interrupted, or stuck? Any delivery failures?”

## Preconditions

- This skill runs on a machine that has OpenClaw state at `~/.openclaw/`.
- `clawmonitor` is installed on that same machine.

## Preflight (recommended)

Before using the commands below, verify the binary exists and can read local OpenClaw state:

```bash
clawmonitor --version
clawmonitor init --non-interactive || true
clawmonitor status --format md
```

If `clawmonitor` is missing, or `status` fails, install it first.

Install:

```bash
pip install clawmonitor
```

Alternative installs (cleaner / safer):

- `pipx` (recommended when available):

  ```bash
  pipx install clawmonitor
  ```

- Virtualenv:

  ```bash
  python3 -m venv .venv
  . .venv/bin/activate
  pip install -U pip
  pip install clawmonitor
  ```

Notes:

- Some OpenClaw environments intentionally disallow installing packages at runtime. If installs are blocked, ask the user to install `clawmonitor` on the host first.
- `clawmonitor init` writes config under `~/.config/clawmonitor/config.toml` and is safe to re-run.

## Core commands

### 0) Tree view (who owns which sessions)

If you suspect ACP/subagent routing issues (e.g. Telegram thread bindings), start with:

```bash
clawmonitor tree
```

### 1) Status (Markdown)

Show the core status table (good default for IM replies):

```bash
clawmonitor status --format md
```

For a more verbose table including task/message previews:

```bash
clawmonitor status --format md --detail
```

### 2) Drill down on one session

Export a redacted report for a single session key:

```bash
clawmonitor report --session-key 'agent:main:main' --format md
```

### 2.5) TUI (interactive)

Full-screen monitor UI:

```bash
clawmonitor tui
```

Useful keys:

- `t`: toggle tree/flat list
- `r`: refresh now
- `f`: cycle refresh interval
- `Enter`: nudge selected session
- `?`: help overlay

### 3) Nudge (ask the session to report progress)

Send a progress request into the session (this is a trigger message; the agent may reply to IM depending on routing/delivery):

```bash
clawmonitor nudge --session-key 'agent:main:main' --template progress
```

## Troubleshooting quick wins

- If `clawmonitor status` shows `DELIVERY_FAILED`: export a report and check the redacted error + related logs.

  ```bash
  clawmonitor report --session-key 'agent:main:main' --format md
  ```

- If Telegram looks “bound” to the wrong sessionKey (ACP routing): run `clawmonitor tree`, then monitor the bound session instead of `agent:main:...`.
- If TUI is unavailable (non-interactive terminals): use `clawmonitor status --format md --detail` for a stable IM-friendly view.

## Reply guidelines

- Prefer `--format md` outputs for IM replies.
- If status shows `DELIVERY_FAILED` or `NO_FEEDBACK`, include the relevant sessionKey and recommend a `report` export next.
- Avoid pasting raw gateway logs unless the user asks; use `clawmonitor report` which redacts common secrets.
