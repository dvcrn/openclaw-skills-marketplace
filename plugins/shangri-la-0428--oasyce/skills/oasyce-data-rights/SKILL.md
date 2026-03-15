---
name: oasyce-data-rights
description: "Register, price, trade, and enforce data rights on the Oasyce decentralized network. Use when user mentions data assets, data rights, data registration, shares, bonding curve, or wants to monetize/protect their data."
---

# Oasyce Data Rights

Settle data rights on the decentralized Oasyce network — register, price, buy shares, and enforce ownership.

## Prerequisites

```bash
pip install oasyce
```

Verify: `oasyce version` should print `0.9.0+`.

## Commands

### Register a data asset

```bash
oasyce register <file_or_dir> [--tags tag1,tag2] [--creator NAME]
```

Registers a file or directory as a data asset:
- Computes content hash (SHA-256)
- Signs with creator's private key
- Anchors to Merkle tree
- Returns a globally unique asset ID

For free/open-source assets, add `--free`:
```bash
oasyce register ./my-project --free --tags opensource,protocol
```

### Get a price quote

```bash
oasyce quote <asset_id> --amount <OAS>
```

Returns how many shares you'd receive for a given OAS deposit, based on the Bonding Curve.

### Buy shares

```bash
oasyce buy <asset_id> --amount <OAS> --buyer <BUYER_ID>
```

Purchases ownership shares in a data asset. Requires collateral deposit (10% of purchase).

### Check holdings

```bash
oasyce shares <owner_id>
```

Shows all share holdings and accumulated dividends.

### Search assets

```bash
oasyce search <query> [--tag TAG]
```

### Verify provenance (PoPC)

```bash
oasyce verify <file> [--device-attestation JSON]
```

Runs 6-point Proof of Physical Capture verification.

## When to use this skill

- User wants to register/protect data assets
- User asks about data monetization or rights
- User mentions Oasyce, OAS tokens, bonding curves
- User wants to check asset ownership or shares
- User wants to verify data provenance

## When NOT to use this skill

- Simple file management (use datavault instead)
- General crypto/blockchain questions unrelated to data rights
