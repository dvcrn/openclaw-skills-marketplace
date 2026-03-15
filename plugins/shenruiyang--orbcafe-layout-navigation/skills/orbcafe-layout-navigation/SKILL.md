---
name: orbcafe-layout-navigation
description: "Build ORBCAFE application shell and navigation experience with CAppPageLayout, NavigationIsland, useNavigationIsland, i18n provider, markdown renderer, and page transitions. Use when requests involve app frame, user menu, locale switching, navigation tree, or route transition UX."
---

# ORBCAFE Layout + Navigation

## Scope

Use this skill for application frame and navigation-level requests.

Primary APIs:
- `CAppPageLayout`, `CAppHeader`, `usePageLayout`
- `NavigationIsland`, `TreeMenu`, `useNavigationIsland`
- `OrbcafeI18nProvider`, `useOrbcafeI18n`
- `MarkdownRenderer`
- `CPageTransition`

## Workflow

1. Choose frame pattern in `references/patterns.md`.
2. Apply locale + user menu + hydration checks in `references/guardrails.md`.
3. Attach markdown/transition utilities only if explicitly needed.

## Output Contract

1. `Layout decision`: full shell vs nav-only.
2. `Code snippet`: app frame with minimal props.
3. `Runtime safety`: locale and hydration checks.
