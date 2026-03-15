---
name: claw-skill-hookaido
description: "Receive incoming webhooks from external services and trigger automations, integrations, and event-driven workflows. Operate Hookaido v2 inbound/outbound/internal webhook flows, queue triage, MCP workflows, release verification, and HTTP/gRPC pull workers. Use when tasks involve Hookaidofile authoring, queue backend selection (`sqlite`, `memory`, `postgres`), `hookaido` CLI commands (`run`, `config fmt`, `config validate`, `mcp serve`), pull operations (`dequeue`/`ack`/`nack`/`extend`) over HTTP or gRPC, Admin API backlog/DLQ handling, or production hardening for ingress and delivery."
---

# Hookaido

## Overview

Implement and troubleshoot Hookaido with a config-first workflow: edit `Hookaidofile`, validate, run, exercise ingress/pull flows, then diagnose queue health and DLQ behavior.
Treat Hookaido v2.0.0's modular architecture as additive in this skill: keep the existing workflow intact by default, and opt into modules such as `postgres`, gRPC workers, or release verification only when they materially help the task.
Use conservative, reversible changes and validate before runtime operations.

## Workflow

1. Confirm target topology: inbound+pull (HTTP or gRPC), push outbound, or internal queue, plus the queue backend (`sqlite`, `memory`, or `postgres`).
2. Choose runtime mode and ensure `hookaido` exists where tools execute.
   - Host-binary mode: use the install action from `metadata.openclaw.install`.
   - Host fallback: run `bash {baseDir}/scripts/install_hookaido.sh` (pinned `v2.0.0`, SHA256-verified).
   - Public repo/source mode: use the public upstream repo `github.com/nuetzliches/hookaido` via `go install github.com/nuetzliches/hookaido/cmd/hookaido@v2.0.0` when a source-based install is preferred.
   - Docker-sandbox mode: use a sandbox image that already includes `hookaido` (preferred), or install inside sandbox via `agents.defaults.sandbox.docker.setupCommand`.
   - Keep host install actions available as fallback and to satisfy `metadata.openclaw.requires.bins`.
3. Inspect and update `Hookaidofile` minimally.
4. Run format and validation before starting or reloading:
   - `hookaido config fmt --config ./Hookaidofile`
   - `hookaido config validate --config ./Hookaidofile`
   - `hookaido config validate --config ./Hookaidofile --strict-secrets` when secret refs or Vault-backed config are involved.
5. Start runtime and verify health:
   - `hookaido run --config ./Hookaidofile --db ./.data/hookaido.db`
   - `hookaido run --config ./Hookaidofile --postgres-dsn "$HOOKAIDO_POSTGRES_DSN"` when `queue postgres` is selected.
   - `curl http://127.0.0.1:2019/healthz?details=1`
6. Validate end-to-end behavior:
   - ingress request accepted and queued
   - consumer `dequeue`/`ack`/`nack`/`extend` path works (HTTP pull, batch `ack`/`nack`, plus gRPC pull when enabled)
7. For incidents, inspect backlog and DLQ first, then mutate.

## Task Playbooks

### Configure Ingress and Pull Consumption

1. Define a route with explicit auth and pull path (HTTP pull, optional gRPC pull worker listener).
2. Keep secrets in env/file refs, never inline.
3. Verify route and global pull auth are consistent.
4. Test with a real webhook payload and a dequeue/ack cycle, using batch `ack`/`nack` when worker throughput matters.

Prefer this baseline:

```hcl
ingress {
  listen :8080
}

pull_api {
  listen :9443
  grpc_listen :9943 # optional gRPC pull-worker listener
  auth token env:HOOKAIDO_PULL_TOKEN
}

/webhooks/github {
  auth hmac env:HOOKAIDO_INGRESS_SECRET
  pull { path /pull/github }
}
```

### Configure Push Delivery

1. Use push delivery only when inbound connectivity to the service is acceptable.
2. Set timeout and retry policy explicitly.
3. Validate downstream idempotency since delivery is at-least-once.

```hcl
/webhooks/stripe {
  auth hmac env:STRIPE_SIGNING_SECRET
  deliver "https://billing.internal/stripe" {
    retry exponential max 8 base 2s cap 2m jitter 0.2
    timeout 10s
  }
}
```

### Configure Queue Backends

1. Default to `sqlite` unless the task explicitly needs ephemeral dev mode or shared Postgres storage.
2. Treat `memory` and `postgres` as additive v2 modules, not replacements for existing sqlite workflows.
3. When using `postgres`, document the DSN source and validate health plus backlog endpoints after startup.

Prefer these patterns:

```hcl
queue sqlite

queue memory

queue postgres
```

### Operate Queue and DLQ

1. Start with health details and backlog endpoints.
2. Inspect DLQ before requeue or delete.
3. If requeueing many items, explain expected impact and rollback path.
4. Require clear operator reason strings for mutating admin calls.

Use:

- `GET /healthz?details=1`
- `GET /backlog/trends`
- `GET /dlq`
- `POST /dlq/requeue`
- `POST /dlq/delete`

### Use MCP Mode for AI Operations

1. Default to `--role read` for diagnostics.
2. Enable mutations only with explicit operator intent:
   - `--enable-mutations --role operate --principal <identity>`
3. Enable runtime control only for admin workflows:
   - `--enable-runtime-control --role admin --pid-file <path>`
4. Include `reason` for mutation calls and keep it specific.

### Verify Public Releases

1. Prefer official release assets from the public Hookaido repo.
2. When supply-chain assurance matters, validate checksums, signature material, and provenance before rollout.
3. Keep verification optional by default so existing skill flows do not become heavier unless the task requires it.

Use:

- `hookaido verify-release --checksums ./hookaido_v2.0.0_checksums.txt --require-provenance`

## Validation Checklist

- `hookaido config validate` returns success before runtime start/reload.
- `hookaido config validate --strict-secrets` is used when secret refs, Vault, or public-release rollout validation matters.
- Health endpoint is reachable and reports expected queue/backend state.
- Pull consumer can `dequeue`, `ack`, `nack`, and `extend` with valid token (HTTP and optional gRPC transport), including batch `ack`/`nack` when enabled.
- For push mode, retry/timeout behavior is explicitly configured.
- For `queue postgres`, runtime is started with `--postgres-dsn` or `HOOKAIDO_POSTGRES_DSN`.
- Any DLQ mutation is scoped, justified, and logged.

## Safety Rules

- Do not disable auth to "make tests pass."
- Do not suggest direct mutations before read-only diagnostics.
- Treat queue operations as at-least-once; require idempotent handlers.
- Keep secrets in `env:` or `file:` refs.

## References

- Read `references/operations.md` for command snippets and API payload templates.
