# ☤CaduceusMail 5.3.3

☤CaduceusMail lets your OpenClaw automate an enterprise-level communications stack with one domain/mailbox combo.
Inbox-reliability optimization engine: automates sender trust hardening, identity rotation, and scale-ready outreach/support flows designed to keep your mail out of junk.

Version 5.3.3 keeps that shipping surface and restores the high-impact 4.2.0 product voice while preserving scanner-facing coherence: full env/bin declarations in skill metadata, explicit privilege/persistence disclosure, and regression coverage to prevent metadata drift.

## What the stack controls

☤CaduceusMail coordinates three planes together:

1. Identity plane through Microsoft Entra and Microsoft Graph.
2. Transport plane through Exchange Online accepted domains, mailbox aliases, and RBAC.
3. DNS and authentication plane through Cloudflare records, SPF, MX, and DMARC.

That means alias lane creation, retirement, and verification happen as one operational flow instead of being scattered across separate admin panels.

## What is in 5.3.3

The repo now includes:

* a ClawHub compatible `SKILL.md`
* strict credentials templates
* a one line shell bootstrap for Microsoft 365 and Cloudflare
* a PowerShell bootstrap with `auto`, `browser`, and `device` auth modes
* a doctor that reports readiness for OpenClaw sandboxes and VPS runs
* a Graph backed `entra-exchange.sh` bridge for probe sends
* gateway-assisted Microsoft device-login handoff for VPS/SSH bootstrap runs
* smoke tests and pytest coverage for the shipping surface
* OpenClaw config examples and node bootstrap docs

## Repository layout

```text
.
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── VERSION
├── pyproject.toml
├── credentials/
├── docs/
├── examples/
├── scripts/
├── src/
└── tests/
```

## Quick start

Copy the credential templates, fill them in, then run the wrapper.

```bash
cp credentials/entra.txt.template credentials/entra.txt
cp credentials/cloudflare.txt.template credentials/cloudflare.txt

bash ./scripts/caduceusmail.sh \
  --organization-domain "example.com" \
  --mailbox "ops@example.com" \
  --bootstrap-auth-mode device
```

For headless steady state runs after the initial trust ceremony:

```bash
bash ./scripts/caduceusmail.sh \
  --organization-domain "example.com" \
  --mailbox "ops@example.com" \
  --skip-m365-bootstrap
```

Persistence is opt-in. By default the wrapper does not write runtime keys or secrets to disk.
If you explicitly want persistence, use `--persist-env` and optionally `--persist-secrets`.

For VPS-first onboarding, `--gateway-login-handoff` attempts to open Microsoft device login through OpenClaw browser controls and falls back to a dashboard URL when no local browser is available on host.

## Doctor

The doctor is the fastest way to see whether the skill is actually ready to ship.

```bash
python3 ./scripts/caduceusmail-doctor.py --json
```

It reports:

* required binaries on the host
* credentials file presence and key coverage
* whether headless steady state is possible
* whether the current environment suggests device auth
* whether the SKILL frontmatter is ClawHub safe

## OpenClaw config injection

The preferred production path is to inject secrets through `skills.entries.<skill>.env` instead of editing files inside sandboxes.

A sample config lives at `examples/openclaw.config.json5`.

## Required env and trust boundaries

For full capability, inject these keys in OpenClaw env or strict credentials files:

* `ENTRA_TENANT_ID`
* `ENTRA_CLIENT_ID`
* `ENTRA_CLIENT_SECRET`
* `EXCHANGE_DEFAULT_MAILBOX`
* `EXCHANGE_ORGANIZATION`
* `ORGANIZATION_DOMAIN`
* `CLOUDFLARE_API_TOKEN`
* `CLOUDFLARE_ZONE_ID`

This skill performs high-impact tenant and DNS operations. It can persist env/secrets only when explicitly requested with `--persist-env` or `--persist-secrets`.
The PowerShell bootstrap may install Microsoft modules from PSGallery if missing.

## Smoke tests

A smoke test ships with the repo and does not require PowerShell because it uses `--simulate-bootstrap`.

```bash
bash ./scripts/caduceusmail-sandbox-smoke.sh
```

Full pytest:

```bash
PYTHONPATH=src python3 -m pytest -q
```

## Probe sending

The new `scripts/entra-exchange.sh` wrapper and `scripts/send_mail_graph.py` helper provide the missing bridge used by lane verification and probe sending. They use Microsoft Graph app only auth against `/users/{mailbox}/sendMail` and set the `from` address to the lane alias.

## OpenClaw and ClawHub notes

This repository is intentionally shaped as a skill folder first. ClawHub stores versioned skill bundles, and OpenClaw loads skills from workspace, managed, and bundled locations. The bundle is compatible with the single line metadata requirement in `SKILL.md`, and the examples in `docs/openclaw.md` show how to inject secrets at run time and how to treat the first bootstrap differently from daily headless runs.

## License

MIT.
