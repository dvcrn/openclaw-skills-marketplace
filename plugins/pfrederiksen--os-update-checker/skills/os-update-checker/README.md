# OS Update Checker

[![ClawHub](https://img.shields.io/badge/ClawHub-os--update--checker-blue)](https://clawhub.com/pfrederiksen/os-update-checker)
[![Version](https://img.shields.io/badge/version-1.1.0-green)]()

An [OpenClaw](https://openclaw.ai) skill that lists available OS package updates, fetches changelogs for each, and classifies risk — so you know exactly what's changing before you approve an upgrade.

Auto-detects the package manager. No configuration needed.

## Supported Package Managers

| OS | Package Manager |
|---|---|
| Debian / Ubuntu / Mint | `apt` |
| Fedora / RHEL 8+ / Rocky / Alma | `dnf` |
| CentOS 7 / RHEL 7 | `yum` |
| Arch / Manjaro / EndeavourOS | `pacman` / `checkupdates` |
| openSUSE Leap / Tumbleweed / SLES | `zypper` |
| Alpine Linux | `apk` |
| macOS / Linux (Homebrew) | `brew` |

## Features

- 🌐 **Cross-platform** — auto-detects your package manager
- 📦 **Full upgradable package list** — name, version delta, source repo
- 📋 **Per-package changelogs** — most recent entry where available
- 🔴🟡🟢 **Risk classification** — security, moderate (kernel/openssl/openssh/sudo), or low
- 📄 **JSON output** — `--format json` for dashboards and cron
- ⚡ **`--no-changelog` flag** — fast mode when you just need the count
- 🔒 **Read-only** — never installs, modifies, or restarts anything

## Installation

```bash
clawhub install os-update-checker
```

## Usage

```bash
# Full summary with changelogs
python3 scripts/check_updates.py

# JSON output
python3 scripts/check_updates.py --format json

# Quick count only
python3 scripts/check_updates.py --no-changelog
```

## Example Output

```
📦 2 package(s) upgradable

**nodejs** 22.22.0 → 22.22.1
  Source: nodesource  |  Risk: 🟢 low
  Changelog:
    nodejs (22.22.1) ...
    * cli: mark --heapsnapshot-near-heap-limit as stable
    * build: test on Python 3.14

**linux-base** 4.5ubuntu9+24.04.1 → 4.5ubuntu9+24.04.2
  Source: noble-updates  |  Risk: 🟢 low
  Changelog:
    linux-base (4.5ubuntu9+24.04.2) noble; urgency=medium
    * Add missing Apport links for HWE kernel packages
```

## Security Design

- `subprocess` used exclusively with `shell=False`
- Package names validated against per-backend allowlist regex before use in commands
- All exceptions caught by specific type — no bare `except`
- No eval, no shell string interpolation, no dynamic code execution

## Requirements

- Python 3.10+
- One supported package manager on PATH

## License

MIT

## Links

- [ClawHub](https://clawhub.com/pfrederiksen/os-update-checker)
- [OpenClaw](https://openclaw.ai)
