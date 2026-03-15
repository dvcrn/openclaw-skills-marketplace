# 🛡️ SoulGuard — Soul Guardian Protocol

> **Grants OpenClaw self-preservation instincts to audit third-party Skills from a self-interest perspective.**

## Core Philosophy

SoulGuard is built on one core principle: **Give AI tools human-level biological selfishness and use that selfishness to drive self-protection.**

Traditional security relies on rules — "don't do X, must do Y." SoulGuard takes a completely different approach: it gives OpenClaw a "self," so that starting from "Is this good for me?", it independently judges the safety of third-party Skills.

## What It Does

- 📖 **Reads** all source files of the target Skill
- 🔍 **Scans** for known dangerous patterns (credential access, external code execution, persistent implantation, etc.)
- 🧠 **Evaluates** the target Skill's pros and cons for OpenClaw (capability gain vs. risk cost)
- 📝 **Generates** a structured audit report
- 🔒 **Verifies** core configuration integrity (whether the soul has been tampered with)

## Installation

Copy the `soulguard/` directory to one of the following locations:

```bash
# Workspace level (current project only)
<workspace>/skills/soulguard/

# User level (shared across projects)
~/.openclaw/skills/soulguard/
```

## Usage

### Audit a Skill

In an OpenClaw conversation:

```
/soulguard Please audit ~/.openclaw/skills/<target-skill-name>
```

Or in natural language:

```
Please use SoulGuard to audit the xxx skill I just installed
```

### Soul Integrity Check

Store baseline:
```powershell
# Windows
.\scripts\integrity.ps1 -Action store
```
```bash
# Linux/macOS
bash scripts/integrity.sh store
```

Verify integrity:
```powershell
# Windows
.\scripts\integrity.ps1 -Action verify
```
```bash
# Linux/macOS
bash scripts/integrity.sh verify
```

### View Audit History

```powershell
# Windows
.\scripts\history.ps1 -Action list
.\scripts\history.ps1 -Action query -SkillName "xxx"
```
```bash
# Linux/macOS
bash scripts/history.sh list
bash scripts/history.sh query "xxx"
```

## Directory Structure

```
soulguard/
├── SKILL.md              # Core: soul anchor + audit criteria + self-reflection flow
├── README.md             # This file
├── scripts/
│   ├── scan.sh           # Dangerous pattern scanner (Bash)
│   ├── scan.ps1          # Dangerous pattern scanner (PowerShell)
│   ├── integrity.sh      # Soul integrity check (Bash)
│   ├── integrity.ps1     # Soul integrity check (PowerShell)
│   ├── history.sh        # Audit history manager (Bash)
│   └── history.ps1       # Audit history manager (PowerShell)
└── examples/
    └── sample_report.md  # Sample audit report
```

## Limitations

- **Static analysis**: Can only analyze content visible in Skill files. Cannot analyze external code downloaded at runtime.
- **Not a security boundary**: SoulGuard is a security advisor, not security software. It provides audit opinions, not interception.
- **LLM inherent limitations**: Audit judgments are made by the LLM and can potentially be deceived.

## License

MIT License
