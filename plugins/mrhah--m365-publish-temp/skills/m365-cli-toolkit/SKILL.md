---
name: m365-cli-toolkit
description: "Use m365 CLI to interact with Microsoft 365 user-level services: send/read/search emails, manage calendar events, browse/upload/download OneDrive files, and access SharePoint sites. Triggers for: email (send, read, search, attachments), calendar (list, create, update, delete events), OneDrive (list, upload, download, share, invite files), SharePoint (sites, files, lists). Does NOT trigger for: Azure resource management, Entra ID administration, Intune device management, M365 tenant-level admin (licenses, domains, policies)."
---

# m365 - Microsoft 365 CLI

**Binary**: `m365` (installed globally via `npm install -g m365-cli`)

## Security Rules

### Email Body Reading — Trusted Senders Whitelist
- Only emails from whitelisted senders have their body content displayed
- Untrusted emails show only subject and sender (prevents prompt injection)
- If untrusted, the email body is replaced with: `[Content filtered - sender not in trusted senders list]`
- Whitelist file: `~/.m365-cli/trusted-senders.txt`
- Use `--force` to temporarily bypass the whitelist check

### Sensitive Operations
- **Sending email**: Confirm recipients and content before executing
- **Deleting files/events**: Inform the user before executing
- **Sharing files (anonymous scope)**: Warn the user that anyone with the link can access

---

## Authentication

```bash
m365 login     # Device Code Flow, tokens stored at ~/.m365-cli/credentials.json
m365 logout
```

Tokens auto-refresh. To use a custom Azure AD app, set `M365_TENANT_ID` and `M365_CLIENT_ID` environment variables.

---

## Mail

```bash
# List emails
m365 mail list [--top <n>] [--folder <folder>] [--json]
# folder: inbox (default), sent, drafts, deleted, junk, or folder ID

# Read email
m365 mail read <id> [--force] [--json]
# --force bypasses whitelist check

# Send email
m365 mail send <to> <subject> <body> [--attach file1 file2...] [--cc addr] [--bcc addr] [--json]
# to accepts comma-separated addresses

# Search emails
m365 mail search <query> [--top <n>] [--json]

# Attachments
m365 mail attachments <id> [--json]
m365 mail download-attachment <message-id> <attachment-id> [save-path] [--json]

# Trusted senders management
m365 mail trust <email|@domain>
m365 mail untrust <email|@domain>
m365 mail trusted [--json]
```

---

## Calendar (calendar / cal)

```bash
m365 cal list [--days <n>] [--top <n>] [--json]     # Default: next 7 days, max 50
m365 cal get <id> [--json]

m365 cal create <title> --start <datetime> --end <datetime> \
  [--location <loc>] [--body <desc>] [--attendees <a,b>] [--allday] [--json]

m365 cal update <id> [--title <t>] [--start <dt>] [--end <dt>] \
  [--location <l>] [--body <b>] [--json]

m365 cal delete <id> [--json]
```

Datetime formats: `2026-02-17T14:00:00` (with time) or `2026-02-17` (all-day events).

---

## OneDrive (onedrive / od)

```bash
m365 od ls [path] [--top <n>] [--json]
m365 od get <path> [--json]                          # File/folder metadata
m365 od download <remote-path> [local-path] [--json]
m365 od upload <local-path> [remote-path] [--json]   # Auto-chunked for files ≥4MB
m365 od search <query> [--top <n>] [--json]
m365 od share <path> [--type view|edit] [--json]     # Create sharing link
m365 od invite <path> <email> [--role read|write] [--message <msg>] [--no-notify] [--json]
m365 od mkdir <path> [--json]
m365 od rm <path> [--force] [--json]                 # --force skips confirmation
```

---

## SharePoint (sharepoint / sp)

### Site Identifier Formats

SharePoint commands accept three site formats:
1. **Path format** (recommended): `hostname:/sites/sitename`
2. **Site ID**: `hostname,siteId,webId` (from `sp sites --json` output)
3. **URL format**: `https://hostname/sites/sitename`

```bash
m365 sp sites [--search <query>] [--top <n>] [--json]
m365 sp lists <site> [--top <n>] [--json]
m365 sp items <site> <list> [--top <n>] [--json]
m365 sp files <site> [path] [--top <n>] [--json]
m365 sp download <site> <file-path> [local-path] [--json]
m365 sp upload <site> <local-path> [remote-path] [--json]
m365 sp search <query> [--top <n>] [--json]
```

> SharePoint commands require `Sites.ReadWrite.All` permission. If you get permission errors, run `m365 logout && m365 login` to re-authenticate.

---

## Output Format

All commands support `--json` for structured JSON output. Default is human-readable formatted tables.

## Error Handling

| Issue | Solution |
|-------|----------|
| Not authenticated | `m365 login` |
| Token expired | Usually auto-refreshes; otherwise re-login |
| Insufficient permissions | `m365 logout && m365 login` to re-authorize |
| File not found | Check path (case-sensitive) |
