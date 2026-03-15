---
name: hermes-analysis
description: "亚马逊卖家数据分析（Hermes API V2）— 市场评估、选品分析、竞品研究"
---

# Hermes 数据分析 Skill (V2)

基于 Hermes V2 API 的亚马逊卖家数据分析工具。支持市场评估、产品搜索、竞品分析、实时数据获取。

## 快速开始

### 1. 获取 API Token

1. 访问 [Hermes 开发者平台](https://hermes.yesy.dev/api-docs) 注册账号
2. 登录后进入 API Keys 页面，创建新 Token
3. 复制生成的 `hms_live_xxx` 格式的 Token

### 2. 配置 Token

将 Token 设置为环境变量：

```bash
# macOS/Linux — 添加到 ~/.zshrc 或 ~/.bashrc
export HERMES_API_TOKEN="hms_live_your_token_here"

# 或在 Claude Code 项目中配置 .env 文件
echo 'HERMES_API_TOKEN=hms_live_your_token_here' >> .env
```

### 3. 验证

在 Claude Code 中输入：「分析 Throw Pillow Covers 市场」，确认 API 调用正常。

## API 配置

| 项目 | 值 |
|------|-----|
| Base URL | `https://hermes.spider.yesy.dev/openapi/v2` |
| 认证 | `Authorization: Bearer ${HERMES_API_TOKEN}` |
| 方法 | 全部 POST，Content-Type: application/json |
| 文档 | https://hermes.yesy.dev/api-docs |

**调用模板（所有接口通用）：**
```bash
curl -s -X POST "https://hermes.spider.yesy.dev/openapi/v2/{endpoint}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${HERMES_API_TOKEN}" \
  -d '{...}'
```

**通用响应结构：**
```json
{
  "success": true,
  "data": [...],
  "error": null,
  "meta": {
    "requestId": "xxx",
    "timestamp": "2026-01-01T00:00:00Z",
    "total": 100,
    "page": 1,
    "pageSize": 20,
    "totalPages": 5
  }
}
```

---

## 接口参考

### 1. categories — 类目搜索

**端点：** `POST /openapi/v2/categories`

查询亚马逊类目层级。支持按关键词搜索、按路径查询、按父类目获取子类目。5 种查询模式互斥，每次只用一种。

**请求参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| marketplace | string (enum: US, UK) | 否 | US | 站点 |
| categoryKeyword | string | 否 | - | 按关键词搜索类目（最常用） |
| categoryId | string | 否 | - | 按类目ID精确查询 |
| categoryPath | string[] | 否 | - | 按路径精确查询 |
| parentCategoryId | string | 否 | - | 获取某父类目的子类目 |
| parentCategoryPath | string[] | 否 | - | 按父路径获取子类目 |

**响应字段（Category）：**

| 字段 | 类型 | 说明 |
|------|------|------|
| categoryId | string | 类目ID |
| categoryName | string | 类目名称 |
| categoryPath | string[] | 完整路径，如 ["Home & Kitchen", "Bedding", "Pillowcases"] |
| parentCategoryId | string? | 父类目ID |
| parentCategoryName | string? | 父类目名称 |
| parentCategoryPath | string[]? | 父类目路径 |
| hasChildren | boolean | 是否有子类目 |
| isRoot | boolean | 是否根类目 |
| level | integer (1-9) | 层级深度 |
| marketplace | string | 站点 |
| link | string? | Amazon 链接 |
| productCount | integer | 产品数量 |

**调用示例：**
```bash
# 搜索"pillow"相关类目
curl -s -X POST "https://hermes.spider.yesy.dev/openapi/v2/categories" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${HERMES_API_TOKEN}" \
  -d '{"categoryKeyword": "pillow", "marketplace": "US"}'

# 获取某类目的子类目
curl -s -X POST "https://hermes.spider.yesy.dev/openapi/v2/categories" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${HERMES_API_TOKEN}" \
  -d '{"parentCategoryPath": ["Home & Kitchen", "Bedding"], "marketplace": "US"}'
```

---

### 2. markets/search — 市场数据

**端点：** `POST /openapi/v2/markets/search`

按类目获取市场聚合数据，包含销量、价格、集中度、品牌数等指标。用于市场可行性评估。

**请求参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| categoryKeyword | string | 否 | - | 按类目名关键词过滤 |
| categoryPath | string[] | 否 | - | 按类目路径精确查询 |
| marketplace | string | 否 | US | 站点 |
| dateRange | string | 否 | 30d | 时间范围 |
| sampleType | enum: by_sale_100, by_bsr_100, avg | 否 | by_sale_100 | 样本类型 |
| newProductPeriod | enum: 1, 3, 6, 12 | 否 | 3 | 新品定义周期（月） |
| topN | enum: 3, 5, 10, 20 | 否 | 10 | 头部卖家/品牌的 Top N |
| **筛选项（Min/Max 对）** |
| sampleAvgMonthlySales | number | 否 | - | 样本平均月销量 |
| sampleAvgMonthlyRevenue | number | 否 | - | 样本平均月销售额 |
| sampleAvgPrice | number | 否 | - | 样本平均价格 |
| sampleAvgBsr | number | 否 | - | 样本平均 BSR |
| sampleAvgRating | number | 否 | - | 样本平均评分 |
| sampleAvgReviewCount | number | 否 | - | 样本平均评论数 |
| sampleAvgGrossMargin | number | 否 | - | 样本平均毛利率 |
| totalSkuCount | integer | 否 | - | 总 SKU 数 |
| sampleSkuCount | integer | 否 | - | 样本 SKU 数 |
| topAvgMonthlySales | number | 否 | - | 头部平均月销量 |
| topAvgMonthlyRevenue | number | 否 | - | 头部平均月销售额 |
| topSalesRate | number | 否 | - | 头部销量集中率 |
| topBrandSalesRate | number | 否 | - | 头部品牌集中率 |
| topSellerSalesRate | number | 否 | - | 头部卖家集中率 |
| sampleBrandCount | integer | 否 | - | 样本品牌数 |
| sampleSellerCount | integer | 否 | - | 样本卖家数 |
| sampleFbaRate | number | 否 | - | FBA 占比 |
| sampleAmzRate | number | 否 | - | 亚马逊自营占比 |
| sampleNewSkuCount | integer | 否 | - | 新品数 |
| sampleNewSkuRate | number | 否 | - | 新品占比 |
| **分页与排序** |
| page | integer (>=1) | 否 | 1 | 页码 |
| pageSize | integer (1-100) | 否 | 20 | 每页数量 |
| sortBy | string (见下方枚举) | 否 | sampleAvgMonthlySaleAmt | 排序字段 |
| sortOrder | enum: asc, desc | 否 | desc | 排序方向 |

**sortBy 枚举值：** totalSkuCnt, sampleSkuCnt, sampleAvgPrice, sampleAvgMonthlySaleCnt, sampleAvgMonthlySaleAmt, sampleAvgBigCategoryBsr, sampleAvgRatingAmt, sampleAvgRatingCnt, sampleAvgGrossMarginRate, sampleBrandCnt, sampleSellerCnt, sampleFbaSkuRate, sampleNewSkuRate, topAvgMonthlySaleCnt, topAvgMonthlySaleAmt, topSaleCntRate, topBrandSaleCntRate, topSellerSaleCntRate

**响应字段（MarketDTOV2）：**

| 字段 | 类型 | 说明 |
|------|------|------|
| categories | string[] | 类目路径 |
| categoryLevel | integer | 类目层级 |
| totalSkuCount | integer | 总 SKU 数 |
| sampleSkuCount | integer? | 样本 SKU 数 |
| sampleAvgPrice | number? | 样本平均价格 |
| sampleAvgMonthlySales | number? | 样本平均月销量 |
| sampleAvgMonthlyRevenue | number? | 样本平均月销售额 |
| sampleTotalMonthlySales | number? | 样本总月销量 |
| sampleAvgBsr | number? | 样本平均 BSR |
| sampleAvgRating | number? | 样本平均评分 |
| sampleAvgReviewCount | number? | 样本平均评论数 |
| sampleAvgGrossMargin | number? | 样本平均毛利率 |
| sampleBrandCount | integer? | 品牌数 |
| sampleSellerCount | integer? | 卖家数 |
| sampleAvgSellerCount | number? | 平均卖家数 |
| sampleFbaRate | number? | FBA 占比 |
| sampleFbmRate | number? | FBM 占比 |
| sampleAmzRate | number? | 亚马逊自营占比 |
| sampleNewSkuCount | integer? | 新品数量 |
| sampleNewSkuRate | number? | 新品占比 |
| topAvgMonthlySales | number? | 头部平均月销量 |
| topAvgMonthlyRevenue | number? | 头部平均月销售额 |
| topAvgBsr | number? | 头部平均 BSR |
| topAvgSubBsr | number? | 头部平均子类目 BSR |
| topSalesRate | number? | 头部销量集中率 |
| topRevenueRate | number? | 头部收入集中率 |
| topBrandSalesRate | number? | 头部品牌集中率 |
| topSellerSalesRate | number? | 头部卖家集中率 |
| sampleSellerAddresses | string[]? | 卖家地址分布 |

**集中度指标说明：**
- `topSalesRate`：Top N 产品销量占总样本销量的比例。越高 = 市场越集中，新卖家进入越难
- `topBrandSalesRate`：Top N 品牌销量占比。越高 = 品牌垄断越强
- `topSellerSalesRate`：Top N 卖家销量占比。越高 = 卖家集中度越高

**调用示例：**
```bash
# 查询 Throw Pillow Covers 市场数据
curl -s -X POST "https://hermes.spider.yesy.dev/openapi/v2/markets/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${HERMES_API_TOKEN}" \
  -d '{
    "categoryPath": ["Home & Kitchen", "Bedding", "Pillow Covers"],
    "topN": "10",
    "marketplace": "US"
  }'
```

---

### 3. products/search — 产品搜索

**端点：** `POST /openapi/v2/products/search`

按关键词和筛选条件搜索产品。支持丰富的过滤和排序。

**请求参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| keyword | string | 否 | - | 搜索关键词 |
| mode | string | 否 | - | 搜索模式 |
| marketplace | enum: US, UK | 否 | US | 站点 |
| dateRange | string | 否 | 30d | 时间范围 |
| categoryPath | string[] | 否 | - | 类目路径过滤 |
| onlyCategoryRank | boolean | 否 | false | 仅显示类目排名 |
| keywordMatchType | enum: fuzzy, phrase, exact | 否 | - | 关键词匹配模式 |
| excludeKeywords | string | 否 | - | 排除关键词 |
| **销量/收入筛选** |
| monthlySalesMin/Max | integer (>=0) | 否 | - | 月销量 |
| revenueMin/Max | number (>=0) | 否 | - | 月收入 |
| childSalesMin/Max | integer (>=0) | 否 | - | 子 ASIN 月销量 |
| salesGrowthRateMin/Max | number | 否 | - | 销量增长率 |
| **排名筛选** |
| bsrMin/Max | integer (>=0) | 否 | - | 大类 BSR |
| subBsrMin/Max | integer (>=0) | 否 | - | 小类 BSR |
| bsrGrowthRateMin/Max | number | 否 | - | BSR 增长率 |
| **价格/评分筛选** |
| priceMin/Max | number (>=0) | 否 | - | 价格 |
| ratingMin/Max | number (0-5) | 否 | - | 评分 |
| reviewCountMin/Max | integer (>=0) | 否 | - | 评论数 |
| monthlyNewReviewsMin/Max | integer (>=0) | 否 | - | 月新增评论 |
| reviewRateMin/Max | number | 否 | - | 评论率 |
| **其他筛选** |
| fbaShippingMin/Max | number (>=0) | 否 | - | FBA 配送费 |
| listingAge | string | 否 | - | 上架时长 |
| variantCountMin/Max | integer (>=0) | 否 | - | 变体数 |
| qaCountMin/Max | integer (>=0) | 否 | - | Q&A 数 |
| grossMarginMin/Max | number | 否 | - | 毛利率 |
| lqsMin/Max | number (>=0) | 否 | - | Listing 质量分 |
| sellerCountMin/Max | integer (>=0) | 否 | - | 卖家数 |
| **品牌/卖家过滤** |
| includeBrands | string | 否 | - | 包含品牌（逗号分隔） |
| excludeBrands | string | 否 | - | 排除品牌（逗号分隔） |
| includeSellers | string | 否 | - | 包含卖家 |
| excludeSellers | string | 否 | - | 排除卖家 |
| fulfillment | string[] | 否 | - | 配送方式 |
| videoFilter | string | 否 | - | 视频筛选 |
| badges | string[] | 否 | - | 标签筛选 |
| **分页与排序** |
| page | integer (>=1) | 否 | 1 | 页码 |
| pageSize | integer (1-100) | 否 | 20 | 每页数量 |
| sortBy | enum (见下) | 否 | monthlySales | 排序字段 |
| sortOrder | enum: asc, desc | 否 | desc | 排序方向 |

**sortBy 枚举值：** monthlySales, monthlyRevenue, bsr, price, rating, reviewCount, listingDate

**响应字段（ProductDTOV2）：**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string? | 内部ID |
| asin | string? | ASIN |
| parentAsin | string? | 父 ASIN |
| title | string | 标题 |
| imageUrl | string? | 主图 URL |
| brand | string? | 品牌 |
| price | number? | 价格 |
| listingDate | string? | 上架日期 |
| fulfillment | string? | 配送方式 |
| keywords | string[]? | 关键词 |
| categories | string[]? | 类目路径 |
| categoryId | string? | 类目ID |
| bsrRank | integer? | 大类 BSR |
| bsrCategory | string? | BSR 大类名 |
| bsrCategoryLink | string? | BSR 类目链接 |
| bsrGrowth | number? | BSR 变化量 |
| bsrGrowthRate | number? | BSR 变化率 |
| subBsrRank | integer? | 小类 BSR |
| subBsrCategory | string? | 小类名 |
| subBsrCategoryLink | string? | 小类链接 |
| subBsrGrowth | number? | 小类 BSR 变化量 |
| subBsrGrowthRate | number? | 小类 BSR 变化率 |
| salesMonthly | integer? | 月销量 |
| salesRevenue | number? | 月销售额 |
| salesGrowthRate | number? | 销量增长率 |
| childSalesMonthly | integer? | 子 ASIN 月销量 |
| childSalesRevenue | number? | 子 ASIN 月销售额 |
| parentSalesGrowthRate | number? | 父 ASIN 销量增长率 |
| rating | number? | 评分 |
| ratingCount | integer? | 评分数 |
| reviewCount | integer? | 评论数 |
| reviewMonthlyNew | integer? | 月新增评论 |
| reviewRate | number? | 评论率 |
| isBestSeller | boolean? | Best Seller 标签 |
| isAmazonChoice | boolean? | Amazon Choice 标签 |
| isNewRelease | boolean? | New Release 标签 |
| hasAPlus | boolean? | 有 A+ 页面 |
| hasVideo | boolean? | 有视频 |
| fbaFee | number? | FBA 费用 |
| profitMargin | number? | 利润率 |
| sellerCount | integer? | 卖家数 |
| buyboxSeller | string? | Buy Box 卖家 |
| sellerLocation | string? | 卖家位置 |
| weight | string? | 重量 |
| size | string? | 尺寸 |
| packageWeight | string? | 包装重量 |
| packageSize | string? | 包装尺寸 |
| variantCount | integer? | 变体数 |
| lqs | number? | Listing 质量分 |
| qaCount | integer? | Q&A 数 |

**调用示例：**
```bash
# 搜索 throw pillow covers，按月销量排序
curl -s -X POST "https://hermes.spider.yesy.dev/openapi/v2/products/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${HERMES_API_TOKEN}" \
  -d '{
    "keyword": "throw pillow covers",
    "sortBy": "monthlySales",
    "sortOrder": "desc",
    "pageSize": 50,
    "marketplace": "US"
  }'
```

---

### 4. products/competitor-lookup — 竞品查询

**端点：** `POST /openapi/v2/products/competitor-lookup`

按关键词、品牌、ASIN 或卖家查找竞品。返回与 products/search 相同的产品结构。

**请求参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| keyword | string | 否 | - | 搜索关键词 |
| brand | string | 否 | - | 品牌过滤 |
| seller | string | 否 | - | 卖家过滤 |
| asin | string | 否 | - | ASIN 过滤 |
| marketplace | enum: US, UK | 否 | US | 站点 |
| dateRange | string | 否 | 30d | 时间范围 |
| categoryPath | string[] | 否 | - | 类目路径 |
| page | integer (>=1) | 否 | 1 | 页码 |
| pageSize | integer (1-100) | 否 | 20 | 每页数量 |
| sortBy | enum: monthlySales, monthlyRevenue, bsr, price, rating, reviewCount, listingDate | 否 | monthlySales | 排序 |
| sortOrder | enum: asc, desc | 否 | desc | 排序方向 |

**响应：** 与 products/search 完全相同（ProductDTOV2 列表）。

**调用示例：**
```bash
# 查找某品牌的竞品
curl -s -X POST "https://hermes.spider.yesy.dev/openapi/v2/products/competitor-lookup" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${HERMES_API_TOKEN}" \
  -d '{"brand": "MIULEE", "marketplace": "US", "pageSize": 20}'

# 查找某 ASIN 的竞品
curl -s -X POST "https://hermes.spider.yesy.dev/openapi/v2/products/competitor-lookup" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${HERMES_API_TOKEN}" \
  -d '{"asin": "B07XXXXXX", "marketplace": "US"}'
```

---

### 5. realtime/product — 实时产品数据

**端点：** `POST /openapi/v2/realtime/product`

获取亚马逊产品的实时详情，包括评论、变体、BSR、图片等。数据实时抓取，响应较慢（5-15秒）。

**请求参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| asin | string (10位字母数字) | **是** | - | 产品 ASIN |
| marketplace | enum: US, UK, DE, FR, IT, ES, JP, CA, AU, IN, MX, BR | 否 | US | 站点（支持更多站点） |

**响应字段（RealtimeProductDTO）：**

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | ASIN |
| title | string? | 标题 |
| brand | string? | 品牌 |
| rating | number? | 评分 |
| ratingCount | integer? | 评分总数 |
| reviewCount | integer? | 评论总数 |
| imageUrl | string? | 主图 |
| images | string[]? | 所有图片 |
| categories | string[]? | 面包屑类目 |
| features | string[]? | 要点（Bullet Points） |
| description | string? | 产品描述 |
| specifications | object? | 技术参数 |
| parentAsin | string? | 父 ASIN |
| listingDate | string? | 上架日期 |
| variants | array? | 变体列表（含 ASIN、属性、价格等） |
| ratingBreakdown | object? | 评分分布（1-5星占比） |
| topReviews | object? | 热门评论 |
| attributes | array? | 产品属性列表 |
| bestsellersRank | array? | BSR 排名列表（多类目） |
| link | string? | 产品链接 |
| dimensions | string? | 尺寸 |
| weight | string? | 重量 |
| isBundle | boolean? | 是否套装 |
| isUsed | boolean? | 是否二手 |
| buyboxWinner | object? | Buy Box 获胜者信息 |

**调用示例：**
```bash
curl -s -X POST "https://hermes.spider.yesy.dev/openapi/v2/realtime/product" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${HERMES_API_TOKEN}" \
  -d '{"asin": "B0CXXXXXX", "marketplace": "US"}'
```

---

## 分析流程

以下是基于 5 个接口组合使用的标准分析流程。根据用户需求选择合适的流程。

### 流程 1：市场可行性验证

> 适用场景：用户想了解某个品类/关键词的市场情况，判断是否值得进入

**Step 1 — 类目定位**
调用 `categories`（categoryKeyword）→ 获取 categoryPath，确认目标类目

**Step 2 — 市场指标**
调用 `markets/search`（categoryPath, topN:"10"）→ 获取市场聚合数据

**Step 3 — 头部产品分析**
调用 `products/search`（keyword, sortBy:monthlySales, pageSize:50）→ 查看头部产品

**分析要点：**
- 市场容量：sampleTotalMonthlySales、totalSkuCount
- 竞争强度：topSalesRate、topBrandSalesRate、topSellerSalesRate
- 进入门槛：sampleAvgReviewCount、sampleAvgRating
- 利润空间：sampleAvgGrossMargin、sampleAvgPrice
- 新品机会：sampleNewSkuRate、sampleNewSkuCount

### 流程 2：ASIN 深度分析

> 适用场景：用户有具体的 ASIN，想深入了解该产品

**Step 1 — 实时数据**
调用 `realtime/product`（asin）→ 获取评论、变体、BSR、图片等详情

**Step 2 — 竞品对比**
调用 `products/competitor-lookup`（asin）→ 找到该 ASIN 的竞品

**Step 3 — 关键词表现（可选）**
调用 `products/search`（keyword:产品相关关键词）→ 查看该关键词下的排名

### 流程 3：竞品研究

> 适用场景：用户想了解某品牌/卖家/关键词的竞品格局

**Step 1 — 竞品查找**
调用 `products/competitor-lookup`（keyword/asin/brand/seller）→ 竞品列表

**Step 2 — 头部竞品详情（可选）**
对 Top 3-5 竞品调用 `realtime/product` → 获取详情

### 流程 4：定价与利润分析

> 适用场景：帮助用户制定定价策略

**Step 1 — 类目均价**
调用 `markets/search`（categoryPath）→ sampleAvgPrice、sampleAvgGrossMargin

**Step 2 — 价格带分布**
调用 `products/search`（keyword, sortBy:monthlySales, pageSize:100）→ 统计各价格区间的产品数和销量

**分析要点：**
- 将产品按价格分段，统计每段的产品数量和平均月销量
- 找到"高销量 + 合理价格"的甜蜜区间
- 对比 FBA 费用和毛利率

### 流程 5：子类目扫描

> 适用场景：用户想在某个大类下找细分机会

**Step 1 — 获取子类目**
调用 `categories`（parentCategoryPath）→ 子类目列表

**Step 2 — 批量市场数据**
对每个子类目调用 `markets/search` → 获取各子类目的市场指标

**Step 3 — 对比排序**
按市场容量、竞争度、新品率等维度对子类目排序，找到最优细分

---

## 评估标准

### 市场健康度评估

| 指标 | 优秀 | 良好 | 一般 | 差 |
|------|------|------|------|-----|
| 市场容量（月销售额） | >$5M | $1M-$5M | $500K-$1M | <$500K |
| Top10 销量集中率 | <30% | 30%-50% | 50%-70% | >70% |
| Top10 品牌集中率 | <40% | 40%-60% | 60%-80% | >80% |
| 新品占比（3个月） | >15% | 10%-15% | 5%-10% | <5% |
| 平均评论数 | <200 | 200-500 | 500-1000 | >1000 |
| 平均毛利率 | >40% | 30%-40% | 20%-30% | <20% |
| 品牌数量 | >50 | 20-50 | 10-20 | <10 |

### 产品潜力评估

| 指标 | 高潜力 | 中等 | 较低 |
|------|--------|------|------|
| 月销量 | >500 | 100-500 | <100 |
| 评分 | >=4.3 | 4.0-4.3 | <4.0 |
| 评论数 | <500 | 500-2000 | >2000 |
| 毛利率 | >35% | 25%-35% | <25% |
| BSR 增长率 | 负值（排名上升） | 稳定 | 正值（排名下降） |
| 是否有 A+ | 有 | - | 无 |
| LQS 分数 | >8 | 5-8 | <5 |

---

## 注意事项

1. **站点支持**：products/search、markets/search、competitor-lookup 仅支持 US 和 UK；realtime/product 支持 12 个站点
2. **响应时间**：realtime/product 需要实时抓取，响应时间 5-15 秒；其他接口通常 1-3 秒
3. **分页限制**：pageSize 最大 100，大量数据需要翻页
4. **categoryPath 格式**：必须是字符串数组，如 `["Home & Kitchen", "Bedding", "Pillowcases"]`
5. **数据精度**：销量和收入为估算值，仅供参考
6. **调用频率**：避免短时间内大量调用，合理使用分页
7. **错误处理**：检查响应中的 `success` 字段和 `error` 对象
