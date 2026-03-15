# 🛡️ Avenger Initiative

> Encrypted GitHub backup & restore for any [OpenClaw](https://openclaw.ai) agent system.

<p align="center">
  <a href="https://proskills.md/skills/avenger-initiative">
    <img src="https://img.shields.io/badge/ProSkills.md-Browse%20%26%20Install-brightgreen?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyek0xMCAxN2wtNS01IDEuNDEtMS40MUwxMCAxNC4xN2w3LjU5LTcuNTlMMTkgOGwtOSA5eiIvPjwvc3ZnPg==" alt="ProSkills.md">
  </a>
  &nbsp;
  <a href="https://clawhub.ai/Asif2BD/avenger-initiative">
    <img src="https://img.shields.io/badge/ClawHub-Install%20via%20CLI-orange?style=for-the-badge" alt="ClawHub">
  </a>
  &nbsp;
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="MIT License">
  </a>
</p>

<p align="center">
  <strong>
    &nbsp;
    <a href="https://proskills.md/skills/avenger-initiative">📦 ProSkills.md</a>
    &nbsp;·&nbsp;
    <a href="https://clawhub.ai/Asif2BD/avenger-initiative">🔧 ClawHub</a>
    &nbsp;·&nbsp;
    <a href="#installation">⬇️ Install</a>
    &nbsp;·&nbsp;
    <a href="#quick-start">🚀 Quick Start</a>
    &nbsp;·&nbsp;
    <a href="SECURITY.md">🔒 Security</a>
  </strong>
</p>

---

## What It Does

Avenger Initiative backs up your entire OpenClaw system to a **private GitHub repo** every night — configs, agent memories, SOUL files, custom skills, cron jobs — everything needed to fully restore from zero.

**Security model:**
- `openclaw.json` (API keys, bot tokens) → **AES-256-CBC encrypted** before leaving disk
- Everything else (SOUL.md, MEMORY.md, etc.) → plaintext in your private repo
- Encryption key stays on your machine — never committed to Git

**Branch-per-night strategy with smart retention:**

| Branch | Pattern | Retention |
|--------|---------|-----------|
| Daily | `backup/daily/YYYY-MM-DD` | Last 7 days |
| Weekly | `backup/weekly/YYYY-WNN` | Last 8 weeks |
| Monthly | `backup/monthly/YYYY-MM` | Last 12 months |

## What's in the vault?

Every backup automatically generates a human-friendly **`README.md`** in the vault root — so anyone (or any agent) landing in the repo immediately knows what it is, what's encrypted vs plaintext, and exactly how to restore. It includes step-by-step restore commands, natural-language Avenger agent commands, and security notes. A compact **`AVENGER-MANIFEST.json`** is also written with machine-readable backup metadata for scripted restores.

---

## Installation

### Option 1 — ClawHub CLI (recommended)

```bash
clawhub install avenger-initiative
```

> Get the ClawHub CLI: `npm install -g clawhub`

### Option 2 — ProSkills.md

Visit **[proskills.md/skills/avenger-initiative](https://proskills.md/skills/avenger-initiative)** and click **Install** — the skill is listed for free, no login required to browse.

### Option 3 — Manual (git clone)

```bash
mkdir -p ~/.openclaw/workspace/skills
git clone https://github.com/ProSkillsMD/avenger-initiative \
  ~/.openclaw/workspace/skills/avenger-initiative
chmod +x ~/.openclaw/workspace/skills/avenger-initiative/scripts/*.sh
```

---

## Quick Start

### 1. Create a private GitHub vault repo

Go to [github.com/new](https://github.com/new) and create a **private** repo (e.g. `my-openclaw-vault`).

### 2. Set up Avenger Initiative

Tell your OpenClaw agent:

> **"Setup avenger"**

Your agent will walk you through the rest — vault repo URL, encryption key, first backup.

Or run manually:

```bash
bash ~/.openclaw/workspace/skills/avenger-initiative/scripts/setup.sh \
  --repo https://github.com/yourname/your-vault
```

### 3. Save your encryption key

After setup, you'll see a 64-character hex key. **Save it in your password manager immediately.**  
Without it, `openclaw.json.enc` cannot be decrypted.

### 4. First backup runs automatically

Daily backups are scheduled at 02:00 UTC via OpenClaw cron.

---

## Usage

| Say this to your agent | What happens |
|------------------------|-------------|
| `"avenger backup"` | Runs backup now |
| `"avenger status"` | Shows last backup time and branch |
| `"restore from vault"` | Guided restore flow |
| `"avenger setup"` | First-time setup wizard |

---

## Restore

```bash
# Restore latest (main branch)
bash ~/.openclaw/workspace/skills/avenger-initiative/scripts/restore.sh

# Restore from a specific date
bash ~/.openclaw/workspace/skills/avenger-initiative/scripts/restore.sh \
  --branch backup/daily/2026-03-10

# After restore
openclaw gateway restart
```

---

## Requirements

- [OpenClaw](https://openclaw.ai) installed and running
- [GitHub CLI](https://cli.github.com) (`gh`) authenticated (`gh auth login`)
- `git`, `openssl` (standard on most systems)
- A private GitHub repo for your vault

---

## Security

This skill uses:
- **`openssl enc -aes-256-cbc`** — encrypts your `openclaw.json` with your own key
- **`git push`** — pushes to your own private vault repo only
- **No external servers** — data goes only to your own GitHub account

See [SECURITY.md](SECURITY.md) for full script-by-script analysis and audit instructions.

---

## Changelog

### v1.0.4
- Each backup now generates a human-friendly `README.md` inside the vault with purpose, restore commands, and Avenger agent commands
- Added `AVENGER-MANIFEST.json` (machine-readable backup metadata)

### v1.0.3
- Fixed: `main` branch now always exists (setup.sh initializes it on first run)
- Fixed: backup commits to `main` first, then creates dated snapshot branch

### v1.0.2
- Added ProSkills.md + ClawHub badges to README
- Full installation guide (3 methods: CLI, ProSkills.md, git clone)

### v1.0.1
- Added `.clawhubsafe` and `SECURITY.md` to clarify false-positive security scan flags

### v1.0.0
- Initial release

---

## License

MIT © [ProSkillsMD](https://github.com/ProSkillsMD)

---

<p align="center">
  <sub>
    Find more OpenClaw skills at
    <a href="https://proskills.md"><strong>ProSkills.md</strong></a>
    — the verified AI skills directory
  </sub>
</p>
