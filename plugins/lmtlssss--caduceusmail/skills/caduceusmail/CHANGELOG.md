# Changelog

## 5.3.3

Fresh-onboarding and VPS handoff release.

### Added

* gateway-assisted Microsoft device-login handoff in `scripts/caduceusmail.sh`
* fallback dashboard URL emission when browser handoff is unavailable
* handoff artifact output at `INTEL_DIR/caduceusmail-login-handoff.json`

### Changed

* bootstrap output parsing now extracts the JSON summary robustly even when PowerShell emits preamble text
* validated a true fresh OpenClaw pull path (`clawhub install` -> strict credentials -> live provision/verify/retire probes)

## 5.1.1

Wording/design restoration release that brings back the high-impact 4.2.0 product voice while keeping the scan-hardening changes.

### Changed

* expanded `SKILL.md` frontmatter `requires.env` to explicitly declare Entra secret and Cloudflare credentials used by runtime code paths
* expanded `SKILL.md` frontmatter `requires.bins` to include `pwsh` and `rg` alongside existing runtime tools
* added explicit privilege, persistence, module-install, and external-script-resolution disclosures in `SKILL.md`
* documented canonical env keys and trust boundaries in `README.md` and `docs/openclaw.md`
* added `tests/test_skill_frontmatter.py` coverage that enforces sensitive env and binary declarations
* restored 4.2.0-style design language and positioning in `SKILL.md` and `README.md` (including inbox-reliability optimization messaging and hard rules framing)

## 5.1.0

This release turns ☤CaduceusMail into a full repository grade skill bundle.

### Added

* `VERSION`, `CHANGELOG.md`, `pyproject.toml`, `Makefile`, and test suite
* `scripts/caduceusmail-doctor.py` plus `src/caduceusmail/doctor.py`
* `scripts/entra-exchange.sh` and `scripts/send_mail_graph.py` for probe sends
* `examples/openclaw.config.json5`
* `docs/architecture.md`, `docs/openclaw.md`, and `docs/node-bootstrap.md`
* `--simulate-bootstrap` path in the shell wrapper for smoke tests and CI like environments

### Changed

* `SKILL.md` stays ClawHub safe with single line JSON metadata
* shell wrapper now skips PowerShell dependency when bootstrap is simulated or skipped
* bootstrap script is shipped as both `.ps1` and `.ps1.txt`
* repo layout is now ready for GitHub release zips and ClawHub publishing

### Fixed

* missing `entra-exchange.sh` bridge used by probe sends
* sandbox smoke flow no longer depends on a local browser or installed PowerShell
* normalized canonical identity to `☤CaduceusMail` + `caduceusmail` across scripts, docs, and metadata
* default behavior is non-persistent; env/secret writes now require explicit `--persist-env`/`--persist-secrets`
* external script resolution is now opt-in via `CADUCEUSMAIL_ALLOW_EXTERNAL_SCRIPT_RESOLUTION=1`
