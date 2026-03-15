---
name: browser-commerce-base
description: "Browser-first workflow for e-commerce skills on OpenClaw. Use when shopping, comparing products, extracting prices, checking seller/store details, reading logged-in carts/orders, validating coupons, checking delivery availability, or collecting screenshots from Taobao, JD, Pinduoduo, Meituan, Eleme, VIP, SHEIN, Dianping, and similar commerce platforms."
---

# Browser Commerce Base

Use this skill as the shared browser workflow for e-commerce tasks.

## Profile selection

Choose browser profile by risk and need:

- `openclaw`: default for public browsing, search results, product pages, screenshots, and cross-platform comparison.
- `user`: use only when existing login state matters, such as carts, coupons, orders, addresses, or member prices.
- `chrome-relay`: use only when the user explicitly wants the extension attach-tab flow.

Default rule:
- public commerce pages → `openclaw`
- logged-in private pages → `user`

## Base workflow

1. Start with `browser status` and `browser start` if needed.
2. Open/focus the target site in a stable tab.
3. Run `snapshot` before any action.
4. Prefer `snapshot --interactive` / actionable refs over brittle CSS assumptions.
5. After navigation, filter changes, popups, or SKU changes, re-run `snapshot`.
6. Use `highlight` when a button/card/price block is ambiguous.
7. Capture evidence with screenshots when the result matters.
8. When the page is highly dynamic, check `requests`, `errors`, and `response body`.

## Commerce extraction order

For most shopping tasks, extract in this order:

1. platform
2. page type: search result / product detail / cart / order / coupon / store
3. title
4. current price
5. final price / coupon price / member price
6. store or seller
7. sales / rating / review count
8. shipping or delivery promise
9. SKU / spec options
10. risks / caveats
11. link + screenshot evidence

## Standard page workflows

### Search results page

Goal: compare multiple candidates quickly.

Do:
- open search page
- snapshot interactive elements
- identify product cards, price text, store names, tags, sales, coupons
- collect top candidates into structured notes
- screenshot result page if ranking matters

### Product detail page

Goal: make one item decision-ready.

Do:
- extract title, price, final price, store, shipping, service badges
- inspect SKU/spec selectors
- note coupons, subsidies, timed promotions, member-only prices
- if specs are changed, re-snapshot before re-reading price
- screenshot detail evidence when recommending a purchase

### Cart / order / coupon page

Goal: use private login state safely.

Do:
- switch to `profile="user"` only if needed
- prefer read/check actions over side effects
- stop before irreversible actions such as payment or final order submission
- summarize discounts, totals, coupon applicability, and delivery info

### Location-sensitive commerce page

Goal: judge delivery or stock by location.

Do:
- use geolocation or user-browser context when available
- check whether delivery area, ETA, store availability, or fee changes by location
- state clearly when output depends on location assumptions

## Safety boundaries

- Do not complete payment.
- Do not place final orders without explicit confirmation.
- Do not change account settings, addresses, or payment methods unless explicitly asked.
- For logged-in pages, prefer observation and recommendation over action.

## Debug workflow

When automation becomes unstable:

1. re-run `snapshot`
2. `highlight` the target ref
3. inspect `errors`
4. inspect `requests`
5. use `response body` for commerce APIs when visible UI is incomplete
6. use trace only when needed

## Read references as needed

- Read `references/browser-commerce-schema.md` for the reusable output schema.
- Read `references/platform-adaptation.md` for platform-specific browser strategy.
