---
name: taobao-competitor-analyzer
description: "Analyze a Taobao product against marketplace competitors by searching the same product name on JD.com, Pinduoduo, and Vipshop, then extracting visible price information through browser automation only. Use when the user provides a product name and wants a cross-platform price check, competitor snapshot, price comparison table, or marketplace research without using APIs."
---

# Taobao Competitor Analyzer

Compare a Taobao product with the same or closest-matching listings on 京东、拼多多、唯品会 using the browser tool only. Work from a product name, collect visible listing information, and return a compact comparison with price evidence and caveats.

## Workflow

1. Normalize the input product name.
2. Search the exact or lightly simplified keyword on:
   - 京东
   - 拼多多
   - 唯品会
3. Stay in browser-driven flows only. Do not call site APIs, hidden JSON endpoints, app-only interfaces, or unofficial scrapers.
4. Extract the top relevant visible results from each site.
5. Prefer listings that match the same brand, model, spec, size, quantity, and packaging.
6. Summarize the comparison in a table and state any uncertainty.

## Input Rules

Require a product name as input.

If the product name is too broad, ask one short follow-up to narrow it, for example:
- brand
- model
- size/specification
- package count
- flavor/color/version

Good inputs:
- `Apple AirPods Pro 2`
- `维达抽纸 3层 100抽 24包`
- `耐克 Air Zoom Pegasus 41 男款`

Weak inputs that need clarification:
- `纸巾`
- `耳机`
- `运动鞋`

## Browser Execution Rules

- Prefer the isolated OpenClaw browser unless the user explicitly asks to use their Chrome tab.
- Start with one tab per site when practical.
- Re-snapshot after navigation or major DOM changes.
- If a site shows login walls, anti-bot interstitials, region prompts, or app-download overlays, use the visible web result if possible and mention the limitation.
- If a site blocks access completely, report it instead of trying to bypass it.
- Do not fabricate missing prices.

## Search Targets

Use the standard web search pages when possible:

- 京东: search for the product name on jd.com
- 拼多多: search for the product name on pinduoduo.com or the visible web listing/search experience available in browser
- 唯品会: search for the product name on vip.com

If direct site search is unstable in browser, use a public search engine query constrained to the site, then open the most relevant visible result. Example pattern:
- `site:jd.com 商品名`
- `site:pinduoduo.com 商品名`
- `site:vip.com 商品名`

Still use browser navigation for the actual evidence collection.

## Matching Rules

Treat listings as comparable only when the core attributes align.

Check, in order:
1. Brand
2. Product line / model
3. Variant
4. Size / weight / count
5. Seller type if obvious (official flagship, self-operated, marketplace seller)

If there is no close match on a platform:
- say `未找到足够接近的同款`
- optionally include the nearest visible alternative, clearly labeled as `近似款`

## What To Capture Per Site

Capture only information visible on the page. Prefer the first 1-3 relevant results.

For each selected listing, collect when visible:
- platform
- title
- displayed price
- promo/discount wording
- package/specification
- store/seller name
- delivery or shipping note
- URL
- confidence: high / medium / low
- note about why it matches or why it is only approximate

## Output Format

Return a concise comparison first, then short notes.

Use a table like this:

| 平台 | 商品标题 | 价格 | 规格/版本 | 店铺 | 匹配度 | 备注 |
|---|---|---:|---|---|---|---|
| 京东 | ... | ¥... | ... | ... | 高 | 同品牌同规格 |
| 拼多多 | ... | ¥... | ... | ... | 中 | 规格接近，包装不同 |
| 唯品会 | ... | ¥... | ... | ... | 低 | 仅找到近似款 |

Then add:
- `最低可见价` and platform
- `可比性判断`: high / medium / low
- `风险提示`: differences in package, seller, promo timing, membership price, shipping, or coupon requirements

## Interpretation Rules

- Do not claim a platform is cheaper unless the compared items are materially comparable.
- Separate `标价` from coupon-after price when the page makes that distinction.
- Mention when a price may depend on membership, flash sale, subsidy, or region.
- If search results are noisy, prefer accuracy over completeness.

## Example Requests

- `帮我查一下“德芙黑巧克力 84g”在京东、拼多多、唯品会的价格`
- `对比一下“iPhone 16 Pro 256GB”在几个平台上的可见报价`
- `把这个淘宝商品名拿去京东、拼多多、唯品会搜同款，做个价格表`

## Failure Handling

If one or more sites cannot be accessed or searched reliably, still return a partial result and list:
- which site failed
- what was attempted
- whether the failure was due to login wall, anti-bot page, timeout, or missing web search results

## Resource

- Read `references/site-notes.md` when you need execution reminders for JD, Pinduoduo, and Vipshop search behavior and evidence standards.
