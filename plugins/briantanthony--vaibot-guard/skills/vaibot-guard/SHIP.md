# VAIBot Guard — Ship Checklist

This file tracks what must be true before we call **vaibot-guard** complete and ready to ship.

## A) Correctness & cryptography (must-have)

- [x] Canonicalize hashing: hash must be deterministic (stable key ordering); do not rely on JS object insertion order.
- [ ] Domain separation consistency:
  - [x] Leaf: `sha256("leaf:" + eventHash)`
  - [x] Node: `sha256("node:" + left + ":" + right)`
  - [x] Checkpoint hash: domain-separated and canonicalized (`hashCheckpoint("checkpoint:" + stableStringify(checkpointWithoutHash))`).
- [x] Self-audit tooling: command/script to recompute Merkle roots from stored leaves and verify checkpoint roots.

## B) Replay + anchoring behavior (must-have)

- [x] Add `vaibot-guard flush` CLI command to replay pending checkpoints on demand.
- [x] Support time-based checkpointing (every T seconds) in addition to event-count-based (whichever comes first; configurable via `VAIBOT_MERKLE_CHECKPOINT_EVERY` and `VAIBOT_MERKLE_CHECKPOINT_EVERY_MS`).
- [x] Clarify required-mode semantics and enforce consistently:
  - [x] In `VAIBOT_PROVE_MODE=required`, we require `/prove` for:
    - [x] per-event receipts (precheck/finalize)
    - [x] checkpoint roots
    - [x] both
- [x] In `VAIBOT_PROVE_MODE=required`, the guard service refuses to start unless `VAIBOT_API_URL` and `VAIBOT_API_KEY` are configured.

## C) Inclusion proofs (must-have)

- [x] Service endpoint `POST /api/proof` to generate inclusion proof
- [x] Add CLI command: `vaibot-guard proof --session_id ... --index ... --checkpoint_seq ...`
- [x] Add verifier reference snippet (how to recompute root from `{leaf, siblings}` and compare to checkpoint root)
- [x] Decide MVP performance stance:
  - [x] Keep O(n) proof generation (document limits; keep checkpoints reasonably sized for interactive use)
  - [ ] OR optimize by storing per-level nodes per checkpoint window

## D) Security posture (must-have)

- [x] Policy file support (JSON for now): denied patterns, approval-required patterns, sensitive paths, allowlisted domains.
  - [x] Add a default policy file (`references/policy.default.json`) and schema (`references/policy.schema.json`).
  - [x] Wire `VAIBOT_POLICY_PATH` into the guard service and use it for deny/approve/domain/path rules.
- [x] Path boundary hardening (symlinks + realpath edge cases): resolve intent paths against realpath(cwd), treat unresolved paths as outside workspace, and ensure all mutations stay within realpath(workspace).
- [x] Secret redaction in logs/receipts (policy-driven regex redaction for command/args and network destinations; env_keys redaction via patterns).
- [x] Guard service auth (localhost token): require `VAIBOT_GUARD_TOKEN` for `/v1/decide/exec`, `/v1/finalize`, `/v1/flush`, `/api/proof`.

## E) Operational readiness (must-have)

- [x] Provide systemd runbook + templates (user service + system service): see `references/ops-runbook.md` and `systemd/`.
- [x] Handle EADDRINUSE cleanly (clear error + remediation via `VAIBOT_GUARD_PORT`).
- [x] Log rotation / retention strategy (time-based cleanup via `VAIBOT_LOG_RETENTION_DAYS`) plus documentation.

## F) Product/API alignment (must-have)

- [x] Receipt schema finalization:
  - [x] `vaibot-guard/receipt@0.1` fields finalized (single object model with intent+decision+result; see `references/receipt-schema.md`)
  - [x] `vaibot-guard/checkpoint@0.1` fields finalized (see `references/checkpoint-schema.md`)
  - [x] compatibility notes for future versions (schemas are versioned via `schema` strings; avoid breaking changes without bump)
- [x] Confirm `/api/prove` idempotency key strategy (see `references/idempotency.md`).
- [x] Confirm which `metadata` fields should be indexed on VAIBot side (see `references/metadata-indexing.md`).

## G) Packaging (must-have)

- [x] SKILL.md “Quick Start” is runnable end-to-end.
- [x] Ensure skill folder stays minimal (docs live under `references/`; templates under `systemd/`).
- [x] Decide distribution:
  - [x] repo-only (for now)
  - [ ] packaged `.skill` artifact

---

## Notes / Decisions

- Merkle accumulator + periodic checkpoints are used for enterprise-grade auditability.
- Append-only JSONL remains the raw source of truth.
