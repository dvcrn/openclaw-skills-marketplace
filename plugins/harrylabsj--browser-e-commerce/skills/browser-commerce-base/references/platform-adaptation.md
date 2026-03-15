# Platform Adaptation

## Taobao / Tmall
- Prefer `openclaw` for search/detail browsing.
- Switch to `user` for cart, coupon center, order page, or member prices.
- Re-snapshot after SKU/spec changes because price blocks often refresh.
- Capture store badge, sales hints, coupon hints, and seller tier.

## JD
- Prioritize store type extraction: 自营 / 旗舰店 / 第三方.
- Re-check final price after coupons, PLUS, or subsidy blocks appear.
- For logistics-sensitive items, capture shipping ETA and delivery promise.

## PDD
- Extract 百亿补贴 / 拼团 / 店铺类型 first.
- Be extra cautious with low-price items; capture compensation/service badges.
- Re-snapshot after opening subsidy or group-buy overlays.

## Meituan / Eleme
- Treat location and delivery ETA as first-class fields.
- Check 起送价, 配送费, 配送时长, 月销量, 满减/红包.
- If comparing both platforms, normalize the same restaurant into one row.

## Dianping
- Prefer practical-use extraction over score-only extraction.
- Capture score, review count, recent negative patterns, group-buy constraints.
- Use screenshots when comparing several stores for decision support.

## VIP / SHEIN
- Capture sale timing, discount framing, stock/size hints, and promotion windows.
- Fashion category pages often lazy-load; re-snapshot after scrolling or filtering.
