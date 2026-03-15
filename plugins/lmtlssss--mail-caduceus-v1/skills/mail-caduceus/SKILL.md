---
name: mail-caduceus
description: "Stop landing in junk. Mail Caduceus automates inbox reliability at scale with branded sender lanes, trust hardening, and full lifecycle control from one mailbox."
homepage: https://github.com/lmtlssss/mail-caduceus
---

# Mail Caduceus

Mail Caduceus is a shippable skill for enterprise-grade alias/domain control on top of a single Microsoft 365 mailbox and Cloudflare DNS zone.

## Innovation Summary

This skill makes one mailbox + one domain behave like an enterprise email control plane by coordinating:
- Entra/Graph authorization
- Exchange transport + alias lifecycle
- Cloudflare DNS/auth posture

That means plug-and-play lane creation, verification, and optimization without mailbox sprawl.

## What It Does

- Bootstraps Microsoft Graph + Exchange app permissions with one interactive sign-in.
- Audits credential posture across Graph, Exchange RBAC, and Cloudflare token scope.
- Optimizes root-domain mail posture (SPF, MX, DMARC) with safe defaults.
- Provisions reply-capable or no-reply alias lanes under subdomains.
- Verifies lane readiness (accepted domain, alias attach, Graph state, DNS profile).
- Stores operation outputs atomically for resumable state and operator visibility.

## Hard Rules

- Never send group emails from one operation.
- Never send one message to multiple recipients at once.
- Treat no-reply lanes as intentional non-receiving identities (no MX + SPF -all profile).
- Delete defaults are reply-safe: aliases are retired with fallback continuity unless explicitly hard-removed.

## Quick Start

```bash
# 1) Copy strict credential templates
cp {baseDir}/credentials/entra.txt.template {baseDir}/credentials/entra.txt
cp {baseDir}/credentials/cloudflare.txt.template {baseDir}/credentials/cloudflare.txt

# 2) Edit values in both .txt files

# 3) Run Mail Caduceus (autoloads credentials/*.txt)
{baseDir}/scripts/mail-caduceus.sh \
  --organization-domain "northorizon.ca"
```

## Dry Run First

```bash
{baseDir}/scripts/mail-caduceus.sh \
  --tenant-id "<entra-tenant-id>" \
  --client-id "<entra-app-client-id>" \
  --organization-domain "northorizon.ca" \
  --mailbox "john@northorizon.ca" \
  --dry-run
```

## Lane Provisioning

```bash
# Reply-capable lane
python3 {baseDir}/scripts/email_alias_fabric_ops.py provision-lane \
  --mailbox "john@northorizon.ca" \
  --local "support" \
  --domain "support-reply.northorizon.ca" \
  --send-to "edge0100@icloud.com"

# No-reply lane
python3 {baseDir}/scripts/email_alias_fabric_ops.py provision-lane \
  --mailbox "john@northorizon.ca" \
  --local "support" \
  --domain "support-noreply.northorizon.ca" \
  --no-reply
```

## Retire Lane With Reply Fallback (Recommended)

```bash
# Keeps reply continuity by default (fallback mailbox defaults to --mailbox)
python3 {baseDir}/scripts/email_alias_fabric_ops.py retire-lane \
  --mailbox "john@northorizon.ca" \
  --alias-email "support@support-reply.northorizon.ca"

# Explicitly move fallback replies to another mailbox
python3 {baseDir}/scripts/email_alias_fabric_ops.py retire-lane \
  --mailbox "john@northorizon.ca" \
  --alias-email "support@support-reply.northorizon.ca" \
  --fallback-mailbox "inbox@northorizon.ca"
```

Hard-delete (no fallback continuity):

```bash
python3 {baseDir}/scripts/email_alias_fabric_ops.py control-json --ops-json \
  '{"action":"alias.remove","mailbox":"john@northorizon.ca","email":"support@support-reply.northorizon.ca","preserve_reply":false}'
```

Important:
- Fallback continuity requires the alias domain to remain routable (accepted domain + inbound DNS/MX where applicable).
- If you remove the domain plane itself, replies to that old address will still fail.

## Verify Lane

```bash
python3 {baseDir}/scripts/email_alias_fabric_ops.py verify-lane \
  --mailbox "john@northorizon.ca" \
  --alias-email "support@support-reply.northorizon.ca" \
  --domain "support-reply.northorizon.ca"
```

## Sandbox Smoke Test

```bash
bash {baseDir}/scripts/mail-caduceus-sandbox-smoke.sh
```

## Credentials and Scope Notes

- Strict autoload format:
  - File names: `credentials/entra.txt`, `credentials/cloudflare.txt`
  - First non-empty line must be: `MAIL_CADUCEUS_CREDENTIALS_V1`
  - Remaining lines must be strict `KEY=VALUE` pairs (no unsupported keys)
  - Templates are included in this skill folder as `*.txt.template`
- `mail-caduceus-bootstrap.ps1.txt` is a publish-safe PowerShell source template.
- At runtime, `mail-caduceus.sh` materializes it into a temporary `.ps1` file and executes it.
- Override paths with:
  - `MAIL_CADUCEUS_BOOTSTRAP_SCRIPT`
  - `MAIL_CADUCEUS_FABRIC_SCRIPT`
  - `MAIL_CADUCEUS_ENV_FILE`
  - `MAIL_CADUCEUS_INTEL_DIR`
  - `MAIL_CADUCEUS_CREDENTIALS_DIR`
  - `MAIL_CADUCEUS_ALLOW_EXTERNAL_SCRIPT_RESOLUTION` (default: disabled)

Delete behavior toggles:
- `EMAIL_ALIAS_FABRIC_DELETE_PRESERVE_REPLY_DEFAULT=true|false` (default: `true`)
- `EMAIL_ALIAS_FABRIC_FALLBACK_MAILBOX=<mailbox@domain>` (optional default fallback target)

Persistence toggles:
- `--persist-env` enables writing non-secret runtime keys to `ENV_FILE`.
- `--persist-secrets` enables writing secret values to `ENV_FILE` (opt-in only).
- Default mode is non-persistent: no `.env` writes.

## Sign-In Model (Important)

- First-time bootstrap (permission grants/admin consent/Exchange RBAC):
  - Interactive PowerShell sign-in is typically required.
- Steady-state operations after bootstrap is complete:
  - Fully headless is supported with `ENTRA_CLIENT_SECRET` and `--skip-m365-bootstrap`.
- Recommended production flow:
  - Perform one admin bootstrap once, then run headless for daily operations.

## Security Posture (v1.0.0)

- External script resolution is scope-locked by default.
- Credential autodiscovery is scope-locked to this skill directory unless explicitly overridden.
- Bootstrap artifacts redact generated client-secret values before writing state JSON.
- Intel/state output files are written with restrictive permissions (`700` dir, `600` files where supported).

## Benefits

- One mailbox can run many clean identity lanes safely.
- Domain and alias lifecycle can be automated end-to-end.
- Full state awareness reduces operator guesswork.
- Useful for support, sales, outreach, and transactional messaging with explicit no-reply/reply modes.
- Built for personalized, high-volume outreach with controllable identity variables (display name, alias, subdomain).
- Reduces spam-risk behavior by enforcing single-recipient operations and lane-specific posture.

## Outcome

Mail Caduceus provides Fortune-500-style email operations from a lightweight stack:
- one domain
- one mailbox
- one bootstrap command
- full lifecycle control
