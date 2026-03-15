---
name: money-radar
description: "Real-time financial sign-up bonus radar. Query bank, broker, U-card, crypto exchange and remittance offers with bonus details, conditions and referral links."
---

# MoneyRadar - Financial Sign-up Bonus Query

Query financial sign-up bonus and promotional offers. Covers banks, brokers, U-cards (virtual debit cards), crypto exchanges, SIM cards, remittance services, and more.

## When to Use

Activate this skill when the user asks about:
- Sign-up bonuses for banks, brokers, or exchanges
- U-card / virtual card recommendations
- Financial account opening promotions
- Comparing broker offers (US, HK, Singapore)
- Crypto exchange sign-up rewards
- Remittance or money transfer deals

## Data Source

All data is served from a static JSON file hosted on GitHub Pages:

```bash
curl -s "https://laosji.net/data/referrals.json"
```

No API keys or authentication required.

## Data Structure

The JSON file contains an array of category objects, each with a list of items:

```json
[
  {
    "category": "券商",
    "category_en": "Brokers",
    "items": [
      {
        "platform_zh": "富途证券",
        "platform_en": "Futu Securities",
        "bonus_zh": "送1股苹果 + 最高HK$1800",
        "bonus_en": "1 Apple share + up to HK$1800",
        "conditions_zh": ["开户入金HK$10000", "30天内完成"],
        "conditions_en": ["Deposit HK$10000", "Complete within 30 days"],
        "regions": ["HK", "US", "SG"],
        "link": "https://...",
        "invite_code": "ABC123",
        "is_hot": true
      }
    ]
  }
]
```

## Query Commands

### Fetch All Offers
```bash
curl -s "https://laosji.net/data/referrals.json" | jq '.'
```

### Filter by Category
Available categories: 券商(Brokers), 新加坡券商(SG Brokers), 银行(Banks), U卡(U-Cards), 交易所(Exchanges), 汇款(Remittance), SIM卡(SIM Cards), 工具(Tools)

```bash
# Fetch U-card offers
curl -s "https://laosji.net/data/referrals.json" | jq '.[] | select(.category == "U卡")'

# Fetch broker offers
curl -s "https://laosji.net/data/referrals.json" | jq '.[] | select(.category == "券商")'
```

### Filter by Region
```bash
# Fetch offers available in Singapore
curl -s "https://laosji.net/data/referrals.json" | jq '[.[] | .items |= [.[] | select(.regions | index("SG"))] | select(.items | length > 0)]'
```

### Fetch Hot/Featured Offers
```bash
curl -s "https://laosji.net/data/referrals.json" | jq '[.[] | .items |= [.[] | select(.is_hot == true)] | select(.items | length > 0)]'
```

### Search by Platform Name
```bash
# Search for "Wise"
curl -s "https://laosji.net/data/referrals.json" | jq '[.[] | .items |= [.[] | select(.platform_en | test("Wise"; "i") or .platform_zh | test("Wise"; "i"))] | select(.items | length > 0)]'
```

## Response Fields

Each item in a category contains:

| Field | Type | Description |
|-------|------|-------------|
| `platform_zh` | string | Platform name (Chinese) |
| `platform_en` | string | Platform name (English) |
| `bonus_zh` | string | Bonus summary (Chinese) |
| `bonus_en` | string | Bonus summary (English) |
| `conditions_zh` | string[] | Requirements (Chinese) |
| `conditions_en` | string[] | Requirements (English) |
| `regions` | string[] | Available regions (US, HK, SG, etc.) |
| `link` | string | Sign-up referral link |
| `invite_code` | string | Invite/referral code (if available) |
| `is_hot` | bool | Featured/recommended flag |

## Output Format

Present offers to the user in this format:

```
### [Platform Name] - [Bonus Summary]

**Regions**: [region list]
**Conditions**:
- [condition 1]
- [condition 2]

**Sign up**: [link]
**Invite code**: [invite_code] (if available)
```

When listing multiple offers, group them by category with a header. Detect the user's language preference:
- Chinese user → use `_zh` fields
- English user → use `_en` fields

## Important Notes

- This is **read-only** static data. Updated periodically.
- The `link` field contains referral tracking. Always use the provided link.
- No API key required — data is publicly accessible via GitHub Pages.
