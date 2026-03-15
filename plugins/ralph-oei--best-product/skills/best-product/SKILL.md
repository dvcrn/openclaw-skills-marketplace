---
name: best-product
description: "Find the best products in any category with expert picks, value recommendations, and budget options across US, UK, and EU retailers."
homepage: https://github.com/openclaw/skills
---

# Skill: Product Recommender (/best)

Finds the best products in a category using authoritative review sources across US, EU, and UK.

## Trigger
`/best [product name]` — e.g., `/best airfryer`, `/best wireless earbuds`

## Sources

### Review Aggregators — US
| Source | Region | URL | Access |
|--------|--------|-----|--------|
| Wirecutter | US | nytimes.com/wirecutter | Public |
| RTINGS | US | rtings.com | Public |
| Consumer Reports | US | consumerreports.org | Public (summaries) |

### Review Aggregators — UK
| Source | Region | URL | Access |
|--------|--------|-----|--------|
| TechRadar UK | UK | techradar.com | Public |
| Which? | UK | which.co.uk | Public (summaries) |

### Review Aggregators — EU
| Source | Region | URL | Access |
|--------|--------|-----|--------|
| Tweakers | NL | tweakers.net | Public |
| Kieskeurig | NL/BE | kieskeurig.nl | Public |
| Consumentenbond | NL/BE | consumentenbond.nl | Public (summaries) |
| Testberichte.de | DE | testberichte.de | Public |
| Stiftung Warentest | DE | test.de | Public (summaries) |
| 01net | FR | 01net.com | Public |
| Les Numériques | FR | lesnumeriques.com | Public |
| Altroconsumo | IT | altroconsumo.it | Public |
| Xataka | ES | xataka.com | Public |
| Benchmark.pl | PL | benchmark.pl | Public |
| Komputer Świat | PL | komputerswiat.pl | Public |
| Test-Aankoop | BE | test-aankoop.be | Public (summaries) |

### Price Comparison Sources
| Source | Coverage | URL | Notes |
|--------|----------|-----|-------|
| Kieskeurig | NL/BE | kieskeurig.nl | Aggregates all NL/BE retailers, real-time prices |
| Tweakers Pricewatch | NL | tweakers.net/prijzen | Real-time NL pricing |
| Keepa | Amazon | keepa.com | Amazon price history (free tier) |
| Idealo | EU | idealo.co.uk | EU price comparison |
| PriceRunner | EU | pricerunner.com | Multi-country price comparison |

### Retailers (Availability)

#### United States
| Retailer | Website |
|----------|---------|
| Amazon | amazon.com |
| Best Buy | bestbuy.com |
| Walmart | walmart.com |

#### United Kingdom
| Retailer | Website |
|----------|---------|
| Amazon UK | amazon.co.uk |
| Currys | currys.co.uk |
| John Lewis | johnlewis.com |
| Argos | argos.co.uk |

#### Germany
| Retailer | Website |
|----------|---------|
| Amazon DE | amazon.de |
| Coolblue | coolblue.de |
| MediaMarkt DE | mediamarkt.de |
| Saturn | saturn.de |
| Otto | otto.de |

#### France
| Retailer | Website |
|----------|---------|
| Amazon FR | amazon.fr |
| MediaMarkt FR | mediamarkt.fr |
| Fnac | fnac.com |
| Darty | darty.com |
| Boulanger | boulanger.com |
| Cdiscount | cdiscount.com |

#### Italy
| Retailer | Website |
|----------|---------|
| Amazon IT | amazon.it |
| MediaMarkt IT | mediamarkt.it |
| Unieuro | unieuro.it |
| Euronics | euronics.it |

#### Spain
| Retailer | Website |
|----------|---------|
| Amazon ES | amazon.es |
| MediaMarkt ES | mediamarkt.es |
| El Corte Inglés | elcorteingles.es |
| Fnac | fnac.es |

#### Netherlands
| Retailer | Website |
|----------|---------|
| Amazon NL | amazon.nl |
| Coolblue | coolblue.nl |
| MediaMarkt NL | mediamarkt.nl |

#### Belgium
| Retailer | Website |
|----------|---------|
| Amazon BE | amazon.be |
| MediaMarkt BE | mediamarkt.be |
| Coolblue | coolblue.be |
| Krëfel | krefel.be |

#### Poland
| Retailer | Website |
|----------|---------|
| Amazon PL | amazon.pl |
| Media Expert | mediaexpert.pl |
| RTV Euro AGD | euroagd.pl |
| Komputronik | komputronik.pl |

#### Other EU Markets
| Country | Retailers |
|---------|-----------|
| Austria | Amazon AT, MediaMarkt AT |
| Sweden | Amazon SE, MediaMarkt SE |
| Denmark | Amazon DK |
| Finland | Amazon FI |
| Switzerland | Amazon CH |

## Workflow

