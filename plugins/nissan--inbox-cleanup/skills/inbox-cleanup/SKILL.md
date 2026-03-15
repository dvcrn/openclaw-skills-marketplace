---
name: inbox-cleanup
description: "IMAP bulk email triage — pattern-based delete/archive with dry-run mode. Use when: cleaning up large email inboxes, bulk-deleting emails from specific senders or domains, archiving newsletter/digest emails, triaging email by sender domain or subject patterns. Supports IMAP STARTTLS (e.g. Proton Bridge), dry-run preview, YAML/JSON config for patterns, and processes UIDs (not sequence numbers) for reliable bulk ops."
---

# inbox-cleanup

Bulk IMAP email triage: classify → delete/archive by sender domain, subject keywords, or custom patterns.

## Key files

- `scripts/inbox_cleanup.py` — main cleanup script (dry-run by default)
- `scripts/config_example.yaml` — pattern config template

## Quick start

```bash
# Dry run (preview only — no changes)
python3 scripts/inbox_cleanup.py --config my_patterns.yaml --dry-run

# Live run
python3 scripts/inbox_cleanup.py --config my_patterns.yaml
```

## Required env vars

```bash
IMAP_HOST=127.0.0.1          # IMAP server host
IMAP_PORT=1143               # IMAP port (use 993 for direct SSL, 1143 for Proton Bridge)
IMAP_USER=you@example.com    # IMAP username
IMAP_PASSWORD=yourpassword   # IMAP password
IMAP_STARTTLS=true           # true for STARTTLS (Proton Bridge), false for direct SSL
IMAP_SKIP_CERT_VERIFY=true   # true for self-signed certs (Proton Bridge)
ARCHIVE_FOLDER=Archive        # Folder name to archive to (must exist in mailbox)
```

Or use `--imap-*` CLI flags. See `python3 scripts/inbox_cleanup.py --help`.

## Config file format (YAML)

```yaml
delete_domains:
  - github.com
  - noreply.github.com
  - slack.com

archive_domains:
  - notion.so
  - coinbase.com

archive_keywords:
  - newsletter
  - digest
  - weekly roundup

delete_subject_patterns:
  - "^\\[GitHub\\]"

leave_domains:
  - important-bank.com
```

## Design notes

- **UIDs not sequence numbers**: The script always uses `UID FETCH`/`UID STORE` to
  avoid message-renumbering bugs when messages are deleted mid-batch.
- **Dry-run by default**: Always preview before committing. Pass `--no-dry-run` to apply.
- **Batch fetching**: Headers fetched in batches of 50 for large inboxes. One-at-a-time
  fetch mode available with `--one-at-a-time` for reliable UID tracking.
- **Progress logging**: Stdout log with counts per domain and final report JSON.
- **STARTTLS support**: Needed for Proton Bridge (port 1143 with self-signed cert).

## Secret management

Credentials via env vars or 1Password:

```bash
# Via env vars
export IMAP_PASSWORD="$(op read 'op://Vault/Email Account/password')"
python3 scripts/inbox_cleanup.py --config patterns.yaml
```
