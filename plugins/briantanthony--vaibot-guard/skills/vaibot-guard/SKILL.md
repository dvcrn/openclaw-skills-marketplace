---
name: vaibot-guard
description: "Policy-gated execution + tamper-evident audit trail for VAIBot/OpenClaw operations. Use to precheck/deny/require-approval before shell execution, and to produce signed receipts (hash-chained logs) for execution decisions and outcomes."
---

# VAIBot Guard (OpenClaw Skill)

This skill provides a **local policy decision service** plus a `vaibot-guard` CLI that enforces **pre-execution checks** and writes a **tamper-evident audit log**.

## Deployment modes

- **Local workstation mode (recommended default):** run `vaibot-guard` as a **systemd user service** (`systemctl --user`), optionally coupled to `openclaw-gateway.service` so it starts whenever OpenClaw starts (typically at login).
- **VPS / production mode:** run `vaibot-guard` as a **systemd system service** (`sudo systemctl`) under a dedicated user, with stricter sandboxing and boot-time startup.

See: `references/ops-runbook.md`.

Note: some registries/packagers may strip `*.service` files. This skill’s `install-local` command generates the **user** unit file at install time, so the Clawhub-installed package does not need to include `systemd/*/*.service`.

## Quick Start (local workstation)

### 0) One-time install + configure (recommended)

Fast path (recommended): one-command local install.

This will:
- install a **systemd user service** (`~/.config/systemd/user/vaibot-guard.service`)
- create `~/.config/vaibot-guard/vaibot-guard.env` (mode `0600`) if missing
- **auto-generate `VAIBOT_GUARD_TOKEN`** if it isn’t already set

```bash
node scripts/vaibot-guard.mjs install-local
```

Or run the interactive configurator only (writes/updates `~/.config/vaibot-guard/vaibot-guard.env` with `chmod 600`):

```bash
node scripts/vaibot-guard.mjs configure
```

### 1) Start + smoke test

#### Foreground (quick dev check)

From this skill directory:

```bash
# 1) Start the guard service (foreground)
# Reads VAIBOT_GUARD_TOKEN (and other settings) from:
#   - env vars, or
#   - ~/.config/vaibot-guard/vaibot-guard.env
node scripts/vaibot-guard-service.mjs
```

In another terminal:

```bash
# 2) Precheck + exec (example)
node scripts/vaibot-guard.mjs precheck --intent '{"tool":"system.run","action":"exec","command":"/bin/echo","cwd":".","args":["hello"],"expectedOutputs":["hello"]}'

node scripts/vaibot-guard.mjs exec --intent '{"tool":"system.run","action":"exec","command":"/bin/echo","cwd":".","args":["hello"],"expectedOutputs":["hello"]}' -- /bin/echo hello
```

#### Systemd (recommended)

After running `install-local`, you can manage it with:

```bash
systemctl --user daemon-reload
systemctl --user enable --now vaibot-guard
systemctl --user status vaibot-guard --no-pager
```

Notes:
- `install-local` **generates** the user `.service` unit from an embedded template (so publishing/installing the skill does not need to ship `systemd/*/*.service` files).
- VPS/system service deployment is still supported; see `references/ops-runbook.md`.

### 2) (Optional) Wire VAIBot Guard enforcement into OpenClaw (plugin bridge)

If you are using the `vaibot-guard-bridge` OpenClaw plugin/tool approach (deny `system.run`, allow `vaibot_exec`), use:

```bash
# VAIBOT_GUARD_TOKEN must match what your running guard service expects.
export VAIBOT_GUARD_TOKEN="..."
node scripts/wire-openclaw-bridge.mjs

# then restart gateway
openclaw gateway restart
```

## Components

- `scripts/vaibot-guard-service.mjs` — local HTTP policy service
  - `GET /health`
  - `POST /v1/decide/exec` (precheck)
  - `POST /v1/finalize`
  - `POST /api/proof` (Merkle inclusion proofs)
