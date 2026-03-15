---
name: moss-platform-quick-auth
description: "Handle Moss platform authentication via Quick Auth endpoints and return usable credentials. Use when a user provides an email and asks to register/login, send verification code, complete code-based auth, or use API no-code auth (api-register/api-login) to get access_token/refresh_token/api_key."
---

# Moss Platform Quick Auth

Execute authentication against:

- Base URL: `https://<host>/studio-api/v1/auth/quick/*`

Use `curl` via shell for deterministic API calls.

## Inputs to Collect

Collect these before calling endpoints:

- `host` (example: `sotatts.online`)
- `email`
- Optional: `code` (for code-based flow)
- Optional: user intent (`new user` / `existing user` / `auto`)

## Flow A: Code-based Quick Auth

### Step 1: Send code

```bash
curl -sS -X POST "https://<host>/studio-api/v1/auth/quick/send-code" \
  -H 'Content-Type: application/json' \
  --data '{"email":"<email>"}'
```

Expected success fields:

- `message`
- `expires_in`
- `cooldown_in`

If `IN_COOLDOWN`, wait and retry.

### Step 2: Login or register

Preferred decision logic:

1. Try `/quick/login` first when user status unknown
2. If `USER_NOT_EXIST`, call `/quick/register`

Login:

```bash
curl -sS -X POST "https://<host>/studio-api/v1/auth/quick/login" \
  -H 'Content-Type: application/json' \
  --data '{"email":"<email>","code":"<code>"}'
```

Register:

```bash
curl -sS -X POST "https://<host>/studio-api/v1/auth/quick/register" \
  -H 'Content-Type: application/json' \
  --data '{"email":"<email>","code":"<code>"}'
```

On register success, persist `temp_password` immediately (returned once).

## Flow B: API Auth (No Code)

Use for server-to-server or user-approved no-interaction login.

### Try login first

```bash
curl -sS -X POST "https://<host>/studio-api/v1/auth/quick/api-login" \
  -H 'Content-Type: application/json' \
  --data '{"email":"<email>"}'
```

If `USER_NOT_EXIST`, call register:

```bash
curl -sS -X POST "https://<host>/studio-api/v1/auth/quick/api-register" \
  -H 'Content-Type: application/json' \
  --data '{"email":"<email>"}'
```

Expected fields:

- `user_id`
- `access_token`
- `refresh_token`
- `expires_in`
- `api_key` (should be present)
- `temp_password` (register only; store once)

## Output Contract

Return to user:

- Which endpoint was used
- Result status (`login success` / `register success` / `error code`)
- `user_id`
- `expires_in`
- Credentials (`access_token`, `refresh_token`, `api_key`, `temp_password` if present)

If token-auth endpoints fail unexpectedly (`UNAUTHORIZED` after successful auth), report as backend inconsistency and include endpoint + response payload for debugging.

## Error Handling Map

- `USER_NOT_EXIST` → switch login → register
- `EMAIL_EXISTS` → switch register → login
- `INVALID_CODE` → ask user for correct code
- `CODE_EXPIRED` / `CODE_NOT_FOUND` → re-send code then retry
- `IN_COOLDOWN` → wait `cooldown_in` seconds
- `ACCOUNT_BANNED` → stop and notify user

## Security & UX Rules

- Never claim mailbox access without explicit integration.
- Mask credentials by default in summaries unless user explicitly asks for full raw values.
- Warn that `temp_password` is one-time display and must be saved.
- Keep API calls idempotent where possible and avoid tight resend loops.