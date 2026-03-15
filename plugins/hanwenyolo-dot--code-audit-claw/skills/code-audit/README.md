# 🔍 Code Audit Skill for OpenClaw

An AI-powered code auditor for [OpenClaw](https://openclaw.ai) workspaces. Automatically scans your codebase and soul files for security vulnerabilities, code quality issues, and configuration risks.

## Features

- **Security Audit** (`--mode security`) — Finds hardcoded secrets, dangerous shell commands, SQL injection, unsafe deserialization
- **Quality Audit** (`--mode quality`) — Detects dead code, magic numbers, excessive complexity, TODO/FIXME debt
- **Soul Audit** (`--mode soul`) — OpenClaw-exclusive: inspects SOUL.md/MEMORY.md/AGENTS.md/SKILL.md for missing safety rules, plaintext API keys, cross-file consistency
- **System Audit** (`--mode system`) — Checks system command integrity, suspicious startup items, unexpected network listeners *(macOS)*
- **HTML Reports** — Tiered output: 🔴 Critical / 🟡 Warning / 🟢 Info

## Installation

```bash
clawhub install code-audit
```

Or clone this repo and place the folder in your OpenClaw workspace `skills/` directory.

## Usage

Trigger via chat:
> "code audit", "security audit", "soul audit", "scan my workspace"

Or run the scanner directly:

```bash
# Full audit
python3 scripts/audit_scanner.py ~/.openclaw/workspace --mode all --html

# Security only
python3 scripts/audit_scanner.py /path/to/project --mode security

# Soul files only (OpenClaw)
python3 scripts/audit_scanner.py ~/.openclaw/workspace --mode soul --html

# System security check (macOS)
python3 scripts/audit_scanner.py ~/.openclaw/workspace --mode system --html
```

## Requirements

- Python 3.8+
- OpenClaw (for skill-based triggering)

## Part of the OpenClaw Skill Ecosystem

This skill works best as part of a complete OpenClaw setup. Find more skills at [clawhub.com](https://clawhub.com).

## License

MIT License — free to use, modify, and distribute.

## Contact

Built with ❤️ using OpenClaw. Questions or feedback? Find us on the [OpenClaw Discord](https://discord.com/invite/clawd).
