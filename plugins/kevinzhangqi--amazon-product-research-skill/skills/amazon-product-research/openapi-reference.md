# APIClaw OpenAPI Reference

> Based on the public API documentation at `https://api.apiclaw.io/api-docs`
>
> Base URL: `https://api.apiclaw.io`
>
> Current scope: 5 endpoints for Amazon product research and seller analysis.

---

## Endpoints

1. `POST /openapi/v2/categories`
2. `POST /openapi/v2/markets/search`
3. `POST /openapi/v2/products/competitor-lookup`
4. `POST /openapi/v2/products/search`
5. `POST /openapi/v2/realtime/product`

---

## 1. `categories`

### Purpose
Query the Amazon category tree.

### Common use cases
- search categories by keyword
- confirm an exact category path
- fetch child categories under a parent
- inspect category size using `productCount`

### Request patterns
- no parameters → root categories
- `categoryId` → exact category by ID
- `categoryPath` → exact category by path
- `parentCategoryId` → child categories by parent ID
- `parentCategoryPath` → child categories by parent path
- `categoryKeyword` → keyword-based category search

### Main request fields
| Field | Type | Notes |
|------|------|------|
| marketplace | String | `US` by default |
| categoryId | String | exact category ID |
| categoryPath | List<String> | exact category path |
| parentCategoryId | String | fetch children by ID |
| parentCategoryPath | List<String> | fetch children by path |
| categoryKeyword | String | search term |

### Main response fields
| Field | Type | Meaning |
|------|------|---------|
| categoryId | String | category ID |
| categoryName | String | category name |
| categoryPath | List<String> | full path |
| parentCategoryId | String | parent ID |
| parentCategoryName | String | parent name |
| hasChildren | Boolean | whether the category has children |
| isRoot | Boolean | whether it is a root category |
| level | Integer | category depth |
| link | String | Amazon category URL |
| productCount | Integer | product count |

---

## 2. `markets/search`

### Purpose
Return aggregate market-level metrics for a category.

### Best for
- category validation
- market sizing
- concentration analysis
- new-SKU opportunity analysis
- brand and seller density analysis

### Core request fields
| Field | Type | Notes |
|------|------|------|
| categoryKeyword | String | keyword-based category filter |
| categoryPath | List<String> | exact category path |
| dateRange | String | default `30d` |
| sampleType | String | default `by_sale_100` |
| newProductPeriod | String | what counts as "new" |
| topN | String | top-N sample size |
| page | Integer | pagination |
| pageSize | Integer | pagination |
| sortBy | String | default market revenue-oriented sort |
| sortOrder | String | `asc` or `desc` |

### Common filter ranges
- `sampleAvgMonthlySalesMin/Max`
- `sampleAvgMonthlyRevenueMin/Max`
- `sampleAvgPriceMin/Max`
- `sampleAvgRatingMin/Max`
- `sampleAvgReviewCountMin/Max`
- `sampleBrandCountMin/Max`
- `sampleSellerCountMin/Max`
- `sampleFbaRateMin/Max`
- `sampleAmzRateMin/Max`
- `sampleNewSkuRateMin/Max`
- `topSalesRateMin/Max`
- `topBrandSalesRateMin/Max`
- `topSellerSalesRateMin/Max`

### Main response fields
| Field | Meaning |
|------|---------|
| categories | category path |
| categoryLevel | category depth |
| totalSkuCount | active SKU count |
| sampleSkuCount | sampled SKU count |
| sampleAvgPrice | average price |
| sampleAvgMonthlySales | average monthly unit sales |
| sampleAvgMonthlyRevenue | average monthly revenue per sampled product |
| sampleAvgBsr | average BSR |
| sampleAvgRating | average rating |
| sampleAvgReviewCount | average review count |
| sampleBrandCount | sampled brand count |
| sampleSellerCount | sampled seller count |
| sampleFbaRate | FBA share |
| sampleAmzRate | Amazon retail share |
| sampleNewSkuCount | new SKU count |
| sampleNewSkuRate | new SKU rate |
| topAvgMonthlySales | top-N average monthly sales |
| topAvgMonthlyRevenue | top-N average monthly revenue |
| topSalesRate | top-N sales concentration |
| topRevenueRate | top-N revenue concentration |
| topBrandSalesRate | top-brand concentration |
| topSellerSalesRate | top-seller concentration |

---

## 3. `products/competitor-lookup`

### Purpose
Find competitor products by keyword, brand, seller, ASIN, or category.

### Best for
- direct competitor scans
- brand-level competitor mapping
- ASIN-centered competitive analysis
- category-level competitor sets

### Main request fields
| Field | Type | Notes |
|------|------|------|
| keyword | String | search keyword |
| brand | String | brand filter |
| seller | String | seller filter |
| asin | String | ASIN filter |
| marketplace | String | default `US` |
| categoryPath | List<String> | category filter |
| dateRange | String | default `30d` |
| page | Integer | pagination |
| pageSize | Integer | pagination |
| sortBy | String | `monthlySales`, `monthlyRevenue`, `bsr`, `price`, `rating`, `reviewCount`, `listingDate` |
| sortOrder | String | `asc` or `desc` |

