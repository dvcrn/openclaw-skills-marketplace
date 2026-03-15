---
name: pincer
description: "Security-first wrapper for installing agent skills. Scans for malware, prompt injection, and suspicious patterns before installation. Use instead of `clawhub install` for safer skill management."
homepage: https://github.com/panzacoder/pincer
---

# pincer 🛡️

Security-first wrapper for `clawhub install`. Scans skills for malware, prompt injection, and suspicious patterns before installation.

## Why?

Agent skills are powerful — they're basically executable documentation. The ClawHub ecosystem has already seen [malware campaigns](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/) distributing infostealers via innocent-looking skills. pincer adds a security layer before you install anything.

## Install

```bash
# From ClawHub
clawhub install pincer

# Or manually
chmod +x ./scripts/pincer.sh
ln -sf "$(pwd)/scripts/pincer.sh" ~/.local/bin/pincer
```

**Dependencies:**
- `clawhub` — for fetching skills
- `uvx` — for mcp-scan (`brew install uv`)
- `jq` — for JSON parsing

## Usage

### Safe Install

```bash
# Instead of: clawhub install some-skill
pincer install some-skill

# With specific version
pincer install some-skill@1.2.0
```

### Scan Without Installing

```bash
# Scan a ClawHub skill
pincer scan some-skill

# Scan a local directory
pincer scan ./path/to/skill

# JSON output for automation
pincer scan some-skill --json
```

### Audit Installed Skills

```bash
# Quick-scan all installed skills
pincer audit

# JSON output
pincer audit --json
```

### Manage Trust

```bash
# Add trusted publisher (auto-approve clean skills)
pincer trust add steipete

# Remove from trusted
pincer trust remove old-publisher

# Block a publisher or skill
pincer trust block suspicious-dev
pincer trust block malware-skill

# Unblock
pincer trust unblock redeemed-dev

# List all trust settings
pincer trust list
```

### View History

```bash
# See what you've installed
pincer history

# JSON output
pincer history --json
```

### Configuration

```bash
# Show current config
pincer config show

# Edit in $EDITOR
pincer config edit

# Reset to defaults
pincer config reset
```

## What It Checks

### Via mcp-scan (Invariant Labs)
- Prompt injection attacks
- Malware payloads in natural language
- Tool poisoning
- Sensitive data exposure
- Hard-coded secrets

### Additional Pattern Detection
| Pattern | Risk | Description |
|---------|------|-------------|
| Base64 commands | 🚨 High | Encoded shell commands |
| Hex payloads | 🚨 High | Obfuscated binary data |
| `xattr -d quarantine` | 🚨 High | macOS Gatekeeper bypass |
| `curl \| sh` | 🚨 High | Pipe to shell execution |
| Password archives | 🚨 High | Hidden malicious payloads |
| Download + execute | ⚠️ Medium | `chmod +x && ./` patterns |
| `eval $var` | ⚠️ Medium | Dynamic code execution |
| Hidden files | ⚠️ Medium | Dot-file creation |
| Persistence | ⚠️ Medium | cron/launchd entries |

### Publisher & Provenance
- Publisher reputation (trusted list)
- Download count threshold
- Skill age threshold
- Blocklist checking

### Binary Detection
- Scans for bundled executables
- Flags Mach-O, ELF, PE32 binaries

## Risk Levels

| Level | Meaning | Action |
|-------|---------|--------|
| ✅ **CLEAN** | No issues | Auto-approve if trusted publisher |
| ⚠️ **CAUTION** | Warnings present | Prompt for approval |
| 🚨 **DANGER** | Suspicious patterns | Block (override with `--force`) |
| ☠️ **MALWARE** | Known malicious | Block (cannot override) |
| ⛔ **BLOCKED** | On blocklist | Block (cannot override) |

## Configuration

Config: `~/.config/pincer/config.json`

```json
{
  "trustedPublishers": ["openclaw", "steipete", "invariantlabs-ai"],
  "blockedPublishers": [],
  "blockedSkills": [],
  "autoApprove": "clean",
  "logInstalls": true,
  "minDownloads": 0,
  "minAgeDays": 0
}
```

| Key | Description |
|-----|-------------|
| `trustedPublishers` | Publishers whose clean skills auto-approve |
| `blockedPublishers` | Always block these publishers |
| `blockedSkills` | Always block these specific skills |
| `autoApprove` | `"clean"` = auto-approve clean+trusted, `"never"` = always prompt |
| `logInstalls` | Log installations to history file |
| `minDownloads` | Warn if skill has fewer downloads |
| `minAgeDays` | Warn if skill is newer than N days |

## Examples

### Clean Install
```
$ pincer install bird
🛡️ pincer v1.0.0

  → Fetching bird from ClawHub...
  Publisher: steipete (trusted)
  Stats: 7363 downloads · 27 ★ · created 1 month ago

🛡️ pincer Scanning bird...

  → Running mcp-scan...
  ✅ mcp-scan: passed
  → Checking for suspicious patterns...
  ✅ Pattern check: passed
  → Checking external URLs...
  ✅ URL check: passed
  → Checking for bundled binaries...
  ✅ Binary check: passed

Risk Assessment:
  ✅ CLEAN — No issues detected

  → Auto-approved (clean + trusted config).
  → Installing bird...
  ✅ Installed successfully!
```

### Dangerous Skill Blocked
```
$ pincer install sketchy-tool
🛡️ pincer v1.0.0

  → Fetching sketchy-tool from ClawHub...
  Publisher: newaccount (unknown)
  Stats: 12 downloads · 0 ★ · created 2 days ago

🛡️ pincer Scanning sketchy-tool...

  → Running mcp-scan...
  🚨 mcp-scan: high-risk warnings
  → Checking for suspicious patterns...
  🚨 Pattern check: suspicious patterns found
    • curl/wget piped to shell
    • macOS quarantine removal (xattr)
  → Checking external URLs...
  ⚠️ URL check: external URLs found
    • http://sketchy-domain.xyz/install
  → Checking for bundled binaries...
  ✅ Binary check: passed

Risk Assessment:
  🚨 DANGER — Suspicious patterns detected
    • mcp-scan: high-risk patterns detected
    • curl/wget piped to shell
    • macOS quarantine removal (xattr)

  ☠️ Install blocked. Use --force to override (not recommended).
```

## Credits

- [mcp-scan](https://github.com/invariantlabs-ai/mcp-scan) by Invariant Labs — core security scanning
- [1Password Security Research](https://1password.com/blog/from-magic-to-malware-how-openclaws-agent-skills-become-an-attack-surface) — threat analysis that inspired this tool
- [Snyk ToxicSkills Report](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/) — ecosystem threat research

## License

MIT

---

**Stay safe out there.** 🛡️
