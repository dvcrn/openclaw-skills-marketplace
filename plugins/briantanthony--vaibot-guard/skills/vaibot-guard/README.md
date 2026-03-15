# VAIBot-Guard

Local policy guard + tamper-evident audit log for OpenClaw/VAIBot operations.

At a high level:
- You run a **local Guard service** (`vaibot-guard-service`) on `127.0.0.1`.
- OpenClaw (via a bridge plugin) or a CLI wrapper asks Guard **“is this tool call allowed?”**
- Guard returns `allow | deny | approve` and writes an append-only **audit trail** under `.vaibot-guard/`.

## What this repo/package contains

- `scripts/vaibot-guard-service.mjs` — HTTP service (policy decisions + audit + checkpoints)
- `scripts/vaibot-guard.mjs` — CLI to install/configure/run precheck/exec/finalize/flush/proof
- `references/` — policy + receipt/checkpoint schema docs
- `systemd/` — example unit/env files (note: some registries strip `.service` files)

## HTTP API (current)

Health:
- `GET /health`

Exec decisions (shell commands):
- `POST /v1/decide/exec`
- `POST /v1/finalize`

Generic tool decisions (used by the OpenClaw bridge plugin):
- `POST /v1/decide/tool`
- `POST /v1/finalize/tool`

Ops / audit:
- `POST /v1/flush` — attempt to flush/anchor checkpoints
- `POST /api/proof` — inclusion proofs for checkpointed leaves

> Auth: if `VAIBOT_GUARD_TOKEN` is set, protected endpoints require `Authorization: Bearer <token>`.

## Quick start (local workstation)

### 1) Install local service + config (recommended)

From this directory:

```bash
node scripts/vaibot-guard.mjs install-local
```

This will:
- create/update `~/.config/vaibot-guard/vaibot-guard.env` (chmod 600)
- generate a `VAIBOT_GUARD_TOKEN` if missing
- generate a **systemd user** unit (so it can run continuously)

Start it:

```bash
systemctl --user daemon-reload
systemctl --user enable --now vaibot-guard
systemctl --user status vaibot-guard --no-pager
```

### 2) Dev-mode foreground run (fast check)

```bash
node scripts/vaibot-guard-service.mjs
```

Then in another terminal:

```bash
curl -s http://127.0.0.1:39111/health | jq
```

## Wiring into OpenClaw

VAIBot-Guard can be used two ways:

1) **Skill/CLI wrapper approach** (good for early testing)
- precheck + exec wrappers call the Guard service

2) **Gateway plugin bridge (recommended for real enforcement)**
- an OpenClaw Gateway plugin intercepts **all tool calls** and asks Guard for a decision
- default posture can be `enforce` (fail-closed) or `observe` (log-only)

If you have a bridge wiring script:

```bash
export VAIBOT_GUARD_TOKEN="..."
node scripts/wire-openclaw-bridge.mjs
openclaw gateway restart
```

## Configuration / environment

Common env vars:

- `VAIBOT_GUARD_HOST` (default `127.0.0.1`)
- `VAIBOT_GUARD_PORT` (default `39111`)
- `VAIBOT_GUARD_TOKEN` (recommended)
- `VAIBOT_POLICY_PATH` (default `references/policy.default.json`)
- `VAIBOT_WORKSPACE` (default `process.cwd()`)
- `VAIBOT_GUARD_LOG_DIR` (default `${VAIBOT_WORKSPACE}/.vaibot-guard`)

Anchoring (optional):
- `VAIBOT_API_URL`
- `VAIBOT_API_KEY`
- `VAIBOT_PROVE_MODE` (`off|best-effort|required`, default `best-effort`)

Checkpoint cadence:
- `VAIBOT_MERKLE_CHECKPOINT_EVERY` (default `50`)
- `VAIBOT_MERKLE_CHECKPOINT_EVERY_MS` (default `600000`)

## Policy

Default policy lives at:
- `references/policy.default.json`

Docs:
- `references/policy.md`
- `references/receipt-schema.md`
- `references/checkpoint-schema.md`
- `references/inclusion-proofs.md`
- `references/required-mode.md`


## Security notes

- Treat `VAIBOT_GUARD_TOKEN` and `VAIBOT_API_KEY` as secrets.
- If you set `VAIBOT_PROVE_MODE=required`, Guard becomes **fail-closed** when proof anchoring cannot be performed.
- The tool endpoints are designed for localhost; think carefully before exposing them remotely.
