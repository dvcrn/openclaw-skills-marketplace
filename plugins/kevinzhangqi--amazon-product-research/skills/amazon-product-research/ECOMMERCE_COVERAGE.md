# 电商运营自然语言需求分析与覆盖度测试

## 一、从已安装 Skill 提取的自然语言需求

### 1. Amazon Seller Skill - 运营需求

#### 选品相关 (Product Selection)
| 自然语言需求 | 示例查询 | apiclaw 支持 |
|-------------|---------|-------------|
| 查找某类目热销产品 | "find best sellers in electronics" | ✅ markets/search |
| 分析类目市场容量 | "analyze market size for headphones" | ✅ markets/search |
| 查看类目竞争度 | "how competitive is wireless earbuds market" | ✅ markets/search |
| 查找新品机会 | "find new products with low competition" | ✅ products/search |
| 分析产品趋势 | "show trending products in home category" | ⚠️ 需扩展 |

#### 定价相关 (Pricing)
| 自然语言需求 | 示例查询 | apiclaw 支持 |
|-------------|---------|-------------|
| 查看竞品价格 | "what's the price range for bluetooth speakers" | ✅ markets/search |
| 分析价格分布 | "show price distribution in headphones category" | ✅ markets/search |
| 查找低价竞品 | "find cheapest wireless headphones" | ✅ products/search |
| 分析利润率 | "calculate profit margin for $30 product" | ❌ 需扩展 |
| 动态定价建议 | "suggest price for my product" | ❌ 需扩展 |

#### 跟踪竞争对手 (Competitor Tracking)
| 自然语言需求 | 示例查询 | apiclaw 支持 |
|-------------|---------|-------------|
| 查找某品牌产品 | "find all Sony products" | ✅ competitor-lookup |
| 分析品牌市场份额 | "what's Sony's market share in headphones" | ⚠️ 需扩展 |
| 查看竞品销量 | "how many units does competitor X sell" | ⚠️ 需扩展 |
| 跟踪竞品动态 | "track competitor B08N5WRWNW" | ❌ 需扩展 |
| 分析竞品评价 | "analyze reviews for competitor product" | ❌ 需扩展 |

#### 产品分析 (Product Analysis)
| 自然语言需求 | 示例查询 | apiclaw 支持 |
|-------------|---------|-------------|
| 查看产品详情 | "show details for ASIN B08N5WRWNW" | ✅ realtime/product |
| 分析产品评价 | "analyze reviews for B08N5WRWNW" | ❌ 需扩展 |
| 查看产品销量 | "how many sales for product X" | ⚠️ 需扩展 |
| 分析产品BSR | "what's the BSR for this product" | ✅ products/search |
| 查看产品历史 | "show price history for product X" | ❌ 需扩展 |

---

### 2. Competitive Analysis Skill - 分析需求

#### 竞争分析 (Competitive Analysis)
| 自然语言需求 | 示例查询 | apiclaw 支持 |
|-------------|---------|-------------|
| 对比竞品特性 | "compare features with competitor" | ❌ 需扩展 |
| 分析竞品定位 | "analyze competitor positioning" | ❌ 需扩展 |
| SWOT分析 | "do SWOT analysis for competitor X" | ❌ 需扩展 |
| 生成销售话术 | "create battle card vs competitor" | ❌ 需扩展 |
| 分析竞品优势 | "what are competitor's strengths" | ⚠️ 需扩展 |

---

### 3. Apify E-commerce Skill - 数据需求

#### 价格监控 (Price Monitoring)
| 自然语言需求 | 示例查询 | apiclaw 支持 |
|-------------|---------|-------------|
| 监控某产品价格 | "monitor price for product X" | ❌ 需扩展 |
| 检测MAP违规 | "check MAP violations for my brand" | ❌ 需扩展 |
| 跨平台比价 | "compare prices across Amazon and Walmart" | ❌ 需扩展 |

#### 评价分析 (Review Analysis)
| 自然语言需求 | 示例查询 | apiclaw 支持 |
|-------------|---------|-------------|
| 分析评价情感 | "analyze sentiment of reviews" | ❌ 需扩展 |
| 查找质量问题 | "find quality issues in reviews" | ❌ 需扩展 |
| 评价关键词提取 | "extract keywords from reviews" | ❌ 需扩展 |

#### 卖家发现 (Seller Discovery)
| 自然语言需求 | 示例查询 | apiclaw 支持 |
|-------------|---------|-------------|
| 查找未授权卖家 | "find unauthorized sellers" | ❌ 需扩展 |
| 发现新卖家 | "discover new sellers for product X" | ❌ 需扩展 |

---

## 二、覆盖度测试 (Coverage Test)

### 当前 apiclaw skill 支持的功能

```
✅ 已支持:
├── 类目查询 (categories)
│   ├── "list all categories"
│   ├── "有哪些类目"
│   └── "show subcategories of Electronics"
├── 市场分析 (markets/search)
│   ├── "analyze market for headphones"
│   ├── "市场分析 耳机类目"
│   └── "show market data for electronics"
├── 产品搜索 (products/search)
│   ├── "find wireless headphones under $50"
│   ├── "查找蓝牙耳机 价格低于200"
│   ├── "search for bluetooth speakers with 4+ stars"
│   └── "top 10 products in electronics sort by revenue"
├── 竞品查询 (competitor-lookup)
│   ├── "search by brand Sony"
│   └── "竞品分析 brand Sony"
└── 实时产品 (realtime/product)
    ├── "show me details for ASIN B08N5WRWNW"
    └── "查看 B08N5WRWNW 详情"
```

