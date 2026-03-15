# Mail Caduceus

Mail Caduceus helps you stop landing in junk by automating inbox reliability at scale with branded sender lanes, trust hardening, and full lifecycle control.

Version: `1.0.3`

## Highlights

- One-line bootstrap for M365 + Cloudflare stack readiness.
- Strict credential templates in `credentials/`.
- Alias/subdomain lane provisioning (reply-capable + no-reply).
- Reply-safe retirement path with fallback continuity.
- Security-first defaults:
  - scope-locked script resolution
  - non-persistent default mode for secrets

## Install / Use

Use the skill from repository root (`SKILL.md`).

## Release Flow

Use `scripts/release.sh` for future SemVer bumps:

- `scripts/release.sh patch`
- `scripts/release.sh minor`
- `scripts/release.sh major`

## License

MIT. See `LICENSE`.
