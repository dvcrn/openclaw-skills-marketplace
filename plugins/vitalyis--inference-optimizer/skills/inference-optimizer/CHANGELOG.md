# Changelog

## [0.2.3] - 2026-03-03

- Exec allowlist docs: resolved binary paths (`/usr/bin/bash` on Ubuntu), preflight patterns, and troubleshooting guidance in README and SKILL.
- SKILL.md: ClawHub frontmatter (emoji, os, bins), commands table, Installation section, Security & Allowlist split; README install command `clawhub install inference-optimizer`.

## [0.2.2] - 2026-03-03

- Added `/preflight` chat flow for backup, audit, and setup preview without shell access.
- Split command intent: `/audit` is analyze-only; `/optimize` is analyze plus approved actions.
- Added `scripts/preflight.sh` with timestamped backups and run logs.
- Updated setup and verify scripts to include `/preflight` wiring and checks.
- Updated docs to reflect archive-first purge behavior and command boundaries.

## [0.2.1] - 2026-03-02

Follow-up security review (see [SECURITY.md](SECURITY.md) addendum):

- Replaced "return raw output" / "return output" with passive phrasing
- Added guidance disclaimer in SKILL.md (not system overrides; platform precedence)
- Added Before installing checklist (7 steps) to README
- Manual install: preview before `--apply`
- Added Script reference section (line numbers for review)

## [0.2.0] - 2026-03-02

Security remediation (see [SECURITY.md](SECURITY.md)):

- Purge: archive by default; `--delete` for immediate removal
- Setup: preview by default; `--apply` to modify workspace
- Instructions: descriptive wording instead of prescriptive prohibitions
- Data handling: audit metadata only; rewrites use `<redacted>` for secrets
- Allowlist: prefer manual purge; path-specific patterns if exec required

---

## [0.1.0] - 2026-03-02

- Initial release: audit script, purge script, setup, verify, optimization-agent.md.
