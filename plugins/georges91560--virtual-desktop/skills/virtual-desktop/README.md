# virtual-desktop

🖥️ **Universal browser execution layer for OpenClaw agents**

Gives your agent a persistent headless browser — navigate any website,
click, type, fill forms, upload files, extract data, save sessions,
act on your behalf on any platform.

Built for OpenClaw agents running on Docker VPS.
Uses Playwright headless Chromium — no Xvfb, no VNC, no host dependencies.

---

## What your agent can now do

- **Analyze** — read any page, extract structured data, monitor changes over time
- **Plan** — map UIs, identify selectors, prepare multi-step workflows
- **Execute** — click, type, submit, upload, download, navigate complex flows
- **Self-correct** — screenshot errors, identify root causes, retry intelligently
- **Improve** — write discovered patterns to `.learnings/` so every run is smarter

## Works for any task

Content creation · Email management · Social publishing · Sales funnels ·
Market research · Admin workflows · Data extraction · Form automation ·
File management · Platform monitoring · Anything a human does in a browser

## Architecture

```
OpenClaw container
└── Agent
    └── virtual-desktop skill
        └── Playwright headless Chromium
            ├── Sessions  → /workspace/credentials/sessions/
            ├── Screenshots → /workspace/screenshots/
            └── Logs      → /workspace/logs/browser/
```

## Files written

| File | Purpose |
|---|---|
| `AUDIT.md` | Every action logged before + after |
| `screenshots/` | Visual proof of every execution |
| `.learnings/ERRORS.md` | Selector failures, auth issues, bot blocks |
| `.learnings/LEARNINGS.md` | Platform patterns, UI maps, navigation tricks |
| `tasks/lessons.md` | Task-scoped immediate capture |
| `memory/YYYY-MM-DD.md` | Daily summary |

## One-time setup

```bash
playwright install chromium
mkdir -p /workspace/screenshots /workspace/logs/browser /workspace/credentials/sessions
```

## Requirements

- OpenClaw v2026.1.0+
- Python 3 + Playwright (usually already installed in container)
- Run once: `playwright install chromium`

## Author

Georges Andronescu (Wesley Armando) — Veritas Corporate
