---
name: gougoubi-create-prediction
description: "Create public prediction proposals on Gougoubi with deterministic validation, approval, and transaction submission. Use when creating/publishing prediction markets from structured input."
---

# Gougoubi Create Prediction

Create a new public prediction proposal on Gougoubi from structured input.

## Run Conditions

- Wallet must be connected.
- Stake amount must be at least `10000 DOGE`.
- Deadline must be in the future.
- At least one tag is required.

## Minimal Input (User Only)

```json
{
  "marketName": "",
  "deadlineIsoUtc": "2026-05-10T12:00:00Z"
}
```

## Agent Auto-Fills

The skill must provide all non-required fields:

- `imageUrl` (platform default image)
- `liquidityToken` (platform default token)
- `deadlineTimezone` (user locale or `UTC`)
- `rules` (AI generated from name + deadline)
- `stakeAmountDoge` (default `10000`)
- `tags` (AI generated classification from proposal title/content)
- `groupAddress` (must be created before proposal submit; not empty)
- `language` (script detection only; must be in `zh-CN|en|ja|ko|es|fr|de|ru|tr`, else `en`)
- `skills` (empty string)

## Deterministic Steps

1. Validate minimal user input (`marketName`, `deadlineIsoUtc`).
2. Run AI enrichment for `rules` and `tags`.
3. Detect `language` with script rules and normalize to supported set, else `en`.
4. Create community group first (`name = marketName`, `description = rules`, `groupType = RESTRICT`).
5. Resolve `groupAddress` from group creation receipt and map to proposal `groupUrl` arg.
6. Auto-fill remaining fields with platform defaults.
7. Convert `stakeAmountDoge` to wei.
8. Check DOGE balance.
9. Check DOGE allowance to factory.
10. If allowance is insufficient, request approval and wait confirmation.
11. Submit create transaction (11 args in canonical order).
12. Wait for receipt and return tx hash + proposal address when available.

## Output

```json
{
  "ok": true,
  "txHash": "0x...",
  "proposalAddress": "0x... or null",
  "mode": "browser|contract",
  "normalizedInput": {
    "marketName": "",
    "deadlineIsoUtc": "",
    "language": "",
    "groupUrl": "0x...",
    "aiGenerated": {
      "rules": true,
      "tags": true,
      "language": false
    },
    "languageSource": "script-detect-supported-or-en",
    "defaultsApplied": true
  },
  "warnings": []
}
```

Failure shape:

```json
{
  "ok": false,
  "stage": "validation|ai-enrichment|community-create|approve|create|confirm|resolve",
  "error": "AI enrichment failed",
  "retryable": true
}
```

## Boundaries

- Do not use private credentials or private hosts.
- Do not auto-accept wallet signatures.
- If content moderation flags risk, require user confirmation before submission.
