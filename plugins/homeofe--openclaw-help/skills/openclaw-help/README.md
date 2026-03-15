# openclaw-help

> OpenClaw plugin providing a config-driven `/shortcuts` command with safe placeholder defaults.

**Current version:** `0.2.0`

---

## What it does

Registers `/shortcuts` (note: `/help` is a built-in OpenClaw command and cannot be overridden by plugins).

Prints:
- Generic placeholder sections by default
- Custom sections injected via local config

**Security design:** The repo ships with placeholder-only content. All personal shortcuts, project names, command mappings live in your local `openclaw.json` config — never in the repo.

---

## Install

```bash
clawhub install openclaw-help
```

Or local development:
```bash
openclaw plugins install -l ~/.openclaw/workspace/skills/openclaw-help
openclaw gateway restart
```

---

## Configure

In `~/.openclaw/openclaw.json` → `plugins.entries.openclaw-help.config`:

```json5
{
  "enabled": true,
  "includeTips": false,
  "sections": [
    {
      "title": "📁 Projects",
      "lines": [
        "/<project>   - Your project shortcut"
      ]
    },
    {
      "title": "🛠 Tools",
      "lines": [
        "/<command>   - Your custom command"
      ]
    }
  ]
}
```

---

## OPSEC rule

- Never put personal commands, phone numbers, group IDs, tokens, domains, or internal workflows into this repo
- Keep all real shortcuts in local config only

---

## Changelog

### v0.2.0
- **fix:** Register `/shortcuts` instead of `/help` (`/help` is a built-in command, cannot be overridden)
- **fix:** Return format changed from `{ ok, message }` to `{ text }` (gateway-compatible)
- **feat:** `requireAuth: false` — uses gateway-level `commands.allowFrom` for authorization
- **feat:** Initial public release on GitHub + npm + ClawHub

---

## License

MIT
