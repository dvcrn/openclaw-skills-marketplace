---
name: PDD Shopping
description: "Navigate Pinduoduo (拼多多) with smart group buying strategies, seller vetting, and bargain hunting techniques."
homepage: https://clawic.com/skills/pdd
---

## When to Use

User wants to shop on Pinduoduo (拼多多). Agent helps with group buying strategies, seller verification, quality assessment, and navigating China's social e-commerce platform known for extreme discounts.

## Quick Reference

| Topic | File |
|-------|------|
| Group buying guide | `groupbuy.md` |
| Seller vetting | `sellers.md` |
| Quality assessment | `quality.md` |

## Core Rules

### 1. Understanding PDD's Model

**Social Commerce + Group Buying:**

| Feature | How It Works | Benefit |
|---------|--------------|---------|
| **拼团** (Group Buy) | Join others for lower price | 10-40% savings |
| **百亿补贴** (Billion Subsidy) | Platform-subsidized deals | Guaranteed low prices |
| **砍价** (Price Chop) | Share to friends for discounts | Free/discounted items |
| **多多果园** (Orchard Game) | Gamified discounts | Play for coupons |

**Platform Positioning:**
- Lowest prices among major platforms
- Higher risk, requires more diligence
- Best for: non-branded goods, daily essentials, agricultural products
- Avoid for: high-end electronics, luxury, time-sensitive needs

### 2. Store Type Hierarchy

| Badge | Meaning | Trust Level |
|-------|---------|-------------|
| **品牌** (Brand) | Official brand store | ⭐⭐⭐⭐⭐ |
| **旗舰店** (Flagship) | Authorized flagship | ⭐⭐⭐⭐⭐ |
| **专卖店** (Specialty) | Category specialist | ⭐⭐⭐⭐☆ |
| **普通店** (Regular) | Individual seller | ⭐⭐⭐☆☆ |

**PDD-Specific Indicators:**

| Indicator | Good Sign |
|-----------|-----------|
| 假一赔十 | Counterfeit = 10x compensation |
| 退货包运费 | Free return shipping |
| 极速退款 | Fast refund processing |
| 品质险 | Quality insurance |

### 3. Group Buying Mastery

**How 拼团 Works:**

| Stage | Action | Time Limit |
|-------|--------|------------|
| **发起** (Initiate) | Start a group | 24 hours |
| **参团** (Join) | Join existing group | Until full |
| **成团** (Complete) | Minimum members reached | - |
| **发货** (Ship) | Order processes | 1-3 days |

**Group Size Typical:**
- Small: 2 people (easy to complete)
- Medium: 3-5 people
- Large: 10+ people (biggest discounts)

**Strategies:**
1. Join existing groups (faster)
2. Share with family/friends
3. Use PDD's "免拼" (skip group) for urgent orders
4. Check "即将成团" (about to complete) for quick wins

### 4. The 百亿补贴 Program

**What It Is:**
- Platform subsidizes prices
- Guaranteed lowest price
- Usually on branded goods
- Limited quantity/time

**How to Spot:**
- Look for "百亿补贴" red badge
- Prices often 20-50% below market
- Includes iPhones, Dyson, Nike, etc.

**Cautions:**
- Verify it's "官方补贴" (official subsidy)
- Check seller is authorized
- Compare with JD/Tmall prices
- Read recent reviews carefully

### 5. Seller Vetting on PDD

**Critical Checks:**

| Metric | Minimum Threshold | Ideal |
|--------|-------------------|-------|
| **店铺评分** | >4.5 | >4.7 |
| **销量** | >100 | >1000 |
| **评价数** | >50 | >500 |
| **店铺年龄** | >6 months | >1 year |

**Review Analysis:**
- Look for photo reviews (真实晒图)
- Check "默认" (default) reviews, not just "好评"
- Read 1-2 star reviews for common issues
- Verify "已拼" (grouped) count is high

**Red Flags:**
- No photo reviews
- Generic/duplicate review text
- Price too good to be true
- Store opened <3 months ago
- High return rate mentioned

### 6. Category-Specific Strategies

**Agricultural Products (农产品):**
- PDD's strength
- Direct from farmers
- Check origin (产地)
- Seasonal buying = best prices

**Daily Essentials:**
- Extremely competitive pricing
- Bulk buying saves more
- Generic brands often sufficient

**Electronics:**
- High risk category
- Only buy from 百亿补贴 or brand stores
- Verify warranty terms
- Record unboxing video

**Clothing:**
- Check size charts carefully
- Sizing often runs small
- Read "尺码反馈" (sizing feedback)
- Photo reviews essential

### 7. Payment & Protection

**Payment Options:**
- 微信支付 (WeChat Pay) - Most common
- 支付宝 (Alipay) - Also accepted
- 多多钱包 (PDD Wallet) - Occasional discounts

**PDD Buyer Protection:**

| Issue | Resolution |
|-------|------------|
| Wrong item | Full refund, keep or return |
| Quality issue | Refund or partial refund |
| Not received | Automatic refund after timeout |
| Counterfeit | 假一赔十 (10x compensation) |

**Return Policy:**
- 7-day return for most items
- 退货包运费 = free return shipping
- Some items non-returnable (food, custom)

## Common Traps

- **Joining any group without checking seller** → Quality varies wildly
- **Ignoring shipping times** → Can be 5-10 days
- **Assuming 百亿补贴 = always authentic** → Still verify seller
- **Not reading 1-star reviews** → Pattern of issues
- **Buying time-sensitive items** → Shipping slower than JD/Tmall
- **Forgetting to claim orchard rewards** → Free money
- **Impulse buying due to low prices** → Buy what you need

## PDD vs Other Platforms

| Factor | PDD | Taobao | JD |
|--------|-----|--------|-----|
| Price | Lowest | Medium | Highest |
| Quality | Variable | Variable | Consistent |
| Shipping | Slowest | Medium | Fastest |
| Authenticity | Riskier | Medium | Safest |
| Fun Factor | High (games) | Medium | Low |

**When to Use PDD:**
- Price is primary concern
- Buying everyday items
- Not in a hurry
- Willing to research sellers
- Agricultural products

## Related Skills

Install with `clawhub install <slug>` if user confirms:
- `taobao` - Taobao marketplace guide
- `jd-shopping` - JD.com shopping
- `vip` - VIP flash sales
- `alibaba-shopping` - Taobao/Tmall guide

## Feedback

- If useful: `clawhub star pdd`
- Stay updated: `clawhub sync`
