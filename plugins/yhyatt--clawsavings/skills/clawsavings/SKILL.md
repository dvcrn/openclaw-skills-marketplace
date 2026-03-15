---
name: clawsavings
description: "ClawSavings"
---

# ClawSavings — Israeli Discounts & Price Comparison

> **USP:** Knows which Israeli card saves you most at any store — 72 stores, 24 verified deals, one answer.

---

## When to Use This Skill

Activate when the user asks about:
- **Best card/club** to use at a specific store ("באיזה כרטיס לויקטורי?")
- **Discounts, vouchers, deals** for Israeli stores
- **Saving money** on purchases in Israel
- **Cheapest place** to buy a product ("איפה הכי זול?")
- Keywords: "הנחה", "חיסכון", "כרטיס", "מועדון", "שובר", "זול"

---

## Loading the Knowledge Base — LOAD ONLY WHAT YOU NEED

The full `discounts.json` is ~20KB. **Do not load the whole file.**  
Instead, use targeted extraction to keep token cost minimal.

### Step 1 — Identify the category (always first)

```bash
python3 -c "
import json
d = json.load(open('~/.openclaw/workspace/skills/clawsavings/discounts.json'))
store = 'שם_החנות'  # replace with the queried store
cat = d['quick_lookup']['store_to_category'].get(store)
best = d['quick_lookup']['best_sources_by_category'].get(cat, [])
print('category:', cat)
print('best_sources:', best)
"
```

Cost: reads only `quick_lookup` — ~200 tokens total.

### Step 2 — Load just that category + source metadata

```bash
python3 -c "
import json
d = json.load(open('~/.openclaw/workspace/skills/clawsavings/discounts.json'))
cat = 'supermarkets'  # from step 1
out = {
    'category_data': d['categories'][cat],
    'sources_meta': {k: d['sources'][k] for k in d['quick_lookup']['best_sources_by_category'][cat]},
    'cache_ttl_days': d['meta']['cache_ttl_days']
}
import sys; json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
" 2>/dev/null
```

Cost: ~800–1,200 tokens (one category) vs ~5,000 (full file).  
**Savings: ~75% fewer tokens per query.**

### When the store is not in quick_lookup

Load only `quick_lookup.store_to_category` and tell the user the store isn't indexed yet, offer to check the HTZone or Poalim Wonder site.

---

## Decision Logic

### "Which card/club should I use at store X?"

1. Extract category via Step 1 above
2. Load category section via Step 2
3. For each source in `best_sources_by_category[category]`:
   - Check `type`: `pos_discount` = automatic at checkout · `voucher` = buy in advance · `cashback` = retroactive
   - Check `deals[]` and `cached_at` — is the deal data fresh? (TTL = 30 days)
   - Use `max_pct` as fallback if deals are empty/stale
4. Rank by `effective_pct` (deals) or `max_pct` (structural)
5. Answer concisely in Hebrew

**Response template:**
```
ל[חנות]:

1. **[מקור]** — [עסקה ספציפית או % מקסימום]
2. **[מקור]** — [עסקה ספציפית או % מקסימום]

💡 [טיפ מעשי אחד]
```

### "Where's cheapest for product X?"

General supermarket ranking (baked-in knowledge, no lookup needed):
- **Cheapest:** רמי לוי, אושר עד
- **Good value:** ויקטורי, יינות ביתן
- **Mid-range:** שופרסל, מגה
- **Expensive:** AM:PM, שופרסל אקספרס

For exact product prices → government XML (point to scraper, don't run it):
`https://github.com/OpenIsraeliSupermarkets/israeli-supermarket-scarpers`

### "How do I save most on X category?"

Load category → list all sources → explain the best combo (e.g. "buy a Poalim Wonder voucher AND pay with HTZone card if you have both").

---

## Cache Refresh (On-Demand)

**When to refresh:** `cached_at` is `null` OR more than 30 days old AND user needs exact deal price.

**How:**
1. Answer immediately using structural data (`max_pct`) — don't block the response
2. Note: "המחיר המדויק דורש בדיקה" 
3. If user confirms they want live price → use browser to fetch source URL
4. Parse deal rows → update `deals[]` + `cached_at` in discounts.json → save

**Refresh URLs (verified):**
| Source | URL |
|--------|-----|
| `poalim_wonder` | `https://www.bankhapoalim.co.il/he/Poalim-Wonder` + `/Shopping` sub-page |
| `htzone_club` | `https://www.htzone.co.il/sale/1147` (requires login + JS render) |
| `htzone_pos` | `https://www.htzone.co.il/sale/62` (requires login + JS render) |

**Model for cache refresh:**
- Simple pages (Poalim Wonder — no login required) → current model is sufficient
- HTZone pages (login + JS required) → browser automation with logged-in session needed; if not available, respond with structural data only and note the limitation

**Update the file after refresh:**
```bash
python3 -c "
import json
path = '~/.openclaw/workspace/skills/clawsavings/discounts.json'
d = json.load(open(path))
from datetime import date
d['categories']['CATEGORY']['sources']['SOURCE']['deals'] = [/* new deals */]
d['categories']['CATEGORY']['sources']['SOURCE']['cached_at'] = str(date.today())
json.dump(d, open(path,'w'), ensure_ascii=False, indent=2)
print('updated')
"
```

---

## Output Format

- **Language:** Hebrew (group speaks Hebrew)
- **Tone:** Short, practical, no fluff
- **Numbers:** Always show exact ₪ amounts when available (₪300 → ₪259)
- **POS vs Voucher:** Always clarify — automatic at checkout vs. buy in advance
- **Max length:** 5 lines unless multiple options worth listing

---

## Examples

**"באיזה כרטיס כדאי בויקטורי?"**
```
לויקטורי:
1. **פועלים וונדר** — שובר ₪300 ב-₪259 + 50 נקודות (13.7%)
2. **כרטיס הייטקזון** — עד 20% אוטומטית בקופה

💡 אם יש לך את שניהם — קנה שובר וונדר ושלם איתו עם כרטיס הייטקזון
```

**"יש הנחה לוולט?"**
```
וולט — פועלים וונדר: שובר ₪100 ב-₪80 + 25 נקודות (20% 🔥)
```

**"איפה הכי זול לקנות?"**
```
לסל קניות רגיל: רמי לוי / אושר עד הכי זולים.
אם יש לך פועלים וונדר — שובר רמי לוי ₪700 ב-₪620 (11.4%).
```

---

## Maintenance

**Quarterly (structural layer):** Check if HTZone/Poalim benefits structure changed → update `max_pct` → update `last_reviewed`

**On-demand (deal layer):** Refresh only when user asks + cache is stale → update `deals[]` + `cached_at`

---


## Limitations

1. HTZone specific deals require login + JS render — structural max_pct used as fallback
2. Gov XML price comparison not yet wired — reference only
3. Max / Isracard deals not yet researched
