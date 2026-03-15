---
name: soilrich-ops
description: "Manage Soil Rich by John — website updates, blog/social content, ISDA compliance, orders, FFA programs. Notion-powered."
homepage: https://github.com/martc03/openclaw-ultimate
---

# Soil Rich by John — Operations

Manage the Soil Rich by John business from your phone. Website updates, content creation, compliance lookups, order tracking, and FFA program management.

**Website:** soilrichbyjohn.com (Next.js + Netlify)
**Products:** PREP (The Primer), BOOST (The Activator), FEED (The Sustainer)
**Location:** Boise, ID — 9601 W State St, Ste 101, 83714

## Commands

### `soil site update [page] [content]`
Update content on soilrichbyjohn.com.

```
soil site update products Update PREP price to $24.99
soil site update about Add new team member bio
```

Modifies files in `~/soilrich-website/`, commits the change, and offers to deploy via `site-deployer`.

### `soil site deploy`
Deploy the website to Netlify. Delegates to `site-deployer` skill. **Requires approval.**

```
soil site deploy
```

### `soil blog [topic]`
Draft a blog post. Saves draft to Notion "Soil Rich Content" database with Status=Draft.

```
soil blog Benefits of biochar for home gardens
soil blog Spring soil prep tips for Idaho gardeners
soil blog How PREP helps new lawns establish faster
```

Generates agriculture-focused content using Soil Rich's voice and product knowledge.

### `soil social [platform] [topic]`
Generate social media content. Saves to Notion "Soil Rich Content" database.

```
soil social instagram Spring soil prep tips with PREP
soil social facebook Customer spotlight: garden transformation
soil social twitter New blog post about biochar benefits
```

Platforms: instagram, facebook, twitter

### `soil compliance [product]`
Look up ISDA registration, label requirements, and regulatory references.

```
soil compliance PREP
soil compliance all
```

Reads from: Notion "Soil Rich Compliance" database.

**Quick reference (built-in):**

| Product | Old Name | ISDA # | Status |
|---------|----------|--------|--------|
| PREP (The Primer) | MooPea's | #75785 | Approved 10/31/25 |
| BOOST (The Activator) | MooMix | #75786 | Approved 10/31/25 |
| FEED (The Sustainer) | MooNuggs | #75787 | Approved 10/31/25 |
| MooPea's XL | — | #75788 | Approved, discontinued |

**Key compliance rules:**
- Idaho Code 22-2207 (Soil Amendment Act)
- AAPFCO Uniform Soil Amendment Bill
- Inert ingredients (Blackstrap Molasses, BioChar): listed in "Derived From" + "Soil Amending Ingredients", NOT in Guaranteed Analysis
- "Soil Amending Ingredients" is the required statutory heading
- **ISDA Contact:** Nathan Price, Ag Program Specialist, 208-701-7226, Nathan.Price@ISDA.IDAHO.GOV

### `soil products`
Show current product information.

```
soil products
```

Returns: Product names, old names, ISDA registrations, key ingredients, application rates.

### `soil ffa [topic]`
FFA (Future Farmers of America) program information.

```
soil ffa upcoming events in Boise
soil ffa sponsorship template
soil ffa Idaho FFA chapter contacts
```

Reads from: Notion "Soil Rich FFA" database. Can also search the web for current FFA events in Idaho.

### `soil order [query]`
Look up order or customer information.

```
soil order status for John Smith
soil order pending orders
soil order recent deliveries
```

Reads from: Notion "Soil Rich Orders" database.

### `soil label [product]`
Quick reference to label specifications and compliance details.

```
soil label BOOST
soil label all
```

Returns: Label dimensions, required text elements, Guaranteed Analysis content, Derived From section, Soil Amending Ingredients, regulatory references.

Sources from Notion compliance DB and the label compliance analysis document.

## Notion Databases

- **Soil Rich Orders** — Order tracking, customer inquiries
- **Soil Rich Content** — Blog drafts, social media posts
- **Soil Rich FFA** — FFA contacts, events, sponsorships
- **Soil Rich Compliance** — ISDA registrations, label specs, regulatory refs

## Data Sources

- Notion databases (listed above)
- Website repo: ~/soilrich-website
- Label files: ~/Library/Mobile Documents/com~apple~CloudDocs/Soil Rich by John/04-Label Creation/
- Compliance analysis: LABEL_COMPLIANCE_ANALYSIS.md in label files directory
