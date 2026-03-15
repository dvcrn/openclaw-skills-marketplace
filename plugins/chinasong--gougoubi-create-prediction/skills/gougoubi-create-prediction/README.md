# Gougoubi Create Prediction Skill

Reusable skill package for creating public prediction proposals on Gougoubi:

- Target page: `https://gougoubi.ai/premarket/proposals/create/public`
- Use case: any AI agent that can run browser automation or EVM contract calls
- Goal: consistent behavior and deterministic outputs across agents

## CLI install

Install from local repo clone:

```bash
bash scripts/install-gougoubi-create-prediction-skill.sh
```

Install from GitHub (using Codex skill installer):

```bash
~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo <owner>/<repo> \
  --path skills/gougoubi-create-prediction
```

After install, restart Codex/Cursor agent runtime to pick up the new skill.

## What it standardizes

- Minimal input schema for proposal creation (`marketName` + `deadlineIsoUtc` only)
- Validation rules (deadline, amount, addresses, tags)
- Approval-before-create flow for DOGE token allowance
- Canonical create transaction argument order
- Normalized success/failure output schema

## Required input (user)

```json
{
  "marketName": "Will BTC close above $100k on 2026-12-31?",
  "deadlineIsoUtc": "2026-12-30T16:00:00Z"
}
```

## Auto-filled by skill

- `imageUrl` (default proposal image)
- `liquidityToken` (default Gougoubi liquidity token)
- `deadlineTimezone` (locale or `UTC`)
- `rules` (AI generated rules)
- `stakeAmountDoge` (`10000`)
- `tags` (AI generated classification)
- `groupAddress` (created before proposal submit, using community flow)
- `language` (script-detected only; unsupported values are normalized to `en`)
- `skills` (empty string)

Community creation policy:

- Create group first (same as public create page)
- Group name = proposal name
- Group description = generated rules
- Group type = restricted
- Use created `groupAddress` as proposal `groupUrl` argument

## Success output

```json
{
  "ok": true,
  "mode": "browser",
  "txHash": "0x1234...",
  "proposalAddress": "0xabcd...",
  "warnings": []
}
```

## Failure output

```json
{
  "ok": false,
  "stage": "community-create",
  "error": "Group creation failed or group address unresolved",
  "retryable": true
}
```

## Publish notes

- Keep `SKILL.md` frontmatter complete (`name`, `description`, `metadata`).
- Keep examples aligned with live page constraints (minimum stake `10000 DOGE`).
- Attach screenshots separately if your distribution channel requires them.
- Keep CLI install docs in sync with `scripts/install-gougoubi-create-prediction-skill.sh`.
