---
name: tapauth
description: "Get delegated access for AI agents via TapAuth — the trust layer between humans and AI agents. Use when your agent needs to access GitHub, Google Workspace, Gmail, Linear, or other OAuth providers on behalf of a user. One API call to create an auth request, user approves in browser, agent gets scoped tokens. No API key required."
---

> Generated note: shared plugin assets for this package live at the plugin root. Common local references were rewritten when they appeared in backticks or markdown links.

# TapAuth — Delegated Access for AI Agents

TapAuth lets your agent get OAuth tokens from users without handling credentials directly.
The user approves in their browser. You get a scoped token. That's it.

## Quickest Start: The CLI

The `tapauth` CLI script is bundled with this skill. Save it and make it executable:

```bash
# Copy from this skill directory and make executable
cp /path/to/skill/tapauth ./tapauth
chmod +x tapauth
```

Then use it inline with command substitution:

```bash
# One line. Get a token. Use it.
curl -H "Authorization: Bearer $(./tapauth google drive.readonly)" \
  https://www.googleapis.com/drive/v3/files
```

**First run:** Creates a grant, prints an approval URL to stderr, polls until the user approves, then outputs the token to stdout.

**Subsequent runs:** Returns the cached token instantly — no network call if the token hasn't expired. Automatically refreshes expired tokens.

```bash
# Example: access Google Calendar
curl -H "Authorization: Bearer $(./tapauth google calendar.events)" \
  https://www.googleapis.com/calendar/v3/calendars/primary/events
```

**Environment variables:**
- `TAPAUTH_BASE_URL` — Override the base URL (default: `https://tapauth.ai`)
- `TAPAUTH_HOME` — Override the cache directory (default: `./.tapauth`)

**Security:** Tokens are cached in `.tapauth/` (directory mode 700, files mode 600). Grant secrets are stored locally alongside tokens for automatic refresh.

## The API Flow (v1)

### Step 1: Create a Grant

```bash
# JSON
curl -X POST https://tapauth.ai/api/v1/grants \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "github",
    "scopes": ["repo", "read:user"],
  }'

# Or form-urlencoded (what the CLI uses)
curl -X POST https://tapauth.ai/api/v1/grants \
  -H "Accept: text/plain" \
  --data-urlencode "provider=github" \
  --data-urlencode "scopes=repo,read:user"
```

JSON response:
```json
{
  "grant_id": "abc123",
  "grant_secret": "gs_live_xxxx",
  "approve_url": "https://tapauth.ai/approve/abc123"
}
```

Text response (with `Accept: text/plain`):
```
TAPAUTH_GRANT_ID=abc123
TAPAUTH_GRANT_SECRET=gs_live_xxxx
TAPAUTH_APPROVE_URL=https://tapauth.ai/approve/abc123
```

**Important:** Save `grant_secret` — you need it to retrieve the token. It's only returned once.

### Step 2: User Approves

Show the user the `approve_url`. They'll see:
- Which agent is requesting access
- Which provider and scopes
- Options: approve with full scopes, read-only, or time-limited (1hr/24hr/7d/forever)

The approval URL expires after **10 minutes**. Create a new grant if it expires.

### Step 3: Retrieve the Token

Poll until the user approves. Use Bearer auth with the grant_secret:

```bash
# Plain text (just the token)
curl https://tapauth.ai/api/v1/token/{grant_id} \
  -H "Authorization: Bearer <grant-secret>"

# .env format (token + expiry + grant ID for caching)
curl https://tapauth.ai/api/v1/token/{grant_id}.env \
  -H "Authorization: Bearer <grant-secret>"

# JSON format
curl https://tapauth.ai/api/v1/token/{grant_id}.json \
  -H "Authorization: Bearer <grant-secret>"
```

| HTTP | Meaning |
|------|---------|
| 200 | Token returned in response body |
| 202 | Pending — user hasn't approved yet. Poll again in 2-5 seconds |
| 401 | Invalid or missing grant_secret |
| 404 | Grant not found |
| 410 | Grant expired, revoked, denied, or link expired |

JSON response (`.json`):
```json
{
  "token": "gho_xxxx",
  "expires": "2026-03-05T17:00:00Z",
  "provider": "github",
  "grant_id": "abc123"
}
```

Env response (`.env`):
```
TAPAUTH_TOKEN=gho_xxxx
TAPAUTH_EXPIRES=1741194000
TAPAUTH_GRANT_ID=abc123
TAPAUTH_GRANT_SECRET=gs_live_xxxx
```

## Revocation & Token Lifetimes

