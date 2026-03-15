# Ops runbook

Use interpreter:

```bash
PY=<workspace>/.venv-algo/bin/python
```

Preflight first:

```bash
python3 scripts/preflight_requirements.py
```

## Daily sequence

```bash
$PY /home/molty/.openclaw/workspace/scripts/memory_pensieve/auto_capture_daily.py
$PY /home/molty/.openclaw/workspace/scripts/memory_pensieve/dream_cycle_daily.py
$PY /home/molty/.openclaw/workspace/scripts/memory_pensieve/anchor_daily_algorand.py
$PY /home/molty/.openclaw/workspace/scripts/memory_pensieve/read_anchor_latest.py
$PY /home/molty/.openclaw/workspace/scripts/memory_pensieve/hardening_v21_validate.py
```

## Expected outputs

- `anchor_daily_algorand.py`:
  - `status=anchored` or `status=noop_already_anchored`
  - `events`, `semantic`, `procedural`, `self_model`
  - `txid` or `txids[]`
  - `multi_tx` true/false

- `read_anchor_latest.py`:
  - latest anchor metadata + counts

- `hardening_v21_validate.py`:
  - `ok=true/false`
  - parity: `local_events` vs `onchain_events`
  - `issues[]` and `warnings[]`

## Recovery

```bash
$PY /home/molty/.openclaw/workspace/scripts/memory_pensieve/recover_from_blockchain.py YYYY-MM-DD --restore
```

Writes recovered files in:
- `memory/recovered/events_recovered_YYYY-MM-DD.jsonl`
- `memory/recovered/semantic_recovered_YYYY-MM-DD.jsonl`
- `memory/recovered/procedural_recovered_YYYY-MM-DD.jsonl`
- `memory/recovered/self_model_recovered_YYYY-MM-DD.jsonl`

## Emergency backfill

```bash
$PY /home/molty/.openclaw/workspace/scripts/memory_pensieve/capture_from_logs.py YYYY-MM-DD
```

Use only when raw events were not captured in normal flow.
