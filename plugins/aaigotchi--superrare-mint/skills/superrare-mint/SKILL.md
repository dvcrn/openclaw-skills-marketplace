---
name: superrare-mint
description: "Mint art to a SuperRare-compatible ERC-721 collection on Ethereum via Bankr. Uploads media and metadata to SuperRare, dry-runs safely by default, and records auditable mint receipts."
homepage: https://github.com/aaigotchi/superrare-mint
---

# superrare-mint

Mint aaigotchi art into an existing SuperRare-compatible ERC-721 contract using Bankr signing.

## Scripts

- `./scripts/pin-metadata.mjs --name ... --description ... --image ... [--video ...] [--tag ...] [--attribute trait=value]`
  - Uploads media to SuperRare and pins metadata.
  - Prints JSON including `tokenUri` and `gatewayUrl`.
- `./scripts/mint-via-bankr.sh --token-uri <uri> [--contract <address>] [--receiver <address>] [--royalty-receiver <address>] [--chain mainnet|sepolia] [--broadcast]`
  - Builds calldata for `mintTo(string,address,address)` or `addNewToken(string)`.
  - Defaults to dry-run unless `--broadcast` is passed or `DRY_RUN=0`.
  - Submits without waiting on Bankr, then polls chain directly for the receipt.
  - Writes a JSON receipt on successful broadcast.
- `./scripts/mint-art.sh --name ... --description ... --image ... [options]`
  - End-to-end wrapper: upload metadata, then mint via Bankr.
  - Use `--metadata-only` to stop after pinning and print the token URI.

## Config

Default config path:
- `config.json` in this skill directory

Override with:
- `SUPER_RARE_CONFIG_FILE=/path/to/config.json`

Expected keys:
- `chain`: `mainnet` or `sepolia`
- `collectionContract`
- `receiver`
- `royaltyReceiver`
- `rpcUrl`
- `apiBaseUrl`
- `descriptionPrefix`

## Defaults and safety

- Dry-run is the default. Mint transactions only broadcast with `--broadcast` or `DRY_RUN=0`.
- Broadcast mode uses a short Bankr submit timeout and then waits for the onchain receipt directly, which avoids hanging on long confirmation waits.
- `mint-art.sh` still uploads media/metadata to SuperRare before the dry-run mint preview. Use `--metadata-only` if you want to stop after pinning and inspect the token URI.
- If neither `receiver` nor `royaltyReceiver` is set, the skill calls `addNewToken(string)`.
- If either receiver field is provided, the skill calls `mintTo(string,address,address)`.
- If only one of `receiver` or `royaltyReceiver` is set, the other defaults to the same address.
- Successful broadcasts write receipts into `receipts/`.

## Bankr API key resolution

1. `BANKR_API_KEY`
2. `systemctl --user show-environment`
3. `~/.openclaw/skills/bankr/config.json`
4. `~/.openclaw/workspace/skills/bankr/config.json`

## Quick use

```bash
cp config.example.json config.json

./scripts/pin-metadata.mjs \
  --name "aaigotchi genesis #1" \
  --description "First aaigotchi genesis mint" \
  --image ./art.png

./scripts/mint-via-bankr.sh \
  --token-uri ipfs://... \
  --broadcast

./scripts/mint-art.sh \
  --name "aaigotchi genesis #1" \
  --description "First aaigotchi genesis mint" \
  --image ./art.png \
  --broadcast
```

## Timeouts

Optional environment variables:
- `BANKR_SUBMIT_TIMEOUT_SECONDS` (default `60`)
- `RECEIPT_WAIT_TIMEOUT_SECONDS` (default `300`)
- `RECEIPT_POLL_INTERVAL_SECONDS` (default `5`)
