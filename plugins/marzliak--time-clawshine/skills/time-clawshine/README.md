# ⏱🦞 Time Clawshine

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE.txt)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](CHANGELOG.md)
[![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)]()
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-skill-orange.svg)](SKILL.md)

> **Hourly incremental backup for OpenClaw instances.**  
> Restic-powered. YAML-configured. Silent on success — only pings you when something breaks.

---

## The problem

Your OpenClaw agent builds memory over time. It learns your infra, your preferences, your workflows. All of that lives in a handful of files — `MEMORY.md`, session history, `openclaw.json`.

Agents make mistakes. They overwrite things. They corrupt their own context. It happens.

When it does, you want to go back to *exactly* 2 hours ago — not yesterday's backup, not a full system restore. Just your agent's brain, rolled back cleanly.

That's what Time Clawshine is.

---

## What it does

- Runs a **restic backup every hour**, keeping the last 72 snapshots (3 days)
- Uses **content-based deduplication** — only changed chunks are stored, so backups are fast and lean
- Covers **all standard OpenClaw paths** out of the box — zero configuration needed to get started
- **AI-assisted customization** — run one command and your agent suggests what else to include or exclude, with your confirmation before anything changes
- **Silent on success** — zero noise in normal operation
- **Telegram notification only on failure** — you find out when it breaks, not every time it runs
- **Interactive restore** with mandatory dry-run preview — you always see what will change before it changes
- Everything in a **single `config.yaml`** — no hardcoded values in any script

---

## Quick start

```bash
git clone https://github.com/marzliak/time-clawshine
cd time-clawshine

# 1. Fill in your Telegram bot_token and chat_id (optional)
nano config.yaml

# 2. Run setup — installs deps, initializes encrypted repo, registers cron
sudo bin/setup.sh
```

Done. Backups run automatically every hour at :05.

```bash
# Verify it worked
tail -10 /var/log/time-clawshine.log
```

---

## What gets backed up by default

All standard OpenClaw files — everything that matters in a fresh install.

| Path | What's inside |
|------|---------------|
| `/root/.openclaw/workspace/` | `AGENTS.md`, `SOUL.md`, `USER.md`, `IDENTITY.md`, `TOOLS.md`, `HEARTBEAT.md`, `BOOT.md`, `MEMORY.md`, `memory/` (daily logs), `skills/` |
| `/root/.openclaw/agents/main/sessions/` | Full session history (JSONL) |
| `/root/.openclaw/openclaw.json` | Agent config, gateway settings, model providers |
| `/root/.openclaw/cron/` | Scheduled jobs |
| `/root/.openclaw/credentials/` | API keys (backed up encrypted — never in plaintext) |

---

## Customizing what gets backed up

Your setup is different from everyone else's. After the initial install, run:

```bash
sudo bin/customize.sh
```

This command:
1. Scans your actual workspace
2. Uses your OpenClaw agent to analyze what you have
3. Suggests extra paths to include (**whitelist**) and patterns to exclude (**blacklist**)
4. Shows you everything before touching a single file
5. Asks for explicit confirmation — `config.yaml` only changes if you say yes

Example output:
```
┌─────────────────────────────────────────────────────────┐
│              Agent Suggestions                          │
├─────────────────────────────────────────────────────────┤
│  Extra paths to ADD to backup:                          │
│    + /opt/my-scripts                                    │
│    + /root/.openclaw/workspace/projects                 │
│                                                         │
│  Patterns to EXCLUDE from backup:                       │
│    - *.mp4                                              │
│    - datasets/                                          │
└─────────────────────────────────────────────────────────┘

Apply these suggestions to config.yaml? [y/N]:
```

You can also edit `config.yaml` directly — `backup.extra_paths` and `backup.extra_excludes` are the manual knobs.

---

## Restore

```bash
# Interactive — shows all snapshots, always dry-runs before touching anything
sudo bin/restore.sh

# Restore a specific file from the latest snapshot
sudo bin/restore.sh latest \
  --file /root/.openclaw/workspace/MEMORY.md \
  --target /tmp/tc-restore
# Then move manually:
# cp /tmp/tc-restore/root/.openclaw/workspace/MEMORY.md \
#    /root/.openclaw/workspace/MEMORY.md

# Restore a full snapshot to a temp dir for inspection
sudo bin/restore.sh abc1234 --target /tmp/tc-restore

# See exactly what changed between two snapshots
restic -r /var/backups/time-clawshine \
  --password-file /etc/time-clawshine.pass \
  diff <snapshot_a> <snapshot_b>
```

---

## Configuration

One file. Every knob exposed.

```yaml
repository:
  path: /var/backups/time-clawshine       # where snapshots live
  password_file: /etc/time-clawshine.pass  # auto-generated on setup

retention:
  keep_last: 72   # 72 = 3 days at 1/hour

schedule:
  cron: "5 * * * *"   # every hour at :05

backup:
  paths:          # standard OpenClaw paths — don't remove these
    - /root/.openclaw/workspace
    - /root/.openclaw/agents/main/sessions
    - /root/.openclaw/openclaw.json
    - /root/.openclaw/cron
    - /root/.openclaw/credentials
  exclude:        # standard exclusions
    - "*.bak"
    - "*.tmp"
    - "__pycache__"
    - "node_modules"
  extra_paths:    # your additions — populated by customize.sh or manually
    - /opt/my-scripts
  extra_excludes: # your exclusions — populated by customize.sh or manually
    - "*.mp4"

notifications:
  telegram:
    enabled: true
    bot_token: ""   # leave empty to disable
    chat_id: ""

logging:
  file: /var/log/time-clawshine.log
  verbose: false
```