TapAuth uses zero-knowledge encryption — tokens are encrypted with your `grant_secret`, which TapAuth never stores. This means:

- **TapAuth cannot revoke tokens at the provider level.** We literally cannot decrypt them.
- When a grant expires, we delete the encrypted ciphertext without ever reading it.
- For short-lived token providers (Google ~1hr, Linear ~1hr, Sentry ~8hr): tokens expire naturally.
- For never-expiring tokens (GitHub, Slack, Vercel, Notion): manually revoke in your provider settings if needed.

We recommend setting `expires_in` for grants requesting long-lived tokens.

## Quick Reference

| What | Endpoint | Method |
|------|----------|--------|
| Create grant | `/api/v1/grants` | POST |
| Get token | `/api/v1/token/{id}` | GET |
| Get token (.env) | `/api/v1/token/{id}.env` | GET |
| Get token (.json) | `/api/v1/token/{id}.json` | GET |
| CLI | `$(tapauth <provider> <scopes>)` | — |

No API key needed. No signup needed. The user's approval is the only gate.

## Supported Providers

See the `references/` directory for provider-specific scopes, examples, and gotchas:

- **GitHub** (`github`) → `../../references/github.md` — repos, issues, PRs, user data, gists, workflows
- **Google** (`google`) → `../../references/google.md` — Gmail, Drive, Calendar, Sheets, Docs, Contacts (all scopes)
- **Gmail** → `../../references/gmail.md` — read, send, manage emails (uses `google` provider)
- **Google Drive** (`google_drive`) → `../../references/google_drive.md` — focused Drive-only access
- **Google Contacts** (`google_contacts`) → `../../references/google_contacts.md` — view and manage contacts
- **Google Sheets** (`google_sheets`) → `../../references/google_sheets.md` — read and write spreadsheets
- **Google Docs** (`google_docs`) → `../../references/google_docs.md` — read and write documents
- **Linear** (`linear`) → `../../references/linear.md` — issues, projects, teams
- **Vercel** (`vercel`) → `../../references/vercel.md` — deployments, projects, env vars, domains
- **Notion** (`notion`) → `../../references/notion.md` — pages, databases, search
- **Slack** (`slack`) → `../../references/slack.md` — channels, messages, users, files
- **Sentry** (`sentry`) → `../../references/sentry.md` — error tracking, projects, organizations
- **Asana** (`asana`) → `../../references/asana.md` — tasks, projects, workspaces

> **Tip:** The focused Google providers (`google_drive`, `google_sheets`, etc.) show simpler consent screens.
> Use them when you only need one Google service. Use `google` when you need multiple services.

## Provider Discovery

To programmatically list all available providers and their valid scopes:

```bash
curl https://tapauth.ai/api/providers
```

This returns each provider with its ID, name, category, available scopes, and whether token refresh is supported.

## Provider Notes

- **GitHub:** Tokens use OAuth app authentication. The `repo` scope grants read/write access to repositories. Repo creation requires the user to have appropriate GitHub permissions. Some operations available with GitHub PATs may not work with OAuth tokens.
- **Google:** All Google providers support automatic token refresh. Use focused providers (google_drive, google_sheets, etc.) for simpler consent screens when you only need one service.
- **Discord:** Uses user OAuth tokens (not bot tokens). Tokens expire after ~7 days with automatic refresh. The `guilds` scope returns server list only — no channel/message access.
- **Vercel/Slack/Notion:** These are integration-level providers — scopes are fixed at installation time, not per-request.

## CLI Tool

For a complete grant-creation + polling + caching flow, use the `tapauth` CLI:

```bash
# Install: copy packages/cli/tapauth to your PATH
TOKEN=$(tapauth github repo,read:user)

# First run: creates grant, shows approval URL, polls until approved
# Subsequent runs: returns cached token (auto-refreshes when expired)
```

The CLI stores credentials in `.tapauth/` (mode 700) with per-provider-scope cache files.

## Common Patterns

### Ask the user to approve, then proceed
```
1. Create grant for the provider/scopes you need
2. Tell the user: "Please approve access at: {approve_url}"
3. Poll GET /api/v1/token/{id} (with Bearer auth) every 3 seconds
4. Once approved, use the token for API calls
```

### Handle expiry gracefully
If you get `link_expired` (410), just create a new grant and ask the user again.
If you get `revoked`, the user withdrew access — don't retry.

### Scope selection
Request the minimum scopes you need. Users see exactly what you're asking for
and can approve with reduced permissions. Less scope = more trust = higher approval rate.
