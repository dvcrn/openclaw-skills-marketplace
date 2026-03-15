---
name: viral-app
description: "Use the viral.app API from an agent with a local CLI for account analytics, tracked videos/accounts, projects, creator hub, and live data operations."
---

# viral-app

Use this skill when you need to read or manage data through the viral.app API.

## When to use

- Query analytics (accounts, videos, KPIs, exports).
- Manage tracked entities (accounts, videos, exclusions, refresh runs).
- Manage projects and creator hub resources.
- Pull live platform data (TikTok, Instagram, YouTube).

## Quick start

1. Ensure `viral-app` CLI is installed and available in `PATH`.

```bash
viral-app --help
```

2. Set API key:

```bash
export VIRAL_API_KEY="..."
```

Get this key from viral.app dashboard at `Settings -> API Keys`.

3. Verify access:

```bash
viral-app accounts-list --per-page 1
```

The wrapper injects `x-api-key` automatically from `VIRAL_API_KEY` unless a header is already passed.

## Inputs to collect first

- Task type: read/report or mutate/manage resources.
- Org-scoped IDs: `orgacc_*`, `orgproj_*`, creator/campaign/payout IDs when relevant.
- Platform and entity identifiers (`tiktok|instagram|youtube`, platform account/video IDs).
- Time bounds (`--date-range[from]`, `--date-range[to]`) for analytics tasks.
- Pagination/scope (`--per-page`, filters) to keep output focused.

## Command cookbook

Discover available operations:

```bash
viral-app --help
viral-app <command> --help
```

Common reads:

```bash
viral-app accounts-list --per-page 10
viral-app videos-list --per-page 10
viral-app analytics-get-kpis
viral-app analytics-top-videos --per-page 10
viral-app integrations-apps-list
```

Common mutations:

```bash
viral-app projects-create --body '{"name":"My Project"}'
viral-app accounts-tracked-refresh --body '{"accounts":["orgacc_..."]}'
viral-app projects-add-to-account --body '{"projectId":"orgproj_...","accountId":"orgacc_..."}'
```

## Safety rules

- Confirm intent before `POST`, `PUT`, `PATCH`, or `DELETE` unless the user explicitly asked for that mutation.
- Run `<command> --help` before mutations to verify required flags and body schema.
- Prefer narrow queries first (`--per-page`, filters, date ranges) before broad exports.
- Keep output machine-readable by default; only switch format when requested.

## Troubleshooting

- `401 UNAUTHORIZED`: missing/invalid API key; verify `VIRAL_API_KEY` or `-H "x-api-key: ..."` value.
- `401` can also happen with expired/revoked keys or wrong org context.
- `429` or retry hints: back off and retry later; inspect response headers such as `Retry-After`.
- Empty `data` arrays: validate filters, project/account IDs, and date range constraints.
- Never expose API keys in commits; rotate keys after sharing for tests.

## Agent defaults

- Output defaults to JSON (`RSH_OUTPUT_FORMAT=json` unless overridden).
- Auto-pagination defaults to disabled (`RSH_NO_PAGINATE=true`) for predictable scripted behavior.
- Summarize key metrics after reads and explicitly call out write-side effects after mutations.
