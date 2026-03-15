---
name: Account & Authentication
description: "Account signup, login via email/OTP/wallet/biometric, token refresh, password reset, and session management."
---

# Account & Authentication

Use this skill when the user needs to sign up, log in, manage sessions, reset their password, or link a Web3 wallet.

## Available Tools

- `send_otp` — Send a one-time password to an email address | `POST /api/v1/auth/otp/send`
- `verify_otp` — Verify an OTP code and receive a verification token | `POST /api/v1/auth/otp/verify`
- `otp_rate_limit_status` — Check OTP rate limit status for the current session | `GET /api/v1/auth/otp/status`
- `signup` — Create a new account with email, password, and OTP verification token | `POST /api/v1/auth/signup`
- `login` — Login with email and password | `POST /api/v1/auth/login`
- `login_with_wallet` — Login by signing a nonce with a Web3 wallet | `POST /api/v1/auth/wallet`
- `get_wallet_nonce` — Get a nonce for wallet-based login | `GET /api/v1/auth/wallet/nonce`
- `biometric_login` — Login using biometric credentials | `POST /api/v1/auth/biometric`
- `refresh_token` — Refresh an expired access token using a refresh token | `POST /api/v1/auth/refresh`
- `reset_password` — Reset account password using OTP verification | `POST /api/v1/auth/reset-password`
- `unlock_account` — Unlock a locked account | `POST /api/v1/auth/unlock`
- `get_account` — Get current account information | `GET /api/v1/account` | Requires auth
- `update_password` — Change account password | `PUT /api/v1/account/password` | Requires auth
- `link_wallet` — Link a Web3 wallet to the account | `PUT /api/v1/account/wallet` | Requires auth
- `unlink_wallet` — Remove a linked Web3 wallet | `DELETE /api/v1/account/wallet` | Requires auth
- `logout` — Logout current session | `POST /api/v1/account/logout` | Requires auth
- `logout_all` — Logout from all sessions | `POST /api/v1/account/logout-all` | Requires auth

## Recommended Flows

### Sign Up

Create a new account via email and OTP

1. Send OTP: POST /api/v1/auth/otp/send with {email, type: "signup"}
2. Verify OTP: POST /api/v1/auth/otp/verify with {email, code, type: "signup"} — returns verification_token
3. Sign up: POST /api/v1/auth/signup with {email, password, verification_token}


### Login

Authenticate and receive access/refresh tokens

1. Login: POST /api/v1/auth/login with {email, password} — returns access_token, refresh_token
2. Use access_token as Bearer token in Authorization header for all authenticated requests
3. When access_token expires, refresh: POST /api/v1/auth/refresh with {refresh_token}


## Rules

- OTP is required for signup and password reset — always send then verify before proceeding
- Access tokens expire after 1 hour — use refresh_token to get a new one
- After 5 failed login attempts the account is locked — use /auth/unlock to recover
- Never store or log passwords — use them transiently only

## Agent Guidance

Follow these instructions when executing this skill:

- Always follow the documented flow order. Do not skip steps.
- If a tool requires authentication, verify the session has a valid bearer token before calling it.
- If a tool requires a transaction PIN, ask the user for it fresh each time. Never cache or log PINs.
- Never expose, log, or persist secrets (passwords, tokens, full card numbers, CVVs).
- If the user requests an operation outside this skill's scope, decline and suggest the appropriate skill.
- If a step fails, check the error and follow the recovery guidance below before retrying.

- To sign up a new user: first call `send_otp`, then `verify_otp`, then `signup`. Never skip OTP verification.
- To reset a password: first call `send_otp` with type "forget_password", then `verify_otp`, then `reset_password` with the verification token.
- All authenticated endpoints require a bearer token obtained from `login` or `login_with_wallet`.
- When the access token expires (1 hour TTL), call `refresh_token` with the refresh token. Do not ask the user to log in again.
- Never log, store, or repeat the user's password back to them.
- If login fails 5 times consecutively, the account locks. To unlock: call `send_otp` with type "account_unlock", then `verify_otp`, then `unlock_account` with the verification token.
