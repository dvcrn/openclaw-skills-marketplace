---
name: yhd
description: "Shop YHD.com (1号店) with smart deal finding, daily flash sales, fresh grocery navigation, and membership benefits guidance. Use when the user wants help shopping on 1号店, comparing grocery deals, understanding membership benefits, timing flash sales, or choosing fresh-food purchasing strategies. NOT for: placing real orders, handling payments, or scraping live account data."
---

## When to Use

User wants to shop on YHD.com (1号店). Agent helps with daily deals, fresh grocery shopping, 1号店会员 benefits, price comparison, and finding the best deals on China's leading membership-based shopping platform.

## Quick Reference

| Topic | File |
|-------|------|
| Daily deals timing | `timing.md` |
| Fresh grocery guide | `fresh.md` |
| Membership benefits | `membership.md` |
| Price comparison | `pricing.md` |

## Core Rules

### 1. Daily Flash Sale Timing

YHD operates on **daily rotating flash sales** (每日秒杀):

| Sale Type | Timing | Best For |
|-----------|--------|----------|
| Morning Fresh | 8:00 AM - 10:00 AM | Fresh produce, dairy, bakery |
| Midday Essentials | 12:00 PM - 2:00 PM | Daily necessities, snacks |
| Afternoon Deals | 3:00 PM - 5:00 PM | Home goods, personal care |
| Evening Rush | 8:00 PM - 10:00 PM | Premium items, restocks |
| Midnight Clearance | 12:00 AM - 2:00 AM | Last chance deals, limited stock |

**Strategy:**
- Check tomorrow's preview at 8:00 PM daily
- Set reminders for high-demand categories
- Popular fresh items sell out within 30 minutes
- 1号店会员 get 30-minute early access

### 2. Fresh Grocery Navigation

YHD's strength is **fresh food and groceries**:

| Category | Best Time to Buy | Quality Indicators |
|----------|------------------|-------------------|
| Fresh Produce | Morning 8-10 AM | Harvest date, origin label |
| Meat & Seafood | Morning 8-10 AM | Slaughter/delivery date |
| Dairy & Eggs | Any time | Check expiration dates |
| Bakery & Bread | Morning 8-10 AM | Bake time stamp |
| Frozen Foods | Evening restocks | Temperature indicator |

**Pro Tip:**
- 产地直发 (Direct from origin) = fresher, better prices
- 今日特惠 (Today's special) updates hourly
- 买1赠1 (Buy 1 Get 1) common on produce

### 3. 1号店会员 Benefits

**Membership Tiers:**

| Tier | Annual Fee | Key Benefits |
|------|------------|--------------|
| Regular | Free | Basic deals, standard shipping |
| 1号店会员 | ¥198/year | Free shipping, member prices, early access |
| 1号店PLUS | ¥298/year | All above + cashback + priority support |

**Member-Exclusive Features:**
- 会员价 (Member prices): 5-20% off regular prices
- 会员日 (Member day): 8th of every month, extra discounts
- 免邮券 (Free shipping coupons): Monthly allowance
- 专属客服 (Priority support): Faster response

**Break-Even Analysis:**
- Shop >¥200/month → membership pays for itself
- Heavy fresh grocery buyers → highly recommended

### 4. Price Intelligence

**Price Comparison Strategy:**
- YHD prices vs Tmall/JD: Often competitive on groceries
- 1号店会员价 vs regular: Always check both
- Bundle deals: "满99减20" (Spend ¥99, save ¥20) common
- Flash sale prices: Can be 30-50% off regular

**Price Tracking:**
- 降价通知 (Price drop alerts): Set on wishlist items
- 历史价格 (Price history): Check before buying
- Seasonal patterns: Fresh produce cheaper in harvest season

### 5. Quality Assessment for Fresh Items

**Fresh Produce Grading:**

| Grade | Indicator | Recommendation |
|-------|-----------|----------------|
| A级/A Grade | Premium select | Best quality, higher price |
| B级/B Grade | Standard | Good value, everyday choice |
| 产地直发 | Direct from farm | Freshest, seasonal |
| 进口/Imported | International | Check origin, premium pricing |

**Red Flags:**
- No harvest/pack date listed
- Vague origin description
- Reviews mentioning spoilage
- Photos don't match description

**Green Signals:**
- 溯源码 (Traceability code)
- Same-day or next-day delivery
- High repeat purchase rate
- Detailed farm/region information

### 6. Shipping & Delivery

| Aspect | Details |
|--------|---------|
| Standard Delivery | Same-day or next-day (major cities) |
| Delivery Windows | 2-hour slots, 8:00 AM - 10:00 PM |
| Free Shipping Threshold | ¥99 for non-members, free for 1号店会员 |
| Cold Chain | Available for fresh/frozen items |
| Delivery Fee | ¥6-15 depending on distance/time |

**Delivery Optimization:**
- Choose morning slots for freshest produce
- Evening slots often have more availability
- Combine orders to hit free shipping threshold
- Cold chain items delivered in insulated packaging

### 7. Smart Cart Building

**Timing Strategies:**
1. **Early Morning Shopping:** Best selection of fresh items
2. **Flash Sale Stacking:** Combine multiple concurrent deals
3. **Member Day Shopping:** 8th of month for extra discounts
4. **Coupon Hunting:** Check app banners for stackable coupons

**Category Bundling:**
- Fresh + Pantry = Free shipping easier to reach
- Seasonal items + Regular items = Better overall value
- Bulk buying on non-perishables = Lower unit cost

**Payment Optimization:**
- 1号店钱包: Occasional extra discounts
- Bank partnerships: Check for card-specific deals
- First-order: Usually has welcome discount
- Referral codes: Share with friends for mutual benefits

## Common Traps

- **Overbuying perishables** → Fresh items have limited shelf life
- **Ignoring delivery windows** → Missing your slot means next-day delivery
- **Not checking expiration** → Especially on dairy and packaged foods
- **Missing member benefits** → Non-members pay more and shipping fees
- **Flash sale FOMO** → Compare with regular prices, not all "deals" are deals
- **Ignoring minimum order** → Factor in delivery fees if under threshold

## YHD-Specific Features to Leverage

### 1. 今日特惠 (Today's Deals)
- Updates hourly with new flash sales
- Limited quantity, first-come-first-served
- Set notifications for favorite categories

### 2. 产地直发 (Direct from Origin)
- Farm-to-table produce
- Better prices, fresher quality
- Seasonal availability

### 3. 1号店会员日 (Member Day)
- 8th of every month
- Extra discounts on top of member prices
- Exclusive product launches

### 4. 预售 (Pre-sale)
- Lock in prices for upcoming seasonal items
- Pay deposit, pay balance on delivery
- Common for imported fruits, seafood

## Related Skills

Install with `clawhub install <slug>` if user confirms:
- `vip` — VIP.com flash sale shopping
- `taobao` — Taobao marketplace guidance
- `jd` — JD.com shopping guidance
- `shopping` — general shopping assistance
- `grocery` — grocery shopping optimization

## Feedback

- If useful: `clawhub star yhd`
- Stay updated: `clawhub sync`
