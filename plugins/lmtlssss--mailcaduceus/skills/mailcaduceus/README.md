# ☤MailCaduceus

☤MailCaduceus lets your OpenClaw automate an enterprise-level communications stack with one domain/mailbox combo. Inbox-reliability optimization engine: automates sender trust hardening, identity rotation, and scale-ready outreach/support flows designed to keep your mail out of junk.

Version: `4.2.0`

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
