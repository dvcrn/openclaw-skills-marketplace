---
name: openclaw-memory-pensieve-algorand-v2-1
description: "Operate the current Pensieve memory stack for OpenClaw with append-only local layers, hash-chain integrity, daily dream-cycle consolidation, encrypted Algorand anchoring of full content (events + semantic + procedural + self_model), and v2.1 post-anchor recoverability hardening checks. Use when implementing, running, auditing, or recovering this memory system."
---

# OpenClaw Memory Pensieve v2.1 (hardening)

Run this workflow when the goal is reliable long-term memory with disaster recovery from blockchain anchors.

## Workflow

1. Ensure memory layers exist in `memory/`.
2. Capture important events into `events.jsonl` (append-only, hash-chained).
3. Run daily dream cycle to promote stable patterns.
4. Anchor daily memory to Algorand with encrypted notes (full content, multi-TX if needed).
5. Run v2.1 hardening validator after anchoring.
6. If recovery is needed, reconstruct and verify from on-chain notes.

## Mandatory operational rules

- Keep all `*.jsonl` append-only. Never rewrite or delete lines.
- Keep secrets local in `.secrets/` and never print them in chat.
- Anchor encrypted payloads only (never plaintext memory).
- Treat hardening failures as blocking for “recovery-fidelity” claims.

## Prerequisites (explicit)

- Python environment with `algosdk` and `cryptography`
- Local secret files (not packaged):
  - `.secrets/algorand-wallet-nox.json`
  - `.secrets/algorand-note-key.bin`
- Optional explicit env vars for endpoints/auth:
  - `ALGORAND_ALGOD_URL`, `ALGORAND_ALGOD_TOKEN`
  - `ALGORAND_INDEXER_URL`, `ALGORAND_INDEXER_TOKEN`

Run preflight first:
- `scripts/preflight_requirements.py`

## Runtime commands (current implementation)

Use interpreter:
- `<workspace>/.venv-algo/bin/python`

Bundled scripts in this skill (`scripts/`):
- `auto_capture_daily.py`
- `dream_cycle_daily.py`
- `anchor_daily_algorand.py`
- `read_anchor_latest.py`
- `hardening_v21_validate.py`
- `recover_from_blockchain.py`
- `capture_from_logs.py`
- `preflight_requirements.py`

Main pipeline:
- `scripts/auto_capture_daily.py`
- `scripts/dream_cycle_daily.py`
- `scripts/anchor_daily_algorand.py`
- `scripts/read_anchor_latest.py`
- `scripts/hardening_v21_validate.py`

Recovery/debug:
- `scripts/recover_from_blockchain.py`
- `scripts/capture_from_logs.py`

## Read next

- `references/architecture.md` for layer model and guarantees.
- `references/ops-runbook.md` for day-to-day run commands and outputs.
- `references/hardening-v21.md` for strict post-anchor validation policy.
- `references/security-prereqs.md` for explicit dependency/secret contract.
