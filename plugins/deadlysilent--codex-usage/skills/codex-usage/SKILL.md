---
name: codex-usage
description: "DEPRECATED shim skill for /codex_usage. Use codex-profiler instead; codex-usage is no longer the maintained path."
---

> ⚠️ **Deprecated:** `codex-usage` is no longer maintained as a standalone skill.
> Use **codex-profiler** for all ongoing `/codex_usage` and `/codex_auth` operations.

Run `scripts/codex_usage.py` to produce a Codex profile report discovered from local auth profiles.

## Safe defaults
- `/codex_usage` is read-only.
- For mutations, require explicit confirmation and prefer `--dry-run` first.
- See `RISK.md` for allowed/denied operation boundaries.

## UX requirements (cross-channel)
Before running the script for a user-triggered `/codex_usage` request, send an immediate progress note as a separate message:
- "Running Codex usage checks now…"

Then send final usage result when complete (do not skip the progress note).

Delivery rule:
- If progress note is sent via a channel message tool call, send the final result via the same channel message tool path too (same target/session), then return `NO_REPLY` to avoid split/mismatched delivery.
- Do not mix progress via tool + final via plain assistant reply.

### Interaction adapter
- If inline buttons are supported: show selector buttons (default / all / discovered profiles).
- If inline buttons are not supported: show text menu fallback (`default | all | <profile>`).
- Apply duplicate-request suppression per user for ~20s to avoid accidental spam retries.

## Commands
- `/codex_usage` → **MUST** return selector buttons first (default / all / discovered profiles)
- `/codex_usage default`
- `/codex_usage all`
- `/codex_usage <profile>`
- `/codex_usage delete <profile>` (must require explicit confirmation before mutation)

## How to run
From workspace root:

```bash
python3 skills/codex-usage/scripts/codex_usage.py --profile all --timeout-sec 25 --retries 1 --debug
python3 skills/codex-usage/scripts/codex_usage.py --profile all --format text
```

Profile-specific examples:

```bash
python3 skills/codex-usage/scripts/codex_usage.py --profile default --timeout-sec 25 --retries 1 --debug
python3 skills/codex-usage/scripts/codex_usage.py --profile openai-codex:default --timeout-sec 25 --retries 1 --debug
python3 skills/codex-usage/scripts/codex_usage.py --profile <suffix> --timeout-sec 25 --retries 1 --debug
```

Delete examples (with safeguards):

```bash
# preview only (required guard response without --confirm-delete)
python3 skills/codex-usage/scripts/codex_usage.py --delete-profile openai-codex:mine

# safe preview with explicit confirm but no file mutation
python3 skills/codex-usage/scripts/codex_usage.py --delete-profile openai-codex:mine --confirm-delete --dry-run

# safer default mutation: detach from order/lastGood only (keeps token/profile entry)
python3 skills/codex-usage/scripts/codex_usage.py --delete-profile openai-codex:mine --confirm-delete

# permanent delete: remove profile + usage entries (creates backup first)
python3 skills/codex-usage/scripts/codex_usage.py --delete-profile openai-codex:mine --confirm-delete --hard-delete
```

## Safety posture
- No remote shell execution (`curl|bash`, `wget|sh`) is allowed by this skill.
- No `sudo`, SSH, or system service mutations are performed by this skill.
- Network calls are restricted to trusted Codex usage endpoint host allowlist (`chatgpt.com` over HTTPS).
- Never print full tokens; treat callback/token material as sensitive.

## Notes
- Reads OAuth credentials from `~/.openclaw/agents/main/agent/auth-profiles.json` by default (override via `--auth-path`).
- Uses Codex usage endpoint: `https://chatgpt.com/backend-api/wham/usage`.
- Endpoint is restricted to trusted HTTPS host allowlist (currently `chatgpt.com`).
- If endpoint is unreachable, script falls back to local health-only output (no hard failure).
- If endpoint returns `401`, script reports `auth_not_accepted_by_usage_endpoint` and keeps local profile health output instead of crashing.
- `401` in this path usually indicates the endpoint rejected current OAuth/session token format (not a missing Codex CLI install).
- Injects headers expected by Codex usage probe: `Authorization`, `ChatGPT-Account-Id` (when present), `User-Agent: CodexBar`.
- Reports local profile health (expiry, last used, error/rate-limit counters) + remote windows (5h/week), allowed/limit-reached status.
- Reports user-friendly reset formatting (`reset_in`, `reset_at` in host local timezone).
- Supports retries/timeouts and debug metadata (attempt, elapsed_ms, status) for diagnosis.
- Includes top-level `summary`, `formatted_profiles`, and `suggested_user_message` fields to simplify slash-command response formatting.
- Preferred strict output block format (newline-based, no `|` separators):
  - `Profile: %name%`
  - `Usable: ✅/❌`
  - `Limited: ✅/❌`
  - `5h Left: %remaining left`
  - `5h Reset: dd/mm/yyyy, hh:mm`
  - `5h Time left: x Days, y Hours, z Minutes`
  - `Week Left: %remaining left`
  - `Week Reset: dd/mm/yyyy, hh:mm`
  - `Week Time left: x Days, y Hours, z Minutes`
  - Separate profile blocks with a blank line.
- Never print full tokens.
