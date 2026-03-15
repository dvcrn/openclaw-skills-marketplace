# Security & prerequisites (v2.1.1)

## Explicit required dependencies

Runtime dependencies:
- Python venv with:
  - `algosdk`
  - `cryptography`

Required local files:
- `.secrets/algorand-wallet-nox.json`
- `.secrets/algorand-note-key.bin`

Optional env vars (recommended explicit config):
- `ALGORAND_ALGOD_URL`
- `ALGORAND_ALGOD_TOKEN`
- `ALGORAND_INDEXER_URL`
- `ALGORAND_INDEXER_TOKEN`

## Safety constraints

- Never print secret material (mnemonic, raw keys, tokens) in logs/chat.
- Never include `.secrets/*` in git or distributable artifacts.
- Fail fast if dependencies/secret files are missing.
- Treat recovery claims as valid only after validator status `ok=true`.

## Deployment checklist

1. Create/activate Python venv and install deps.
2. Place wallet + note key in `.secrets/` with restrictive permissions.
3. Configure explicit Algorand endpoints/tokens via env vars.
4. Run `scripts/preflight_requirements.py`.
5. Run pipeline and then `scripts/hardening_v21_validate.py`.
