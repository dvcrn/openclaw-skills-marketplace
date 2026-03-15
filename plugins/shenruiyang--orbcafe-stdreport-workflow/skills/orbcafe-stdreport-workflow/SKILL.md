---
name: orbcafe-stdreport-workflow
description: "Build ORBCAFE standard report/list pages with CStandardPage, CTable, CSmartFilter, useStandardReport, variant/layout persistence, and quickCreate/quickEdit/quickDelete flows. Use when implementing filters, pagination, grouped tables, or report page orchestration."
---

# ORBCAFE StdReport Workflow

## Scope

Use this skill for list/report pages.

Primary APIs:
- `CStandardPage`
- `CTable`
- `CSmartFilter`
- `useStandardReport`
- `CLayoutManager` / `CVariantManager`

## Workflow

1. Choose page pattern via `references/component-selection.md`.
2. Start from minimal runnable snippet in `references/recipes.md`.
3. Apply persistence and interaction constraints in `references/guardrails.md`.
4. Return only required props + one optional enhancement.

## Mandatory rules

- Always set identity:
  - `metadata.id` for `useStandardReport`
  - `appId` for standalone `CTable` / `CSmartFilter`
- Prefer `CStandardPage` + `useStandardReport` for business pages.
- Use `mode="integrated"` on `CStandardPage` unless custom orchestration is explicitly required.

## Output Contract

1. `Pattern`: integrated page or table-only.
2. `Code`: paste-ready, imports from `orbcafe-ui` only.
3. `Data contract`: columns/filters/rows/fetchData shape.
4. `Safety checks`: pagination + i18n + variant/layout notes.
