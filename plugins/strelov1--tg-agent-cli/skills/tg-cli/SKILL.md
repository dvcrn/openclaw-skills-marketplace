---
name: tg-cli
description: "Manage the user's personal Telegram account directly from the command line. Use when the user asks to: read Telegram messages or chats, list dialogs or unread messages, send a message or file as themselves on Telegram, reply to or edit a specific message, delete messages, add reactions, forward messages between chats, search messages inside a chat or across all chats, join or leave a group or channel, export full chat history, mark messages as read, search for public Telegram groups, get info about a chat or user, list group members, or watch a dialog for new messages in real time. This is for the user's personal account (MTProto, not a bot). Two-step agent-friendly auth: call auth-request, get the code from the user, then call auth-complete — no interactive TTY needed."
---

# tg-cli — Agentic Telegram CLI

Standalone CLI for managing a personal Telegram account via MTProto. No subprocesses, no browser, no interactive prompts. Every command returns JSON on stdout; progress and errors go to stderr.

## Security Notes

- **Verification codes and 2FA passwords** are required only during initial authorization (`auth-request` / `auth-complete`). These are standard Telegram credentials — never share them outside of this auth flow.
- **The install script verifies SHA-256 checksums** against the official release manifest before installing the binary.
- **Source code and release artifacts** are open and auditable at [github.com/privateclaw-com/tg-cli](https://github.com/privateclaw-com/tg-cli).
- You can build from source instead of using the pre-built binary: `go install github.com/privateclaw-com/tg-cli@latest`

---

## Setup (First Run)

### Step 1: Check if configured

```bash
tg-cli config list
```

If `app-id` and `api-hash` are missing — help the user get them from [my.telegram.org/apps](https://my.telegram.org/apps):

```bash
tg-cli config set app-id <id>
tg-cli config set api-hash <hash>
```

### Step 2: Check accounts

```bash
tg-cli accounts
```

If no authorized accounts — start auth (see **Authorization** below).

---

## Authorization (Two Steps, No stdin)

### Step 1 — Request code

```bash
tg-cli auth-request +12025551234
```

Returns `{"status":"code_sent","phone":"+12025551234"}`. A verification code is sent to the user's Telegram app (or SMS).

Tell the user: **"Check your Telegram — I've sent a code. Please share it with me."**

### Step 2 — Complete auth

```bash
# Without 2FA
tg-cli auth-complete +12025551234 --code 12345

# With 2FA password
tg-cli auth-complete +12025551234 --code 12345 --password MySecret2FA
```

Returns `{"status":"authorized","phone":"...","username":"..."}`.

If the user has 2FA enabled and you didn't pass `--password`, re-run with it.

---

## Commands

### Account info

```bash
tg-cli me
tg-cli status
tg-cli accounts
tg-cli accounts use +12025551234
```

### List dialogs

```bash
# All dialogs
tg-cli dialogs

# Only unread
tg-cli dialogs --unread

# Limit results
tg-cli dialogs --limit 50
```

Output:
```json
[
  {"id": 123, "name": "Alice", "username": "alice", "type": "user", "unread_count": 3},
  {"id": 456, "name": "Dev Team", "type": "supergroup", "unread_count": 0}
]
```

Types: `user`, `group`, `supergroup`, `channel`.

### Read messages

```bash
tg-cli read alice
tg-cli read team-chat
tg-cli read @username
tg-cli read +12025551234
tg-cli read team-chat --offset 1000   # paginate backwards
tg-cli read team-chat --since 1h      # messages from last 1 hour
tg-cli read team-chat --since 30m     # messages from last 30 minutes
tg-cli read team-chat --since 7d      # messages from last 7 days
```

Output:
```json
{"messages": [{"id": 1, "who": "Alice", "when": "2024-01-01T10:00:00Z", "text": "Hello"}], "offset": 1}
```

Use `offset` value from response as `--offset` to load older messages.

### Send message

```bash
tg-cli send @alice "Hello!"
tg-cli send team-chat "Build is done ✅"
tg-cli send +12025551234 "Hey there"
```

### Reply to a message

```bash
tg-cli reply team-chat 12345 "Got it, thanks!"
tg-cli reply @alice 99 "Sure, see you then"
```

### Edit a message

```bash
tg-cli edit team-chat 12345 "Updated text here"
```

Only works on your own messages.

### Delete messages

```bash
tg-cli delete team-chat 12345
tg-cli delete team-chat 100 101 102   # delete multiple
```

### React to a message

```bash
tg-cli react team-chat 12345 👍
tg-cli react @alice 99 ❤️
```

### Forward a message

```bash
tg-cli forward team-chat 12345 @alice
tg-cli forward inbox 99 project-chat
```

### Send a file

```bash
tg-cli send-file @alice /path/to/report.pdf
tg-cli send-file team-chat ./screenshot.png
```

### Mark as read

```bash
tg-cli mark-read team-chat
```

### Search messages in a dialog

```bash
tg-cli search team-chat "deploy" --limit 20
```

Output:
```json
{"results": [...], "total": 5, "query": "deploy", "dialog": "team-chat"}
```

### Search messages across all chats

```bash
tg-cli search-all "deployment failed" --limit 20
```

Output:
```json
{"results": [...], "total": 3, "query": "deployment failed"}
```

### Get info about a user, group, or channel

```bash
tg-cli info @alice
tg-cli info team-chat
tg-cli info @golang_digest
```

Output for a channel:
```json
{"type": "supergroup", "id": 123, "title": "Team Chat", "username": "teamchat", "members": 42, "description": "..."}
```

### List group members

```bash
tg-cli members team-chat
tg-cli members @golang_digest --limit 50
```

Output:
```json
{"members": [{"id": 1, "username": "alice", "first_name": "Alice"}], "total": 1}
```

### Watch for new messages

```bash
tg-cli watch team-chat             # poll every 5s (default)
tg-cli watch @alice --interval 10  # poll every 10s
```

Prints each new message as a JSON object to stdout as it arrives. Runs until Ctrl+C or `--timeout`.

### Search public groups/channels

```bash
tg-cli search-groups "golang" --limit 10
```

Output:
```json
{"results": [{"id": 1, "title": "Golang", "username": "golang", "type": "supergroup", "members": 50000}], "total": 1}
```

### Join a group or channel

```bash
# By username
tg-cli join @golang_digest

# By t.me invite link
tg-cli join https://t.me/+AbCdEfGhIjK
```

### Leave a group or channel

```bash
tg-cli leave golang_digest
tg-cli leave team-chat
```

Works for channels, supergroups, and regular groups.

### Export full chat history

```bash
# Full export — can take a while for large chats
tg-cli export team-chat > history.json

# Last N messages only
tg-cli export team-chat --limit 500 > recent.json
```

Progress is printed to stderr. Output:
```json
{
  "account": "+12025551234",
  "dialog": "team-chat",
  "total_messages": 1234,
  "incomplete": false,
  "messages": [{"id": 1, "who": "Alice", "when": "...", "text": "..."}]
}
```

`"incomplete": true` means the export was interrupted (FLOOD_WAIT or timeout) — partial data is returned.

---

## Multiple Accounts

```bash
tg-cli --account +19005551234 dialogs
tg-cli --account +79001234567 send @alice "Hello from my Russian number"
```

Set a default account:
```bash
tg-cli accounts use +12025551234
```

---

## Timeout

```bash
tg-cli --timeout 30 dialogs   # 30-second timeout
```

---

## Config

- Config file: `~/.tg-cli/config.json`
- Sessions: `~/.tg-cli/sessions/<phone>/session.json`

```bash
tg-cli config list
tg-cli config set app-id 12345
tg-cli config set api-hash abc123...
tg-cli config set default-account +12025551234
```

---

## Common Errors

| Error | Meaning | Fix |
|-------|---------|-----|
| `app-id and api-hash are required` | Not configured | `tg-cli config set app-id ...` |
| `auth code expired` | 5-min TTL on code | Re-run `auth-request` |
| `2FA required` | User has 2FA | Re-run `auth-complete` with `--password` |
| `cannot find "..."` | Unknown dialog name | Try `@username` format or full name |
| `session invalid or expired` | Session gone | Re-authorize with `auth-request` / `auth-complete` |