### Response object
Returns a list of `Product` objects.

---

## 4. `products/search`

### Purpose
Search products using keyword, category, and multiple numeric filters.

### Best for
- product discovery
- low-competition screening
- growth-product screening
- price-band filtering
- white-space opportunity finding

### Main request fields
| Field | Type | Notes |
|------|------|------|
| keyword | String | keyword search |
| mode | String | optional mode selector |
| dateRange | String | optional |
| marketplace | String | default `US` |
| categoryPath | List<String> | category filter |
| onlyCategoryRank | Boolean | optional |
| page | Integer | pagination |
| pageSize | Integer | pagination |
| sortBy | String | `monthlySales`, `monthlyRevenue`, `bsr`, `price`, `rating`, `reviewCount`, `listingDate` |
| sortOrder | String | `asc` or `desc` |

### Common numeric filters
- `monthlySalesMin/Max`
- `revenueMin/Max`
- `childSalesMin/Max`
- `salesGrowthRateMin/Max`
- `bsrMin/Max`
- `subBsrMin/Max`
- `priceMin/Max`
- `ratingMin/Max`
- `reviewCountMin/Max`
- `listingAge`
- `variantCountMin/Max`
- `qaCountMin/Max`
- `monthlyNewReviewsMin/Max`
- `reviewRateMin/Max`
- `grossMarginMin/Max`
- `lqsMin/Max`
- `sellerCountMin/Max`

### Brand / seller / badge filters
| Field | Notes |
|------|-------|
| includeBrands | comma-separated |
| excludeBrands | comma-separated |
| includeSellers | comma-separated |
| excludeSellers | comma-separated |
| fulfillment | list filter |
| videoFilter | optional |
| badges | optional list |
| excludeKeywords | keyword exclusion |
| keywordMatchType | `fuzzy`, `phrase`, `exact` |

### Response object
Returns a list of `Product` objects.

---

## 5. `realtime/product`

### Purpose
Fetch a real-time product detail page snapshot for a single ASIN.

### Best for
- ASIN deep dives
- listing analysis
- review and feature extraction
- variant inspection
- buy-box inspection

### Main request fields
| Field | Type | Notes |
|------|------|------|
| asin | String | required |
| marketplace | String | supports multiple marketplaces |

### Main response fields
| Field | Meaning |
|------|---------|
| asin | ASIN |
| title | title |
| brand | brand |
| rating | average rating |
| ratingCount | rating count |
| reviewCount | review count |
| imageUrl | primary image |
| images | image set |
| categories | category path |
| features | bullet points |
| description | description |
| specifications | specification map |
| parentAsin | parent ASIN |
| variants | variant list |
| listingDate | listing date |
| ratingBreakdown | star distribution |
| topReviews | top reviews |
| attributes | product attributes |
| bestsellersRank | BSR details |
| link | Amazon product URL |
| dimensions | dimensions |
| weight | weight |
| isBundle | bundle flag |
| isUsed | used-product flag |
| buyboxWinner | buy-box info |

---

## Shared `Product` object fields

### Core identity
- `id`
- `asin`
- `parentAsin`
- `title`
- `imageUrl`
- `brand`
- `price`
- `listingDate`
- `fulfillment`
- `keywords`
- `categories`
- `categoryId`

### Rank fields
- `bsrRank`
- `bsrCategory`
- `bsrGrowth`
- `bsrGrowthRate`
- `subBsrRank`
- `subBsrCategory`
- `subBsrGrowth`
- `subBsrGrowthRate`

### Sales fields
- `salesMonthly`
- `salesRevenue`
- `salesGrowthRate`
- `childSalesMonthly`
- `childSalesRevenue`
- `parentSalesGrowthRate`

### Review fields
- `rating`
- `ratingCount`
- `reviewCount`
- `reviewMonthlyNew`
- `reviewRate`

### Listing / badge fields
- `isBestSeller`
- `isAmazonChoice`
- `isNewRelease`
- `hasAPlus`
- `hasVideo`

### Seller / economics fields
- `fbaFee`
- `profitMargin`
- `sellerCount`
- `buyboxSeller`
- `sellerLocation`

### Logistics / packaging fields
- `weight`
- `size`
- `packageWeight`
- `packageSize`

### Other fields
- `variantCount`
- `lqs`
- `qaCount`

---

## Common response envelope

```json
{
  "success": true,
  "data": {},
  "error": null,
  "meta": {
    "requestId": "unique_request_id",
    "timestamp": "ISO 8601",
    "total": 100,
    "page": 1,
    "pageSize": 20,
    "totalPages": 5
  }
}
```

---

## Practical guidance

Use this reference file only when you need:
- exact field names
- exact filter names
- response field definitions
- endpoint-by-endpoint parameter guidance

For normal usage, start with `SKILL.md` and only come back here if a workflow needs detailed parameter selection.
