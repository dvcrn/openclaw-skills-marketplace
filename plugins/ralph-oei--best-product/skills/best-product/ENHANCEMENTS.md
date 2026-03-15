# best-product Skill Enhancements

## Implemented

- v1.0.1 (2026-03-09): Added Link Verification rules, fixed markdown link format

---

## Planned

### Alternatives Feature

**Priority:** High

**Problem:** Top pick often out of stock or unavailable. Users need instant fallback.

**Proposed Implementation:**

```
Input: /best airfryer nl

Output:
🏆 TOP PICK
Philips Airfryer XXL — €149
[summary]
🔗 https://google.nl/...
❌ Out of stock at Coolblue, MediaMarkt

💎 ALTERNATIVE
 Ninja Foodi Max — €139
[summary, slightly different specs]
🔗 https://google.nl/...
✅ In stock at Coolblue

💶 ALTERNATIVE
Cosori Air Fryer — €99
[summary, budget alternative]
🔗 https://google.nl/...
✅ In stock at Amazon NL
```

**Data Sources:**
- Stock: Kieskeurig (has "voorraad" status), Coolblue API if available
- Alternatives: Find by price bracket + category similarity

**Technical approach:**
1. After finding top pick, check stock at major retailers via Kieskeurig
2. If out of stock → find similar-priced alternatives from same category
3. Flag with ✅/❌ stock status

---

### Price Alerts (Future)

- Store threshold in `~/.openclaw/cache/alerts.json`
- Daily cron checks Kieskeurig/Tweakers/Keepa
- Notify when price drops below threshold