### 缺失的功能 (Gap Analysis)

```
❌ 未支持 (高优先级):
├── 评价分析
│   ├── 评价情感分析
│   ├── 评价关键词提取
│   └── 质量问题检测
├── 价格监控
│   ├── 历史价格跟踪
│   ├── MAP违规检测
│   └── 跨平台比价
├── 产品对比
│   ├── 多产品特性对比
│   ├── 价格对比分析
│   └── 销量对比
└── 趋势分析
    ├── 销量趋势
    ├── 价格趋势
    └── BSR趋势

❌ 未支持 (中优先级):
├── 利润率计算
├── 动态定价建议
├── 库存分析
├── 卖家发现
└── 销售话术生成
```

---

## 三、建议扩展的自然语言模式

### 1. 评价分析扩展

```python
# 新增 intent: review_analysis
review_patterns = [
    "analyze reviews for {asin}",
    "分析 {asin} 的评价",
    "what do customers say about {asin}",
    "find quality issues in reviews",
    "sentiment analysis for {asin}",
]

# 新增 endpoint: /openapi/v2/reviews/analyze
# 参数: asin, analysis_type (sentiment/keywords/quality)
```

### 2. 价格监控扩展

```python
# 新增 intent: price_monitoring
price_monitor_patterns = [
    "monitor price for {asin}",
    "track price changes for {asin}",
    "price history for {asin}",
    "check MAP violations for {brand}",
]

# 新增 endpoint: /openapi/v2/prices/history
# 参数: asin, date_range
```

### 3. 产品对比扩展

```python
# 新增 intent: product_comparison
comparison_patterns = [
    "compare {asin1} and {asin2}",
    "对比 {asin1} 和 {asin2}",
    "how does {asin1} compare to {asin2}",
    "feature comparison for {asin1} vs {asin2}",
]

# 新增 endpoint: /openapi/v2/products/compare
# 参数: asins[], comparison_fields[]
```

---

## 四、测试用例汇总

### 已覆盖的测试用例 (17个)

| # | 查询 | Intent | 状态 |
|---|------|--------|------|
| 1 | find wireless headphones under $50 | products_search | ✅ |
| 2 | search for bluetooth speakers | products_search | ✅ |
| 3 | 查找蓝牙耳机 价格低于200 | products_search | ✅ |
| 4 | search for bluetooth speakers with 4+ stars | products_search | ✅ |
| 5 | top 10 products in electronics sort by revenue | products_search | ✅ |
| 6 | analyze market for headphones | markets_search | ✅ |
| 7 | market analysis for electronics category | markets_search | ✅ |
| 8 | 市场分析 耳机类目 | markets_search | ✅ |
| 9 | list all categories | categories | ✅ |
| 10 | 有哪些类目 | categories | ✅ |
| 11 | show me electronics subcategories | categories | ✅ |
| 12 | search by brand Sony | competitor_lookup | ✅ |
| 13 | find Sony products | products_search | ✅ |
| 14 | 竞品分析 brand Sony | competitor_lookup | ✅ |
| 15 | show me details for ASIN B08N5WRWNW | realtime_product | ✅ |
| 16 | 查看 B08N5WRWNW 详情 | realtime_product | ✅ |
| 17 | get realtime data for ASIN B08N5WRWNW | realtime_product | ✅ |

### 建议新增的测试用例

| # | 查询 | Intent | 优先级 |
|---|------|--------|--------|
| 18 | analyze reviews for B08N5WRWNW | review_analysis | 高 |
| 19 | 分析 B08N5WRWNW 的评价 | review_analysis | 高 |
| 20 | compare B08N5WRWNW and B07ZPKBL9V | product_comparison | 高 |
| 21 | 对比 B08N5WRWNW 和 B07ZPKBL9V | product_comparison | 高 |
| 22 | track price for B08N5WRWNW | price_monitoring | 中 |
| 23 | price history for B08N5WRWNW | price_history | 中 |
| 24 | find unauthorized sellers for my brand | seller_discovery | 中 |
| 25 | calculate profit for $30 product | profit_calculator | 低 |

---

## 五、总结

### 当前覆盖率
- **选品需求**: ~60% (市场分析、产品搜索已支持)
- **定价需求**: ~40% (价格范围查询已支持，利润率计算缺失)
- **竞品跟踪**: ~50% (品牌查询已支持，评价分析缺失)
- **产品分析**: ~50% (产品详情已支持，评价分析缺失)

### 建议优先级
1. **高优先级**: 评价分析 (review analysis) - 大量用户需求
2. **高优先级**: 产品对比 (product comparison) - 竞品分析核心
3. **中优先级**: 价格历史 (price history) - 定价策略支持
4. **中优先级**: 卖家发现 (seller discovery) - 品牌保护
5. **低优先级**: 利润率计算 (profit calculator) - 辅助功能
