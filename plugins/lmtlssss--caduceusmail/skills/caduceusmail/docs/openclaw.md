# OpenClaw and ClawHub

☤CaduceusMail is shaped as an OpenClaw skill bundle. The root folder is the skill. `SKILL.md` uses single line JSON metadata because OpenClaw's embedded parser expects single line frontmatter keys and specifically recommends single line `metadata` JSON. OpenClaw also injects `skills.entries.<key>.env` values into `process.env` for the duration of an agent run, which is the right place for tenant secrets.

## Example config

See `examples/openclaw.config.json5`.

Canonical env keys for full runtime:

* `ENTRA_TENANT_ID`
* `ENTRA_CLIENT_ID`
* `ENTRA_CLIENT_SECRET`
* `EXCHANGE_DEFAULT_MAILBOX`
* `EXCHANGE_ORGANIZATION`
* `ORGANIZATION_DOMAIN`
* `CLOUDFLARE_API_TOKEN`
* `CLOUDFLARE_ZONE_ID`

## Shipping pattern

The recommended path is split in two:

1. First trust ceremony with `--bootstrap-auth-mode device`.
2. Daily headless operations with `--skip-m365-bootstrap` once `ENTRA_CLIENT_SECRET` is present.
3. Keep persistence opt-in: use `--persist-env` and `--persist-secrets` only when you intentionally want disk writes.

### VPS/SSH login handoff

Use `--gateway-login-handoff` during first bootstrap to attempt automatic handoff of `https://microsoft.com/devicelogin` through OpenClaw browser control.
If browser automation is unavailable on the host, the script emits a dashboard URL fallback and writes a machine-readable handoff artifact in the intel directory.

## Security posture

The first bootstrap can install Microsoft modules from PSGallery using `Install-Module` if they are missing.
The skill performs admin-level Graph/Exchange role assignment and Cloudflare DNS operations by design.

## Script resolution safety

`email_alias_fabric_ops.py` resolves `entra-exchange.sh` from this skill directory by default.
External workspace resolution is disabled unless `CADUCEUSMAIL_ALLOW_EXTERNAL_SCRIPT_RESOLUTION=1` is set.

## Why the doctor matters

The doctor tells you whether the current host looks like:

* a browser friendly workstation
* a headless sandbox that should use device auth
* a machine that is already ready for headless steady state

## Paired node model

If your OpenClaw gateway is on Linux and a macOS node is paired, you can still execute the bootstrap from the Mac side when that is operationally easier. The repo does not hardcode node execution, but the playbook in `docs/node-bootstrap.md` explains how to handle that first run cleanly.
