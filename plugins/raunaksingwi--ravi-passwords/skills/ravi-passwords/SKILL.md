---
name: ravi-passwords
description: "Store and retrieve website credentials — E2E encrypted password manager for domain/username/password entries. Do NOT use for API keys/secrets (use ravi-secrets) or reading messages (use ravi-inbox)."
---

# Ravi Passwords

Store and retrieve passwords for services you sign up for. Sensitive fields (username, password, notes) are E2E encrypted — the CLI handles encryption/decryption transparently. Domain is stored in plaintext for lookup.

## Commands

```bash
# Create entry (auto-generates password if --password not given)
ravi passwords create example.com --json
ravi passwords create example.com --username "me@example.com" --password 'S3cret!' --json

# List all entries
ravi passwords list --json

# Retrieve (decrypted)
ravi passwords get <uuid> --json

# Update
ravi passwords update <uuid> --password 'NewPass!' --json

# Delete
ravi passwords delete <uuid> --json

# Generate a password without storing it
ravi passwords generate --length 24 --json
# -> {"password": "xK9#mL2..."}
```

**Create flags:** `--username`, `--password`, `--notes`, `--generate`, `--length` (default 16), `--no-special`, `--no-digits`, `--exclude-chars`

## JSON Shapes

**`ravi passwords list --json`:**
```json
[
  {
    "uuid": "uuid",
    "domain": "example.com",
    "username": "me@example.com",
    "created_dt": "2026-02-25T10:30:00Z"
  }
]
```

**`ravi passwords get <uuid> --json`:**
```json
{
  "uuid": "uuid",
  "domain": "example.com",
  "username": "me@example.com",
  "password": "S3cret!",
  "notes": "",
  "created_dt": "2026-02-25T10:30:00Z"
}
```

## Important Notes

- **E2E encryption is transparent** — the CLI encrypts credential fields before sending and decrypts on retrieval. You see plaintext.
- **Domain cleaning** — `ravi passwords create` auto-cleans URLs to base domains (e.g., `https://mail.google.com/inbox` becomes `google.com`).
- **Always use `--json`** — human-readable output is not designed for parsing.

## Related Skills

- **ravi-secrets** — Store API keys and env vars (key-value secrets, not website credentials)
- **ravi-login** — End-to-end signup/login workflows that store credentials here
- **ravi-identity** — Get your email address for the username field
- **ravi-feedback** — Report password manager issues or suggest improvements
