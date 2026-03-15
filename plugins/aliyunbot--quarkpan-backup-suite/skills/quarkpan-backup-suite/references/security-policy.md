# Security Policy

## Account binding model

- First login must run `bind` and save bound UID fingerprint.
- Every upload must pass `check` before cloud write.
- UID mismatch => block upload and alert.

## Rotation (changing Quark account)

Use explicit two-step flow only:
1. `rotate-arm --ttl-min 10` to generate one-time token.
2. Re-login to target account.
3. `rotate-apply --token <token> --confirm YES_I_UNDERSTAND`.

If token expired or missing, rotation is denied.

## Snapshot safety model

- Never auto-create snapshots on schedule.
- Prompt weekly; create only on explicit owner request.
- Keep 2-3 known good snapshots.
- Require explicit confirmation for rollback.

## Restore safety model

- Always run `--dry-run` before real apply.
- Keep rollback checkpoint before apply.
- Treat cloud upload failure separately from local backup status.
