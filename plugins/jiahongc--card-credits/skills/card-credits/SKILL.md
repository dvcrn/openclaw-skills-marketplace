---
name: card-credits
description: "Return statement credits and cash-like credits for one major-US credit card — amount, cadence, trigger rules, enrollment requirements, and restrictions. Covers 11 major US issuers including co-branded hotel and airline cards."
---

# Card Credits

Return the credits view of one exact card variant in compact format.

## When To Use

When the user asks about a card's statement credits, annual credits, or cash-back credits. Trigger phrases: "card-credits", "statement credits", "what credits", "annual credits", "perks".

## Workflow

1. **Resolve card identity** — normalize the input and match to one exact card variant.
2. **Search issuer only** — run one Brave Search API call scoped to the issuer domain. Do NOT search secondary sources.
3. **Compile** — combine search snippets with knowledge to fill all required sections.
4. **Confidence** — flag uncertain or conflicting claims.

## Step 1: Card Identity Resolution

Normalize the card name and resolve to an exact issuer + family + variant.

### Common Abbreviations

Only shorthands and ambiguous names need entries here. Cards with full, unambiguous names (e.g., "Chase Marriott Bonvoy Boundless", "Chase United Explorer", "American Express Hilton Honors Aspire") are resolved via search — no table entry needed.

| Input | Resolved |
|---|---|
| CSP | Chase Sapphire Preferred |
| CSR | Chase Sapphire Reserve |
| CFU | Chase Freedom Unlimited |
| CFF | Chase Freedom Flex |
| CIP | Chase Ink Business Preferred |
| CIC | Chase Ink Business Cash |
| CIU | Chase Ink Business Unlimited |
| Amex Gold | American Express Gold Card |
| Amex Plat | American Express Platinum Card |
| Amex Biz Gold | American Express Business Gold Card |
| Amex Biz Plat | American Express Business Platinum Card |
| Amex Blue Biz Plus | American Express Blue Business Plus Card |
| Amex Blue Biz Cash | American Express Blue Business Cash Card |
| Venture X | Capital One Venture X Rewards Credit Card |
| Venture X Business | Capital One Venture X Business Card |
| Savor | Capital One SavorOne / Savor (ambiguous — ask) |
| Spark Cash Plus | Capital One Spark Cash Plus |
| Spark Miles | Capital One Spark Miles |
| Double Cash | Citi Double Cash Card |
| Custom Cash | Citi Custom Cash Card |
| Ink Preferred | Chase Ink Business Preferred |
| Ink Cash | Chase Ink Business Cash |
| Ink Unlimited | Chase Ink Business Unlimited |
| Bilt | Bilt Blue / Obsidian / Palladium (ambiguous — ask) |
| Robinhood | Robinhood Gold Card / Cash Card (ambiguous — ask) |
| Aviator Red | Barclays AAdvantage Aviator Red World Elite Mastercard |
| Wyndham Rewards | Barclays Wyndham Rewards Earner Card / Plus / Business (ambiguous — ask) |
| Altitude Reserve | U.S. Bank Altitude Reserve Visa Infinite Card |
| Altitude Connect | U.S. Bank Altitude Connect Visa Signature Card |
| Altitude Go | U.S. Bank Altitude Go Visa Signature Card |
| Delta Gold | American Express Delta SkyMiles Gold Card |
| Delta Platinum | American Express Delta SkyMiles Platinum Card |
| Delta Reserve | American Express Delta SkyMiles Reserve Card |
| Delta Biz Gold | American Express Delta SkyMiles Gold Business Card |
| Delta Biz Plat | American Express Delta SkyMiles Platinum Business Card |
| Delta Biz Reserve | American Express Delta SkyMiles Reserve Business Card |

### Business vs Personal

Both personal and business credit cards are supported. If the user specifies "business" or "biz", resolve to the business variant. If a card name exists in both versions and the user does not specify, treat as ambiguous and ask.

### Ambiguity Rules

- If the input maps to 2+ plausible variants, return a **numbered choice list** and stop.
- If no match exists, return: "Could not match a card. Try including the full card name with issuer."

### Supported Issuers

American Express, Bank of America, Barclays, Bilt, Capital One, Chase, Citi, Discover, Robinhood, U.S. Bank, Wells Fargo.

## Step 2: Search (Issuer Only)

```bash
curl -sS "https://api.search.brave.com/res/v1/web/search?q=CARD+NAME+credits+benefits+site:ISSUER_DOMAIN&count=5" \
  -H "X-Subscription-Token: $BRAVE_API_KEY"
```

Use up to 1 secondary source (prefer Bankrate) for credit trigger details if needed. Combine the issuer search snippets with training knowledge.

## Required Output Sections

### `## 💳 Credits Overview`
Total annual credit value, number of distinct credits, general enrollment requirements.

### `## 🏷️ Credit Details`
Numbered list of each credit with amount, cadence (monthly/annual/semiannual), trigger (what purchase activates it), and restrictions.

### `## 📏 Usage Rules`
Enrollment requirements, expiration, stacking rules, clawback conditions.

### `## 📋 Confidence Notes`
Flag any detail that may have changed since training data.

## Output Rules

- Use one emoji per section heading and numbered lists for credits.
- Keep content to condensed facts — no prose padding.
- Omit the Card Identity section when the match is confident.
- Do not show inline links, sources footer, or YAML blocks in output.

## Confidence Definitions

- **confirmed**: supported by issuer terms or multiple approved sources
- **unconfirmed**: plausible but not fully resolved
- **conflicting**: sources disagree on a material fact
