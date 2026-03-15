# Security Notes

## Scope
- Read-only usage/health checks for OpenAI Codex OAuth profiles.
- No token refresh/write actions in this skill.

## Data Handling
- Reads auth profile metadata from local `auth-profiles.json`.
- Never prints OAuth access/refresh tokens.
- Output is scrubbed for sensitive key names (`access`, `refresh`, `token`, `authorization`, `api_key`).

## Network Egress
- Usage endpoint fixed to trusted HTTPS host allowlist (`chatgpt.com`).
- If endpoint is unreachable, returns local health-only report instead of failing hard.

## Operational Safety
- No gateway stop/start operations.
- No config mutations.
- Intended for private/direct chats for profile-level checks.
