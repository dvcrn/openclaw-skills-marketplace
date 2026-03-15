# Risk Policy — codex-usage

## Safe defaults
- Run in read-only mode by default (`/codex_usage` checks only).
- Mutations require explicit user confirmation.
- Prefer `--dry-run` before any mutation.

## Allowed operations
- Read auth profile state from local filesystem.
- Query Codex usage endpoint over HTTPS (`chatgpt.com`) for WHAM usage.
- Update auth profile order/lastGood in detach mode when explicitly confirmed.
- Hard delete only when explicitly confirmed with `--hard-delete`.

## Denied operations
- No remote shell execution (`curl|bash`, `wget|sh`).
- No `sudo`, SSH, package installs, firewall/system changes.
- No arbitrary outbound hosts outside trusted allowlist.
- Never print full tokens or callback secrets.
