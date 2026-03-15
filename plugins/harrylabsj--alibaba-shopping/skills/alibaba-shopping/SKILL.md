---
name: Alibaba Shopping
description: "Shop Taobao/Tmall with smart search strategies, seller vetting, price negotiation, and deal finding guidance."
homepage: https://clawic.com/skills/alibaba-shopping
---

## When to Use

User wants to shop on Taobao (淘宝) or Tmall (天猫). Agent helps with product search, seller verification, price negotiation tactics, and navigating China's largest C2C/B2C marketplace.

## Quick Reference

| Topic | File |
|-------|------|
| Seller vetting | `sellers.md` |
| Price negotiation | `negotiation.md` |
| Platform differences | `platforms.md` |

## Core Rules

### 1. Platform Selection: Taobao vs Tmall

| Platform | Best For | Trust Level | Price Range |
|----------|----------|-------------|-------------|
| **Tmall (天猫)** | Brand authenticity guaranteed | ⭐⭐⭐⭐⭐ | Higher, fixed prices |
| **Taobao (淘宝)** | Variety, bargains, unique items | ⭐⭐⭐☆☆ | Lower, negotiable |
| **Taobao Global** | Overseas buyers | ⭐⭐⭐⭐☆ | Higher (intl shipping) |

**Decision Matrix:**
- Electronics/Luxury → Tmall (authenticity matters)
- Fashion/Accessories → Taobao (variety + savings)
- Bulk purchases → Taobao (negotiation possible)
- First-time buyer → Tmall (simpler, safer)

### 2. Seller Vetting Protocol

**Check These Before Buying:**

| Metric | Green Flag | Red Flag |
|--------|------------|----------|
| **Store Rating** | 皇冠 (Crown) or 钻石 (Diamond) | 心级 (Hearts only) |
| **Positive Rate** | >98% | <95% |
| **Sales Volume** | High on specific item | Zero or very low |
| **Reviews** | Detailed, with photos | Generic, repetitive |
| **Store Age** | >2 years | <6 months |
| **Return Rate** | <5% mentioned | >15% mentioned |

**Seller Tiers (highest to lowest):**
1. 天猫旗舰店 (Tmall Flagship) - Brand official
2. 天猫专卖店 (Tmall Authorized) - Authorized dealer
3. 皇冠卖家 (Crown Seller) - High volume/experience
4. 钻石卖家 (Diamond Seller) - Established
5. 心级卖家 (Heart Seller) - Newer, higher risk

### 3. Search Optimization

**Effective Search Strategies:**

| Goal | Search Technique |
|------|------------------|
| Exact item | Use model numbers, brand + product code |
| Best price | Sort by price + filter by sales volume |
| Quality | Add "正品" (authentic) or "专柜" (counter) to query |
| Reviews | Sort by "销量" (sales) to see popular items |

**Search Operators:**
- Quotes for exact match: "iPhone 15 Pro"
- Minus to exclude: 手机 -二手 (phone -used)
- Price range: 手机 1000-2000
- Location filter: Add city for faster shipping

### 4. Price Intelligence & Negotiation

**Understanding Pricing:**

| Price Type | What It Means |
|------------|---------------|
| **标价** (Listed) | Often inflated 20-50% for negotiation room |
| **券后价** (After Coupon) | Realistic starting point |
| **到手价** (Final Price) | After all discounts applied |

**Negotiation Tactics (Wangwang Chat):**
1. **Bulk discount:** "买X件能便宜吗?" (Can you discount for X items?)
2. **Price match:** "别家卖X元" (Others sell for X)
3. **Shipping waiver:** "能包邮吗?" (Can you include shipping?)
4. **Gift request:** "能送小礼物吗?" (Any free gifts?)

**Timing for Best Prices:**
- 3.8 (Women's Day), 6.18, 11.11, 12.12 - Major sales
- End of month - Sellers hit quotas
- Late night (11PM-1AM) - Flash deals
- New store openings - Grand opening discounts

### 5. Product Authentication

**Spotting Fakes:**

| Authentic | Suspicious |
|-----------|------------|
| Detailed product photos (5+) | Stock images only |
| Specific model numbers | Vague descriptions |
| "专柜正品" (counter authentic) | "高仿" (high copy) in description |
| Brand authorization certificates | No proof of authenticity |
| Consistent branding | Logo slightly off |

**For Luxury/High-Value Items:**
- Request "专柜验货" (counter verification)
- Check for "假一赔十" (fake = 10x compensation) promise
- Verify seller's authorization documents
- Use Tmall for guaranteed authenticity

### 6. Shipping & Logistics

| Shipping Type | Speed | Cost | Best For |
|---------------|-------|------|----------|
| 普通快递 | 3-7 days | ¥8-15 | Standard items |
| 顺丰速运 | 1-3 days | ¥15-25 | Urgent/valuable |
| 菜鸟驿站 | 3-5 days | Often free | Convenient pickup |
| 同城配送 | Same day | ¥10-20 | Local purchases |

**Free Shipping Threshold:**
- Usually ¥99-299 depending on store
- Some items "包邮" (free shipping) regardless
- Tmall Supermarket often has free shipping promotions

### 7. Payment Protection

**Payment Flow:**
1. Pay → Alipay holds funds (担保交易)
2. Seller ships → You receive
3. Confirm receipt → Funds released
4. **Never confirm before receiving!**

**Dispute Window:**
- Open dispute within 15 days of receipt
- Evidence needed: photos, chat logs
- Taobao intervenes if seller uncooperative

**Refund Types:**
- 仅退款 (Refund only) - Item not received
- 退货退款 (Return + refund) - Item issues
- 换货 (Exchange) - Wrong size/color

### 8. Communication Best Practices

**Wangwang (旺旺) Chat Tips:**
- Save all chat records (dispute evidence)
- Confirm details in writing: color, size, model
- Ask about stock before ordering
- Request real product photos if uncertain

**Common Phrases:**
- "有货吗?" - Do you have stock?
- "什么时候发货?" - When will you ship?
- "发什么快递?" - Which courier?
- "能开发票吗?" - Can you provide invoice?

## Common Traps

- **Too good to be true pricing** → Likely fake or bait-and-switch
- **No reviews or generic reviews** → Bot reviews, avoid
- **Pressure to confirm receipt early** → Scam signal
- **Off-platform payment requests** → Never pay outside Taobao
- **Vague shipping timelines** → Ask specifics before buying
- **Ignoring return policy** → Check before purchasing
- **Not comparing sellers** → Same item, vastly different prices/quality

## Platform-Specific Features

### Taobao Features
- 闲鱼 (Xianyu) integration - Secondhand deals
- 直播 (Live streaming) - Real-time product demos
- 淘金币 - Loyalty points for discounts
- 聚划算 - Group buying deals

### Tmall Features
- 天猫超市 - Grocery delivery
- 天猫国际 - Overseas products
- 品牌闪购 - Flash sales
- 88VIP - Membership program (free shipping, discounts)

## Related Skills

Install with `clawhub install <slug>` if user confirms:
- `shopping` — general shopping assistance
- `vip` — VIP.com flash sale guidance
- `jd` — JD.com shopping guidance
- `ecommerce` — broader ecommerce patterns

## Feedback

- If useful: `clawhub star alibaba-shopping`
- Stay updated: `clawhub sync`