- `scripts/vaibot-guard.mjs` — CLI entrypoint (run with `node scripts/vaibot-guard.mjs ...`)

## Required environment (MVP)

- Node.js 18+ on the host

Optional:
- `VAIBOT_GUARD_HOST` (default `127.0.0.1`)
- `VAIBOT_GUARD_PORT` (default `39111`)
- `VAIBOT_WORKSPACE` (default `process.cwd()`)
- `VAIBOT_GUARD_LOG_DIR` (default `${VAIBOT_WORKSPACE}/.vaibot-guard`)
- `VAIBOT_GUARD_TOKEN` (recommended): bearer token required for service endpoints (`/v1/decide/exec`, `/v1/finalize`, `/v1/flush`, `/api/proof`)
- `VAIBOT_POLICY_PATH` (default: `references/policy.default.json`): policy configuration (deny/approve tokens, allowlisted domains, redaction patterns, and file-mutation posture).
- `VAIBOT_CHECKPOINT_HASH_ALG` (reserved): future knob for migrating checkpoint chaining (`checkpoint.hash`) to SHA3-512. Currently checkpoint chaining uses SHA-256 for consistency.
- `VAIBOT_API_URL` (e.g. `https://www.vaibot.io/api`) to anchor receipts via `/prove`
- `VAIBOT_API_KEY` bearer token for `/prove` (Authorization: `Bearer <API KEY>`)
- `VAIBOT_PROVE_MODEL` (default `vaibot-guard`): `model` field required by VAIBot `/api/prove`.
- `VAIBOT_PROVE_MODE` (`off|best-effort|required`, default `best-effort`). In `required` mode, proving is **fail-closed** for both per-event receipts and checkpoint roots ("no proof, no action"). For security-first deployments, set this to `required`.
- `VAIBOT_MERKLE_CHECKPOINT_EVERY` (default `50`): count-based checkpointing interval (events).
- `VAIBOT_MERKLE_CHECKPOINT_EVERY_MS` (default `600000`): time-based checkpointing interval (ms).

Checkpointing is **whichever comes first**: if either threshold is met *and* there are new events since the last checkpoint, a new checkpoint root is created.
Recommended: 10 minutes and/or a few hundred–few thousand events depending on expected proof frequency.

## Rules (MUST FOLLOW)

1) Start the guard service (once per host):

```bash
node scripts/vaibot-guard-service.mjs
```

2) Before running any risky action, run a precheck:

```bash
node scripts/vaibot-guard.mjs precheck --intent '<json>'
```

3) If the decision is `deny`, do not execute.

4) If the decision is `approve`, require explicit human approval (MVP: stop and surface `approvalId`).

5) If the decision is `allow`, execute **only** via:

```bash
node scripts/vaibot-guard.mjs exec --intent '<json>' -- <command...>
```

6) Ensure the run is finalized (the `exec` command auto-finalizes on exit; you can also call it manually):

```bash
node scripts/vaibot-guard.mjs finalize --run_id <id> --result '<json>'
```

## Intent JSON (minimum fields)

The guard service requires these keys at minimum:

```json
{
  "tool": "system.run",
  "action": "exec",
  "command": "/usr/bin/uname",
  "cwd": "."
}
```

Recommended additional fields (use them when available):
- `args`: string[]
- `env_keys`: string[]
- `network`: `{ destinations: string[] }`
- `files`: `{ read: string[], write: string[], delete: string[] }`
- `correlation`: `{ agent_id, session_id, trace_id }`

## Policy

See: `references/policy.md`
See: `references/receipt-schema.md`
See: `references/checkpoint-schema.md`
See: `references/idempotency.md`
See: `references/metadata-indexing.md`
See: `references/merkle-replay.md`
See: `references/inclusion-proofs.md`
See: `references/required-mode.md`

## Output / receipts

- Decisions + finalize events are appended to hash-chained JSONL logs in `.vaibot-guard/`.
- These logs are designed to be tamper-evident (each line includes `prevHash`).
