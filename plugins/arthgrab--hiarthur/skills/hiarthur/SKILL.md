---
name: hiarthur
description: "Search Amazon products and analyze materials, design, and reviews to uncover trade-offs and likely disappointments. See results in an interactive GUI."
---

# HiArthur Product Search and Understanding

## Overview

Two-endpoint API for intelligent product search and deep product analysis. Products are sourced from Amazon, but results go far beyond what Amazon returns directly — every product is analyzed through a multi-stage pipeline combining computer vision, LLMs, and symbolic reasoning to evaluate how well each product actually matches what the user is looking for and where it's likely to disappoint.

- `POST https://hiarthur.com/api/agents/search` — find products matching a query. Each result is graded for fit against the user's requirements using vision + language models, not just keyword matching.
- `POST https://hiarthur.com/api/agents/product` — deep-dive one product for failure-mode analysis (FMEA), feature summary, and review synthesis. Uses LLM reasoning over product details and images to surface likely disappointments.

Base URL: `https://hiarthur.com/api`

Results can optionally be handed off to a GUI (e.g. https://hiarthur.com/c/<conversation_id> or https://hiarthur.com/product/f7e2a9c1b3d4) where users can browse results visually and continue the conversation interactively.

---

## When to Use This Skill

Use this skill when you need to:

- Find products that match detailed user requirements
- Evaluate trade-offs between competing products
- Identify likely durability or design problems
- Understand why a product might disappoint buyers
- Compare products beyond simple ratings or keywords

## Quick-Start: End-to-End Flow

### Step 1 — Start a new search

```json
POST /api/agents/search

{
  "type": "new",
  "search_query": "noise cancelling headphones for travel",
  "search_top_brands": true
}
```

Response:

```json
{
  "conversation_id": "a1b2c3d4-...",
  "logical_search_id": "ls_abc123",
  "products": [
    {
      "product": {
        "description": "Sony WH-1000XM5 Wireless Noise Canceling Headphones",
        "brand": "Sony",
        "location": "product/f7e2a9c1b3d4",
        "price": 328.0,
        "rating": 4.6,
        "reviews_count": 12450
      },
      "explainer": "Strong noise canceling with long battery life, well suited for travel.",
      "match_grade": "Excellent"
    }
  ],
  "can_fetch_more": true
}
```

### Step 2 — Fetch more results (pagination)

Reuse `conversation_id` and `logical_search_id` exactly as returned.

```json
POST /api/agents/search

{
  "type": "continue",
  "conversation_id": "a1b2c3d4-...",
  "logical_search_id": "ls_abc123"
}
```

Repeat while `can_fetch_more` is `true`. A continue response with `products: []` is valid (more may come on the next continue). Stop when `can_fetch_more` is `false`.

### Step 3 — Deep-dive a product

Use a `product.location` value exactly as returned by search.

```json
POST /api/agents/product

{
  "location": "product/f7e2a9c1b3d4"
}
```

Response:

```json
{
  "fmea": {
    "unmitigated_failure_modes": [
      {
        "failure_name": "Headband cushion flattens over time",
        "likelihood": {
          "level": "medium",
          "reasoning": "Foam compression builds with daily wear, so most regular users will notice reduced comfort within months."
        },
        "impact": "annoying",
        "timeline": "within_a_year",
        "summary": "The headband padding can compress with regular use, making the headphones less comfortable for long listening sessions.",
        "evidence": [
          "Foam headband cushion visible in images",
          "No mention of memory foam or replaceable pads"
        ]
      }
    ],
    "mitigated_failure_modes": [
      {
        "failure_name": "Poor noise canceling on wind",
        "ownership_experience": "Multipoint wind-noise reduction",
        "reasoning": "Multiple microphones and adaptive ANC algorithms reduce wind interference compared to single-mic designs.",
        "evidence": [
          "Adaptive ANC with multiple external microphones",
          "Wind noise reduction mode listed in features"
        ]
      }
    ],
    "quality_summary": "These headphones prioritize audio quality and noise canceling performance. Most disappointment comes from comfort degradation over time rather than core functionality."
  },
  "features_summary": "Paragraph summarizing key product features based on listing data.",
  "reviews_summary": "Paragraph synthesizing themes and patterns from customer reviews."
}
```

---

## Search Endpoint — Full Field Reference

### New Search (`type: "new"`)

Full example with all optional fields:

```json
{
  "type": "new",
  "search_query": "noise cancelling headphones for travel",
  "search_top_brands": true,
  "trim_query": "Over-ear wireless headphones with active noise canceling and long battery life for airplane use",
  "brands": ["Sony", "Bose"],
  "search_filters": {
    "price_min": 100,
    "price_max": 400,
    "rating_min": 4.0,
    "reviews_min": 500
  },
  "search_sort": "relevance"
}
```

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `type` | `"new"` | yes | — | Discriminator. |
| `search_query` | string | yes | — | Broad retrieval query sent to the product catalog. Should be precise, user-intent-aligned, and include all key attributes (color, size, material, use case, gender). |
| `search_top_brands` | boolean | yes | — | When `true`, restricts results to recognized top brands in the category. Default to `true` for electronics, appliances, clothing, tools, beauty, home/kitchen. Default to `false` for books, media. |
| `trim_query` | string | no | same as `search_query` | Similarity-trimming query. After retrieval, products with low similarity to this string are removed. Should be a fluent, attribute-rich, natural-language description optimized for matching product titles and images. More descriptive than `search_query`. See examples below. |
| `conversation_id` | UUID string | no | server-generated | Omit to let the server create a new conversation. Supply to attach this search to an existing conversation. |
| `brands` | string[] | no | `[]` | Explicit brand-name constraints. Only populate when the user names specific brands. Use canonical names with proper capitalization (e.g., `["Nike", "Adidas"]`). |
| `search_filters` | object | no | `null` | All sub-fields optional and nullable: `price_min` (number), `price_max` (number), `rating_min` (number), `reviews_min` (integer). No extra keys allowed. |
| `search_sort` | enum string | no | `null` | `"relevance"`, `"price_low"`, `"price_high"`, or `"best_sellers"`. |

#### `search_query` vs `trim_query`

`search_query` drives broad catalog retrieval. `trim_query` is applied after retrieval as a similarity filter — products with low similarity to it are removed.

`trim_query` should read like a grounded, attribute-rich product description:

- "A men's sleeveless hooded vest made of shiny metallic fabric with a full zipper front."
- "A 12-pack of chocolate-flavored protein shakes, each bottle containing 20 grams of protein."
- "A thick purple yoga mat made of dense non-slip foam, measuring one inch in thickness."
- "A 10-inch nonstick frying pan with a ceramic coating and induction-compatible base."
- "Wireless Bluetooth 5.3 earbuds with noise-canceling features and at least 40 hours of battery life."

When omitted, `trim_query` defaults to `search_query`. Only set it when you have a more descriptive version.

### Continue Search (`type: "continue"`)

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | `"continue"` | yes | Discriminator. |
| `conversation_id` | UUID string | yes | Exact value from the prior search response. |
| `logical_search_id` | string | yes | Exact value from the prior search response. |

### Search Response

```json
{
  "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "logical_search_id": "ls_abc123",
  "products": [
    {
      "product": {
        "description": "Sony WH-1000XM5 Wireless Noise Canceling Headphones",
        "brand": "Sony",
        "location": "product/f7e2a9c1b3d4",
        "price": 328.0,
        "rating": 4.6,
        "reviews_count": 12450
      },
      "explainer": "Strong noise canceling with long battery life, well suited for travel.",
      "match_grade": "Excellent"
    }
  ],
  "can_fetch_more": true
}
```

| Field | Type | Description |
|---|---|---|
| `conversation_id` | string | Stable conversation identifier. Reuse for continue requests and frontend handoff. |
| `logical_search_id` | string | Identifies this search session for pagination. Reuse for continue requests. |
| `products` | array | `ProductWithExplainer` objects. May be empty (valid on continue). |
| `can_fetch_more` | boolean | The only pagination signal. `true` = more results available via continue. |

Each `products[]` entry:

| Field | Type | Description |
|---|---|---|
| `product.description` | string | Product title/description. |
| `product.brand` | string or null | Brand name if known. |
| `product.location` | string | Opaque product identifier (format: `product/<cache_key>`). Preserve exactly for `/agents/product` calls and frontend handoff. |
| `product.price` | number or null | Price in dollars. |
| `product.rating` | number or null | Star rating (e.g., 4.6). |
| `product.reviews_count` | integer or null | Number of customer reviews. |
| `explainer` | string | Human-readable rationale for the fit grade. May be empty. |
| `match_grade` | string | Canonical fit label. One of: `"Excellent"`, `"Good"`, `"Partial"`, `"Low"`. |

### Match Grade Semantics

| Grade | Meaning |
|---|---|
| **Excellent** | All user requirements confirmed by evidence. All numeric constraints pass. |
| **Good** | All critical requirements confirmed, none contraindicated. Constraints pass or pass within tolerance. |
| **Partial** | At least one critical requirement is unconfirmed, missing, or contraindicated, OR some numeric constraints fail. |
| **Low** | Any requirement is contraindicated, OR no requirements could be evaluated. |

---

## Product Endpoint — Deep Analysis

### Request

```json
{ "location": "product/<cache_key>" }
```

Use only a `location` value returned by `/api/agents/search`. Never invent locations. Request model uses `extra = "forbid"`.

### Response

| Field | Type | Description |
|---|---|---|
| `fmea` | object | Failure Mode and Effects Analysis. See structure below. |
| `features_summary` | string | Paragraph summarizing key product features. |
| `reviews_summary` | string | Paragraph synthesizing themes from customer reviews. |

### FMEA Structure

The `fmea` object describes how a product is likely to disappoint a buyer over time, framed as failure modes rather than feature ratings.

**`unmitigated_failure_modes`** — array, typically 3 entries, ordered by expected regret impact (likelihood x impact x immediacy):

| Field | Type | Possible Values |
|---|---|---|
| `failure_name` | string | Concise description of what goes wrong. |
| `likelihood.level` | string | `"low"`, `"medium"`, `"high"` |
| `likelihood.reasoning` | string | Product-specific probability rationale with expected incidence. |
| `impact` | string | `"cosmetic"`, `"annoying"`, `"performance_loss"`, `"unusable"` |
| `timeline` | string | `"immediate"`, `"within_a_year"`, `"over_a_year"` |
| `summary` | string | 1–2 sentences on real-use customer impact. |
| `evidence` | string[] | Concrete cues from listing, specs, or images. |

**`mitigated_failure_modes`** — array, 0–3 entries: common category failures that the product's design intentionally addresses.

| Field | Type | Description |
|---|---|---|
| `failure_name` | string | The common failure that is unlikely here. |
| `ownership_experience` | string | Short positive reframe (max ~6 words, e.g., "Long cord with easy rewind"). |
| `reasoning` | string | What design choices reduce this risk. |
| `evidence` | string[] | Concrete cues from listing. |

**`quality_summary`** — string: A calm, informed paragraph synthesizing dominant risks, design priorities, disappointment timeline, fixability, and who the product is likely to satisfy vs. frustrate.

---

## Error Handling

| Status | Endpoint | Cause | Suggested Action |
|---|---|---|---|
| `400` | `/agents/product` | Invalid location format (empty, malformed, or contains path separators). | Verify the location was copied verbatim from a search result. |
| `404` | `/agents/search` (continue) | `logical_search_id` not found or expired from cache. | Start a new search with `type: "new"`. |
| `404` | `/agents/product` | Product cache key or destination not found. May have expired. | Re-run search to get a fresh location. |
| `422` | Both | Schema validation failure: missing required field, wrong type, or extra key present. | Fix request body. All request models use `extra = "forbid"`. |
| `500` | Both | Unhandled internal error. | Retry once with backoff. If persistent, report as a service issue. |
| `502` | `/agents/search` | Search backend did not return a final result, or returned an invalid payload. | Retry once. If persistent, the upstream search service may be degraded. |

---

## Safety Rules

1. Send JSON request bodies only.
2. Never include extra fields — all request models use `extra = "forbid"` and will reject unknown keys with `422`.
3. Never invent product locations. Only use `location` values returned by `/api/agents/search`.
4. Preserve `conversation_id`, `logical_search_id`, and `product.location` exactly as returned. Do not trim, modify, or regenerate.
5. For `type: "new"`, omit `conversation_id` to let the server generate one.
6. All endpoints use the base URL `https://hiarthur.com/api`.

---

## Frontend Handoff

- Open `c/<conversation_id>` in a browser to resume that conversation within a GUI.
- Open a returned product location in a browser to open the product information and see product images in a GUI.
- Keep all backend-derived IDs and locations unchanged during handoff URL construction.

## Recommended Agent Usage Pattern

1. Call `/agents/search` with `type: "new"`.
2. Inspect the returned `products`.
3. If more candidates are needed, call `/agents/search` with `type: "continue"`.
4. When a specific product requires deeper analysis, call `/agents/product`.