1. **Parse query** — extract product category from user input
2. **Detect region** — default to US, allow override (e.g., `/best airfryer de` or `/best earbuds fr`)
3. **Search sources** — query relevant aggregator for top-rated products
4. **Filter by region** — keep products available in selected region
5. **Categorize picks:**
   - **Top Pick** — best overall
   - **Best Value** — best performance per dollar/pound/euro
   - **Budget** — solid option under $50/£40/€50
6. **Generate output** — 3 picks with summary + link
7. **Price rule:** Show approximate price range from search snippets (e.g., "€120-150"). Use "v.a. €X" for lowest found.
8. **Link rule:** Use direct Google search link with full product name: `https://www.google.[nl|de|co.uk]/search?q=[product-name]`. Default to user's region (detect from timezone or default to NL).
9. **Summary rule:** Always include 1-2 sentence summary explaining why it's top pick, best value, or budget in English.
10. **Language rule:** Always output in English (even for NL queries, translate summary)
11. **Cache** — store results for 6 hours in `~/.openclaw/cache/best-products/`

## Region Detection

| Command | Region | Retailers Checked |
|---------|--------|------------------|
| `/best [product]` | US | amazon.com, Best Buy, Walmart |
| `/best [product] uk` | UK | amazon.co.uk, Currys, John Lewis |
| `/best [product] de` | Germany | amazon.de, MediaMarkt, Saturn, Otto |
| `/best [product] fr` | France | amazon.fr, Fnac, Darty, Boulanger |
| `/best [product] it` | Italy | amazon.it, MediaMarkt, Unieuro |
| `/best [product] es` | Spain | amazon.es, MediaMarkt, El Corte Inglés |
| `/best [product] nl` | Netherlands | amazon.nl, Coolblue, MediaMarkt |
| `/best [product] be` | Belgium | amazon.be, MediaMarkt, Coolblue |
| `/best [product] pl` | Poland | amazon.pl, Media Expert, RTV Euro AGD |
| `/best [product] eu` | Generic EU | amazon.de, Coolblue, MediaMarkt |

## Output Format

```
🎯 /best [product]

📍 [US/UK/DE/FR/IT/ES/NL/BE/PL] — [date]

🏆 TOP PICK
[Product Name]
€[price range]
[1-sentence summary why]
🔗 https://www.google.nl/search?q=product+name

💎 BEST VALUE
[Product Name]
€[price range]
[1-sentence summary why]
🔗 https://www.google.nl/search?q=product+name

💶 BUDGET
[Product Name]
€[price range]
[1-sentence summary why]
🔗 https://www.google.nl/search?q=product+name
```

## Caching

- Location: `~/.openclaw/cache/best-products/`
- Format: `{product}-{region}.json` (e.g., `earbuds-us.json`)
- TTL: 6 hours
- Check cache first; if stale/missing, fetch fresh data

## Link Verification (MANDATORY)

**CRITICAL:** All output URLs MUST be working Google search links. No exceptions.

| Rule | Requirement |
|------|-------------|
| ✅ Use Google Search | `https://www.google.[nl|de|co.uk]/search?q=[full-product-name]` |
| ✅ Full product name | Always use exact name from reviews (e.g., "Philips Airfryer XXL 3000 Series NA342") |
| ✅ Region match | Use google.nl for NL, google.de for DE, google.co.uk for UK |
| ❌ No direct retailer links | These often block; Google search always works |
| ❌ No markdown links | Use raw URL format only: `🔗 https://www.google.nl/search?q=product` — never `[text](url)` |

**Verification workflow:**
1. Search reviews → get exact product names
2. Construct Google search URL with full product name
3. Verify the product name is accurate from trusted sources (Consumentenbond, Which?, etc.)
4. Output Google search link — user can click to see current prices

## External Endpoints

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| Brave Search API | Search queries only | Find review pages from trusted sources |
| Google Search URLs | Product names only | Generate price comparison links for user |
| web_fetch (review sites) | None — read-only | Extract product recommendations |

No personal data, credentials, or API keys are sent to external services.

## Privacy & System Access

- **Timezone detection:** Reads system timezone to default to user's region (can be overridden via command)
- **Cache:** Writes to `~/.openclaw/cache/best-products/` for 6 hours
- **No credentials required:** Uses built-in web tools only

## Security & Privacy

- **Data leaving the machine:** 
  - Product search terms → Brave Search API
  - Product names → Google Search (for price links)
- **Data at rest:** Results cached locally for 6 hours only
- **No credentials required:** Uses OpenClaw's built-in web_search and web_fetch tools
- **No PII:** No user identifiers, emails, or personal information processed

## Trust Statement

This skill uses publicly available review data from trusted sources (Wirecutter, RTINGS, Which?, Tweakers, Consumentenbond, etc.) and price data from major retailers (Amazon, Best Buy, MediaMarkt, Coolblue, etc.). No personal data is collected or sent to third parties beyond standard search queries.

By using this skill, only product search terms are sent to the Brave Search API. All product data comes from publicly accessible web pages.

## Model Invocation Note

This skill can be invoked autonomously when the user types `/best [product]`. Users can opt out by disabling this skill in their OpenClaw configuration.