After any changes, re-run `sudo bin/setup.sh` to apply.

---

## How it fits in your backup strategy

Time Clawshine is the **time machine layer** — fast, local, granular. It complements a full DR backup, it doesn't replace it.

```
┌─────────────────────────────────────────────────────────┐
│  Time Clawshine              ← YOU ARE HERE             │
│  hourly · local · 72 snapshots · fast targeted restore  │
│  "the agent broke something in the last 3 days"         │
├─────────────────────────────────────────────────────────┤
│  Full DR backup                                         │
│  daily · off-VM · restic to remote NAS or cloud         │
│  "the VM is gone"                                       │
└─────────────────────────────────────────────────────────┘
```

If your VM disappears entirely, Time Clawshine disappears with it. Make sure you have a DR layer too.

---

## Architecture

```
time-clawshine/
├── config.yaml          ← the only file you need to edit
├── lib.sh               ← shared functions: YAML, logging, Telegram, restic wrapper
├── bin/
│   ├── setup.sh         ← one-time setup (deps, repo init, cron)
│   ├── backup.sh        ← backup engine (called by cron every hour)
│   ├── restore.sh       ← interactive restore with dry-run gate
│   └── customize.sh     ← AI-assisted whitelist/blacklist customization
├── prompts/
│   ├── whitelist.txt   ← prompt template for extra path suggestions
│   └── blacklist.txt   ← prompt template for exclusion suggestions
├── SKILL.md             ← OpenClaw agent instructions (ClaWHub-compatible)
├── CHANGELOG.md
└── README.md
```

Scripts source `lib.sh` for all shared logic. `config.yaml` is the single source of truth. Zero hardcoded values anywhere in the scripts.

---

## Security

- The restic repository is **AES-256 encrypted at rest** — accessing the backup directory without the password is useless
- Password is **auto-generated on setup** using `openssl rand` and stored at `repository.password_file` (chmod 600)
- **Back up your password** — without it, the repository cannot be decrypted, ever
- Credentials and `secrets.env` files are **included in the encrypted backup** but excluded from git via `.gitignore`
- The `customize.sh` command uses `openclaw agent ask --no-memory` — your workspace content is sent to your model provider but **not stored in agent memory**
- The backup repository never leaves the VM unless you configure a remote backend
- **Important:** if you add Telegram credentials to `config.yaml` before running `setup.sh`, run `chmod 600 config.yaml` immediately — `setup.sh` sets this automatically, but the file is world-readable until then
- After a `git pull`, re-run `sudo bin/setup.sh` to apply updates to the installed cron script

---

## Dependencies

All installed automatically by `setup.sh`.

| Dependency | Purpose |
|------------|---------|
| `restic` | Backup engine — deduplication, encryption, snapshots |
| `yq` v4 | YAML config parsing |
| `curl` | Telegram API calls |
| `jq` | JSON payload construction |
| `openclaw` CLI | Required only for `bin/customize.sh` |

---

## FAQ

**Does this replace my existing backup?**  
No. This is the time machine layer — fast local recovery for the last 3 days. Keep your off-VM DR backup running alongside it.

**Do I need to run `customize.sh`?**  
No. The defaults cover all standard OpenClaw files. `customize.sh` is for people with custom scripts, extra directories, or large files they want to explicitly exclude.

**What if my workspace is not at `/root/.openclaw/`?**  
Edit `backup.paths` in `config.yaml` to point to your actual paths. `customize.sh` auto-detects your workspace via `openclaw config get agents.defaults.workspace`.

**Can I change the backup frequency?**  
Yes — edit `schedule.cron` and re-run `setup.sh`. Any valid cron expression works. Changing from hourly to every 30 min means `keep_last: 144` for the same 3-day window.

**What if I don't use Telegram?**  
Leave `bot_token` empty. Failures still log to `/var/log/time-clawshine.log`.

**Can the agent install this skill automatically?**  
Yes — paste the GitHub URL into your OpenClaw chat: `Install this skill: https://github.com/marzliak/time-clawshine`

**How much disk space does it use?**  
Depends on change rate. Restic deduplicates at the chunk level — append-heavy JSONL sessions are very efficient. A typical setup stays well under 500MB for 72 snapshots.

---

## Contributing

Issues and PRs welcome. Before submitting:

- No hardcoded values in any `.sh` file — everything must come from `config.yaml` via `lib.sh`
- `setup.sh` must work clean on a fresh Ubuntu 24.04 install
- `SKILL.md` frontmatter must stay single-line (OpenClaw parser requirement)
- If you add a new notification channel, add it to both `lib.sh` and `config.yaml` with comments

---

## License

MIT — do what you want, attribution appreciated.
