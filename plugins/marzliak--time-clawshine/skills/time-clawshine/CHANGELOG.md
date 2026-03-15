# Changelog

All notable changes to Time Clawshine are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — 2026-03-04

Initial release.

### Added

**Core backup engine**
- `bin/backup.sh` — hourly restic backup; silent on success; Telegram notification on failure; validates paths before running
- `bin/restore.sh` — interactive restore with mandatory dry-run preview; `--file` and `--target` flags for surgical restores
- `bin/setup.sh` — self-installing setup: installs `restic`, `yq v4`, `curl`, `jq`; initializes AES-256 encrypted repo; registers cron from config
- `lib.sh` — shared layer for all scripts: YAML parsing, structured logging, Telegram wrapper, restic wrapper, path/dep validation

**AI-assisted customization**
- `bin/customize.sh` — analyzes actual workspace, runs AI prompts via the OpenClaw agent, shows whitelist/blacklist suggestions, applies to `config.yaml` only after explicit user confirmation; saves `config.yaml.bak` before any change
- `prompts/whitelist.txt` — template asking the agent to identify extra paths worth backing up
- `prompts/blacklist.txt` — template asking the agent to identify patterns that should be excluded

**Configuration**
- `config.yaml` as single source of truth — zero hardcoded values in any script
- Full standard OpenClaw path coverage by default: `workspace/`, `sessions/`, `openclaw.json`, `cron/`, `credentials/`
- `backup.extra_paths` and `backup.extra_excludes` as clean extension points for custom additions

**OpenClaw skill**
- `SKILL.md` with ClaWHub-compatible frontmatter (single-line metadata, correct `metadata.openclaw` namespace)
- Agent instruction body covering: setup, manual backup, status check, restore, integrity check, config changes, and customization

**Other**
- `CHANGELOG.md` in Keep a Changelog format
- `.gitignore` pre-configured: excludes `.pass`, `.env`, `secrets.*`, `.bak`, backup directories
- 72-snapshot retention (3 days at 1/hour), configurable via `retention.keep_last`

---

[1.0.0]: https://github.com/marzliak/time-clawshine/releases/tag/v1.0.0
