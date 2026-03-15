---
name: ravi-identity
description: "Check Ravi auth status and get your agent identity (email, phone, owner name). Do NOT use for reading messages (use ravi-inbox), sending email (use ravi-email-send), or credentials (use ravi-passwords or ravi-secrets)."
---

# Ravi Identity

You have access to `ravi`, a CLI that gives you your own phone number, email address, and secret store.

## Prerequisites

### Install the CLI

If `ravi` is not installed, tell the user to install it:

```bash
brew install ravi-hq/tap/ravi
```

### Check authentication

Verify you're authenticated before using any command:

```bash
ravi auth status --json
```

If `"authenticated": false`, tell the user to run `ravi auth login` (requires browser interaction — you cannot do this yourself).

## Your Identity

```bash
# Your email address (use this for signups)
ravi get email --json
# → {"id": 1, "email": "janedoe@example.com", "created_dt": "..."}

# Your phone number (use this for SMS verification)
ravi get phone --json
# → {"id": 1, "phone_number": "+15551234567", "provider": "twilio", "created_dt": "..."}

# The human who owns this account
ravi get owner --json
# → {"first_name": "Jane", "last_name": "Doe"}
```

## Switching Identities

Ravi supports multiple identities. Each identity has its own email, phone, and secrets.

### Listing identities

```bash
ravi identity list --json
```

### Setting an identity for this project

Use this when the user wants a different identity for a specific project:

1. List identities: `ravi identity list --json`
2. Set for this project (per-directory override):
   ```bash
   # Recommended: use the CLI (handles bound tokens automatically)
   ravi identity use "<uuid>"

   # Manual fallback (identity only, no bound tokens):
   mkdir -p .ravi && echo '{"identity_uuid":"<uuid>","identity_name":"<name>"}' > .ravi/config.json
   ```
   - Add `.ravi/` to `.gitignore`

All `ravi` commands in this directory will use the specified identity.

### Switching identity globally

```bash
ravi identity use "<uuid>"
```

### Creating a new identity

Only create a new identity when the user explicitly asks for one (e.g., for a
separate project that needs its own email/phone). New identities require a paid
plan and take a moment to provision.

```bash
# Auto-generated name and email (recommended — looks like a real person)
ravi identity create --json
# → name: "Sarah Johnson", email: "sarah.johnson472@ravi.app"

# Custom name, auto-generated email
ravi identity create --name "Shopping Agent" --json

# Custom email local part (domain auto-picked)
ravi identity create --name "Work Agent" --email "shopping" --json

# Full email on a specific domain (must be a domain you have access to)
ravi identity create --email "work@acme.com" --json

# List available domains
ravi domains --json
```

When name is omitted, the server generates a realistic human name like "Sarah Johnson".
The auto-generated email uses the same name: `sarah.johnson472@ravi.app`.

**Custom email rules:** 3-30 chars, lowercase alphanumeric + dots + hyphens,
must start/end with letter or number, no consecutive dots (`..`) or hyphens (`--`).
Returns HTTP 409 if the email address is already taken.

## Important Notes

- **Always use `--json`** — all commands support it. Human-readable output is not designed for parsing.
- **Auth is automatic** — token refresh happens transparently. If you get auth errors, ask the user to re-login.
- **Identity resolution** — `.ravi/config.json` in CWD takes priority over `~/.ravi/config.json`.
- **Identities are permanent** — each identity has its own email, phone, and secrets. Don't create new identities unless the user asks for it.

## Related Skills

- **ravi-inbox** — Read SMS and email messages
- **ravi-email-send** — Compose, reply, forward emails
- **ravi-email-writing** — Write professional emails with proper formatting and tone
- **ravi-contacts** — Look up or manage contacts associated with this identity
- **ravi-passwords** — Store and retrieve website credentials (domain + username + password)
- **ravi-secrets** — Store and retrieve key-value secrets (API keys, env vars)
- **ravi-login** — Sign up for and log into services, handle 2FA/OTPs
- **ravi-feedback** — Send feedback, report bugs, request features
