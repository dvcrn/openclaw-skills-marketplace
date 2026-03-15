---
name: card-full
description: "Return a compact full report for one major-US credit card — fees, welcome offer, earning rates, redemption, credits, travel benefits, protections, mechanics, eligibility, and strategy. Covers 11 major US issuers including co-branded hotel and airline cards."
---

# Card Full

Research any major US credit card and return a compact, complete report.

## When To Use

When the user asks for a full credit card review, breakdown, or "tell me about [card]". Trigger phrases: "card-full", "full report", "tell me about the [card name]", "review [card name]".

## Workflow

1. **Resolve card identity** — normalize the input, fix abbreviations, and match to one exact card variant.
2. **Search** — run one Brave Search API call for the card's issuer page + secondary sources.
3. **Compile** — assemble the report using the required sections below.
4. **Confidence** — flag uncertain or conflicting claims in the Confidence Notes section.

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

- If the input maps to 2+ plausible variants (e.g., "Chase Sapphire" could be Preferred or Reserve), return a **numbered choice list** and stop. Do not guess.
- If no match exists, return: "Could not match a card. Try including the full card name with issuer."

### Supported Issuers

American Express, Bank of America, Barclays, Bilt, Capital One, Chase, Citi, Discover, Robinhood, U.S. Bank, Wells Fargo. If the card is from an unsupported issuer, return: "This card is not from a supported issuer."

## Step 2: Search

Run one Brave Search API call:

```bash
curl -sS "https://api.search.brave.com/res/v1/web/search?q=CARD+NAME+review+welcome+offer&count=20" \
  -H "X-Subscription-Token: $BRAVE_API_KEY"
```

Parse the JSON response — results are in `.web.results[]` with `.title`, `.url`, `.description` fields.

### Source Policy

- **Issuer-first**: always check the card's official product page before secondary sources.
- **Max 5 secondary sources** from this approved list:
  1. NerdWallet (nerdwallet.com) — preferred
  2. The Points Guy (thepointsguy.com) — preferred
  3. Doctor of Credit (doctorofcredit.com)
  4. Bankrate (bankrate.com)
  5. One Mile at a Time (onemileatatime.com)
  6. Upgraded Points (upgradedpoints.com)
- **Stop early** once all required sections are covered.
- **Disallowed**: Reddit, Facebook, Instagram, TikTok, X, YouTube, referral links, user forums.

### Issuer Domains (for classifying results, not constraining searches)

| Issuer | Domains |
|---|---|
| American Express | americanexpress.com, aboutamex.com |
| Bank of America | bankofamerica.com |
| Barclays | cards.barclaycardus.com |
| Bilt | bfrrewards.com |
| Capital One | capitalone.com |
| Chase | chase.com, media.chase.com |
| Citi | citi.com, citicards.com |
| Discover | discover.com |
| Robinhood | robinhood.com |
| U.S. Bank | usbank.com |
| Wells Fargo | wellsfargo.com |

## Step 3: Fetch Pages

Pick the top issuer URL and up to 2 secondary URLs (prefer thepointsguy.com and nerdwallet.com) from the search results. Fetch in parallel:

```bash
curl -sS -L "URL" | sed 's/<[^>]*>//g' | tr -s '\n' | head -200
```

Search snippets are too shallow for full reports — the actual pages have complete credit lists, rate tables, and benefit details.

## Step 4: Required Output Sections

Return compact markdown with these sections in order:

### `## 💰 Fees`
Annual fee, authorized user fee, foreign transaction fee, balance transfer fee, cash advance fee, late fee.

### `## 🎁 Welcome Offer`
Public bonus, spend requirement, qualification window, eligibility restrictions, lifetime/family language.

### `## 📈 Earning Rates`
Base rate, bonus categories with multipliers, caps, point currency.

### `## 🔄 Redemption`
Transfer partners summary, portal options, cash-out rates, minimum redemption.

### `## 🏷️ Credits`
Statement credits, cash-back rebates, and complimentary subscriptions with concrete dollar values only. Each credit with amount, cadence, trigger, and restrictions. Do NOT include enhanced earning rates (e.g., "5x on Lyft"), bonus point multipliers, or anniversary point bonuses — those go in Earning Rates.

### `## ✈️ Travel Benefits`
Lounge access, hotel status, rental car benefits, travel credits, companion fares.

### `## 🛡️ Protections`
Purchase protection, extended warranty, return protection, cell phone protection, fraud protections.

### `## ⚙️ Account Mechanics`
Virtual cards, authorized user handling, app capabilities, autopay notes.

### `## ✅ Eligibility`
Issuer family rules, known restriction language (e.g., Chase 5/24, Amex lifetime language).

### `## 🧭 Strategy`
Downgrade paths, no-fee fallback, ecosystem role, keeper value after year one.

### `## 📋 Confidence Notes`
Flag any uncertain, unconfirmed, or conflicting claims.

### `## 🔗 Sources`
Numbered list of URLs fetched, as markdown hyperlinks with short "Site - Topic" labels.

## Output Rules

- Use one emoji per section heading.
- When listing credits, fees, or any monetary amounts, sort from highest to lowest dollar value.
- Use numbered lists for list-heavy sections.
- Keep content to condensed facts — no prose padding.
- Omit the Card Identity section when the match is confident.
- Do not include YAML blocks in user-facing output.
- End every report with a `## 🔗 Sources` section listing each URL fetched during research as a markdown hyperlink with a short "Site - Topic" label, e.g. `[Chase - Sapphire Preferred](https://...)`.
- Do not show a "Why It Matters" section.

## Confidence Definitions

- **confirmed**: supported by issuer terms or multiple approved sources without disagreement
- **unconfirmed**: plausible but not fully resolved from approved sources
- **conflicting**: approved sources disagree on a material fact

Every report must include a `## 📋 Confidence Notes` section. Keep notes short and tied to concrete uncertainties.
