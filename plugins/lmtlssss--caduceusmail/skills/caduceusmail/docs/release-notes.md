# Release notes for 5.3.3

This release adds VPS-first login handoff while preserving the restored 4.2.0 product voice and metadata/disclosure coherence.

Highlights:

* `SKILL.md` now declares the full sensitive env set used by runtime paths (`ENTRA_CLIENT_SECRET`, Cloudflare token/zone, and organization keys).
* `SKILL.md` now declares complete runtime binaries (`pwsh` and `rg` added).
* Restored the high-impact design language in `SKILL.md` and `README.md` (inbox-reliability optimization + enterprise-stack positioning).
* Added `--gateway-login-handoff` to route Microsoft device-login UX through OpenClaw browser hooks where available.
* Added dashboard URL fallback + intel artifact output when browser handoff is unavailable on host.
* Hardened bootstrap output handling so JSON summary extraction remains stable even with interactive PowerShell/device-login preamble.
* Skill docs now explicitly disclose high-privilege operations, opt-in secret persistence behavior, and PowerShell module installation behavior.
* Regression tests now enforce the sensitive env and binary declaration set so future releases cannot silently drift.
