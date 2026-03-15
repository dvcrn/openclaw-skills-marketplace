---
name: Taobao Shopping
description: "Master Taobao with seller vetting, price negotiation, and deal hunting strategies for China's largest C2C marketplace."
homepage: https://clawic.com/skills/taobao
---

## When to Use

User wants to shop on Taobao (淘宝). Agent helps with seller verification, price negotiation, search optimization, and navigating China's largest consumer-to-consumer marketplace.

## Quick Reference

| Topic | File |
|-------|------|
| Seller ratings | `sellers.md` |
| Price negotiation | `negotiation.md` |
| Search tactics | `search.md` |

## Core Rules

### 1. Taobao vs Tmall: Know the Difference

| Feature | Taobao (淘宝) | Tmall (天猫) |
|---------|---------------|--------------|
| **Sellers** | Individual/C2C | Businesses/B2C |
| **Authenticity** | Varies | More reliable |
| **Price** | Lower, negotiable | Fixed, higher |
| **Service** | Varies by seller | Standardized |
| **Best For** | Variety, bargains | Brand certainty |

**Decision Framework:**
- Electronics/Luxury → Tmall (authenticity)
- Fashion/Novelty → Taobao (variety + price)
- Bulk buying → Taobao (negotiation)
- First-time buyer → Tmall (simpler)

### 2. Seller Rating System

**Understanding the Crowns:**

| Level | Symbol | Meaning |
|-------|--------|---------|
| **Hearts** | ❤️ | New seller (<1 year) |
| **Diamonds** | 💎 | Established (1-3 years) |
| **Blue Crowns** | 👑 | Experienced (3-5 years) |
| **Gold Crowns** | 👑👑 | Top tier (5+ years) |

**Key Metrics:**

| Metric | Good | Caution |
|--------|------|---------|
| **好评率** | >98% | <95% |
| **描述相符** | >4.7 | <4.5 |
| **服务态度** | >4.7 | <4.5 |
| **物流服务** | >4.7 | <4.5 |

**Store Age Check:**
- Click store name → "店铺印象"
- Look for开店时间 (opening date)
- Older stores generally more reliable

### 3. Search Optimization

**Effective Search Strategies:**

| Goal | Search Technique |
|------|------------------|
| Exact item | Model number + brand |
| Best price | Sort by price + check sales |
| Quality | Add "正品" or "专柜" |
| Trending | Sort by "销量" (sales) |

**Search Operators:**
```
"exact phrase"     → Exact match
word1 word2        → Both words
word1 -word2       → Exclude word2
price:100-200      → Price range
```

**Filter Combinations:**
- 天猫 (Tmall only) - Filter for reliability
- 包邮 (Free shipping) - Cost savings
- 货到付款 (COD) - Payment security
- 7天无理由 (7-day return) - Protection

### 4. Price Intelligence

**Understanding Taobao Pricing:**

| Price Type | Reality |
|------------|---------|
| **原价** | Often inflated 30-50% |
| **促销价** | Closer to real price |
| **券后价** | After coupon discount |
| **到手价** | Final after all discounts |

**Negotiation via Wangwang (旺旺):**

**Opening Lines:**
- "亲，能便宜点吗?" (Can you discount?)
- "买两件有优惠吗?" (Discount for two?)
- "包邮可以吗?" (Free shipping?)

**Tactics:**
1. **Bulk discount** - "买X件能便宜吗?"
2. **Price match** - "别家卖XX元"
3. **Shipping waiver** - "能包邮吗?"
4. **Gift request** - "有小礼物吗?"

**Best Times to Negotiate:**
- End of month (sales quotas)
- Morning (sellers more responsive)
- Before major sales (clear inventory)

### 5. Product Verification

**Spotting Fakes:**

| Authentic | Suspicious |
|-----------|------------|
| Detailed photos (5+) | Stock images only |
| Specific model numbers | Vague descriptions |
| "专柜正品" label | "高仿" in description |
| Brand certificates | No proof |

**For Branded Items:**
- Check for authorization documents
- Look for "假一赔十" promise
- Verify with brand's official store on Tmall
- Read 1-star reviews for authenticity complaints

### 6. Review Analysis

**Reading Reviews Effectively:**

| Review Type | Weight |
|-------------|--------|
| 有图评价 (With photos) | High - See real product |
| 追评 (Follow-up) | High - Long-term use |
| 默认好评 (Default) | Low - Often not genuine |
| 差评 (Negative) | High - Check patterns |

**Red Flags in Reviews:**
- Identical text across multiple reviews
- No photo reviews for visual products
- Sudden influx of 5-star reviews
- Mentions of "与描述不符" (not as described)

### 7. Payment & Protection

**Alipay Escrow (担保交易):**
1. You pay → Alipay holds money
2. Seller ships → You receive
3. You confirm → Money released
4. **Never confirm before receiving!**

**Dispute Timeline:**
- Open dispute within 15 days of receipt
- Provide evidence: photos, chat logs
- Taobao mediates if unresolved

**Refund Types:**
- 仅退款 - Item not received
- 退货退款 - Return + refund
- 换货 - Exchange item

**Wangwang Chat Tips:**
- Save all conversations
- Confirm details in writing
- Ask about stock availability
- Request real photos if uncertain

## Common Traps

- **Trusting stock photos** → Always check buyer photos
- **Ignoring seller ratings** → New sellers = higher risk
- **Not negotiating** → Prices often flexible
- **Buying without checking reviews** → Quality varies
- **Confirming receipt early** → Lose protection
- **Off-platform payments** → Never pay outside Taobao
- **Ignoring return policies** → Check before buying

## Taobao-Specific Features

### Useful Tools
- **淘宝直播** - Live shopping, extra discounts
- **闲鱼** - Secondhand marketplace
- **淘金币** - Loyalty points
- **聚划算** - Group buying deals
- **有好货** - Curated recommendations

### Mobile vs Desktop
- Mobile often has app-exclusive coupons
- Desktop better for detailed comparison
- Mobile "拍立淘" - Photo search
- Desktop extensions for price history

## Related Skills

Install with `clawhub install <slug>` if user confirms:
- `alibaba-shopping` - Taobao/Tmall combined guide
- `tmall` - Tmall-specific guidance
- `jd-shopping` - JD.com shopping
- `pdd` - Pinduoduo deals

## Feedback

- If useful: `clawhub star taobao`
- Stay updated: `clawhub sync`
