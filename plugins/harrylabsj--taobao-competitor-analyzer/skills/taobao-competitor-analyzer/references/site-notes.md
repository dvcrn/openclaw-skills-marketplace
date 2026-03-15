# Site Notes

## Goal

Use browser-visible marketplace pages to collect price evidence for the same or closest-matching product on JD, Pinduoduo, and Vipshop.

## Common Reminders

- Prefer visible desktop web pages.
- Use exact product names first, then a lightly simplified query if results are sparse.
- Compare like-for-like products only.
- Keep the evidence chain simple: search page -> listing -> visible title/price/spec.
- Do not use APIs, hidden JSON endpoints, or scraping shortcuts outside the browser tool.

## JD

- Usually supports standard web search and listing pages well.
- Prefer self-operated or official flagship listings when multiple near-identical results exist.
- Watch for coupon text, plus/member pricing, and promotional banners.
- Distinguish list price from final promo price if both are shown.

## Pinduoduo

- Web results may be noisier than JD.
- Watch for subsidy labels, group-buy wording, or strong promo framing.
- Matching confidence should be reduced when the seller, spec, or packaging is unclear.
- If the browser experience is limited, use a public search engine with site restriction, then open the visible result page.

## Vipshop

- Results may lean toward branded discount inventory and variant-specific listings.
- Pay attention to size/color/version because discount channels often surface adjacent variants.
- If the exact match is missing, mark the result as `近似款` instead of treating it as the same SKU.

## Evidence Standard

For each platform, aim to capture:
- title
- displayed price
- variant/specification
- seller/store if visible
- URL
- a short matching note

## Output Discipline

Use short, decision-friendly language.

Recommended summary fields:
- lowest visible comparable price
- whether the comparison is apples-to-apples
- major caveats: variant mismatch, coupon dependency, seller difference, shipping difference, regional limitation
