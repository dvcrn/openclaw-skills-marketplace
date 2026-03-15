# Recommendation Logic Design

## Overview

The recommendation system follows a simple two-step mapping:
1. **Product → Category**: Match input product to predefined categories
2. **Category → Websites**: Recommend appropriate shopping platforms for each category

## Category Classification

### Primary Categories

| Category ID | Category Name (EN) | Category Name (ZH) | Example Products |
|-------------|-------------------|-------------------|------------------|
| electronics | Electronics | 电子产品 | 手机, 笔记本电脑, 平板, 相机, 耳机 |
| clothing | Clothing & Apparel | 服装服饰 | 衣服, 鞋子, 裙子, 外套, 裤子 |
| groceries | Groceries & Food | 食品杂货 | 零食, 大米, 食用油, 生鲜, 饮料 |
| home | Home & Kitchen | 家居厨具 | 家具, 厨具, 床上用品, 家电 |
| beauty | Beauty & Cosmetics | 美妆护肤 | 化妆品, 护肤品, 香水, 面膜 |
| books | Books & Stationery | 图书文具 | 书籍, 文具, 办公用品 |
| sports | Sports & Outdoors | 运动户外 | 运动鞋, 健身器材, 帐篷, 自行车 |
| baby | Baby & Kids | 母婴儿童 | 奶粉, 尿布, 玩具, 童装 |
| automotive | Automotive | 汽车用品 | 汽车配件, 机油, 车饰 |
| digital | Digital & Games | 数码游戏 | 游戏机, 游戏, 手机配件 |

## Product-to-Category Mapping

### Approach 1: Keyword Matching (v1.0.0)
- Maintain a dictionary of product keywords mapped to categories
- Simple substring matching
- Chinese keywords with synonyms support

**Example mapping**:
```json
{
  "手机": "electronics",
  "智能手机": "electronics",
  "iphone": "electronics",
  "笔记本电脑": "electronics",
  "电脑": "electronics",
  "衣服": "clothing",
  "服装": "clothing",
  "上衣": "clothing",
  "裤子": "clothing",
  "鞋子": "clothing"
}
```

### Approach 2: NLP Matching (Future)
- Use word embeddings for semantic similarity
- Handle misspellings and variations
- Support for descriptive queries ("适合跑步的运动鞋")

## Category-to-Website Recommendations

### Recommendation Criteria
1. **Platform Specialization**: Some platforms excel in specific categories
2. **Price Range**: Different platforms cater to different price segments
3. **Authenticity Guarantee**: Important for electronics and cosmetics
4. **Logistics Speed**: Especially important for groceries and perishables
5. **After-sales Service**: Critical for electronics and appliances

### Website Database

| Website | Chinese Name | Strengths | Best For |
|---------|-------------|-----------|----------|
| jd.com | 京东 | Fast logistics, authentic goods, good service | Electronics, Home appliances, Groceries |
| tmall.com | 天猫 | Brand official stores, wide selection | Clothing, Beauty, Electronics |
| taobao.com | 淘宝 | Low prices, vast variety, C2C market | Clothing, Accessories, Unique items |
| suning.com | 苏宁易购 | Electronics & appliances specialist | Electronics, Home appliances |
| vip.com | 唯品会 | Discounted branded clothing | Clothing, Shoes, Bags |
| dangdang.com | 当当网 | Books & media specialist | Books, E-books, Stationery |
| yhd.com | 1号店 | Groceries & daily necessities | Groceries, Food, Household |
| jd.id | 京东全球购 | Imported goods, cross-border | Imported cosmetics,母婴用品 |
| kaola.com | 网易考拉 | Imported goods, authentic | Imported cosmetics,母婴用品 |
| little red book | 小红书 | Social commerce, reviews | Beauty, Fashion, Lifestyle |
| pinduoduo.com | 拼多多 | Group buying, low prices | Daily necessities, Groceries |

### Category-Specific Recommendations

#### Electronics (电子产品)
1. **京东 (JD.com)** - Best for authentic electronics with fast delivery
2. **天猫 (Tmall.com)** - Brand official stores
3. **苏宁易购 (Suning.com)** - Electronics specialist
4. **小米商城 (Mi.com)** - For Xiaomi ecosystem products

#### Clothing (服装服饰)
1. **淘宝 (Taobao.com)** - Largest variety, affordable
2. **天猫 (Tmall.com)** - Brand clothing, better quality
3. **唯品会 (Vip.com)** - Discounted branded clothing
4. **京东 (JD.com)** - For basics and fast delivery

#### Groceries (食品杂货)
1. **京东到家 (JD Daojia)** - Fast grocery delivery
2. **天猫超市 (Tmall Supermarket)** - Wide selection
3. **1号店 (YHD.com)** - Grocery specialist
4. **每日优鲜 (MissFresh)** - Fresh produce

#### Beauty & Cosmetics (美妆护肤)
1. **天猫国际 (Tmall Global)** - Imported cosmetics
2. **京东美妆 (JD Beauty)** - Authentic products
3. **小红书 (Little Red Book)** - Reviews and community
4. **网易考拉 (Kaola.com)** - Imported goods

## Scoring Algorithm (Simple Version)

For v1.0.0, we use fixed rankings per category. Future versions could implement:

1. **Base Score**: Platform's inherent strength in category (0-10)
2. **User Preference**: Optional user preferences (price sensitivity, delivery speed)
3. **Seasonal Factors**: Special promotions, seasonal relevance
4. **Real-time Data**: Stock availability, delivery estimates

## Fallback Strategy

1. If product not found in any category:
   - Use general recommendations (京东, 天猫, 淘宝)
   - Suggest user try broader category search
   
2. If category has no specific recommendations:
   - Fall back to general e-commerce platforms
   - Provide disclaimer about limited data

## Data Structure

```json
{
  "categories": {
    "electronics": {
      "name": "电子产品",
      "websites": [
        {"id": "jd", "name": "京东", "reason": "正品保障，物流快", "rank": 1},
        {"id": "tmall", "name": "天猫", "reason": "品牌官方旗舰店", "rank": 2}
      ],
      "tips": "购买电子产品建议选择官方旗舰店或自营平台"
    }
  },
  "product_mapping": {
    "手机": "electronics",
    "笔记本电脑": "electronics"
  }
}
```

## Future Enhancements

1. **Personalization**: Learn user preferences over time
2. **Price Comparison**: Integrate with price tracking APIs
3. **Review Integration**: Show average ratings for products
4. **Regional Recommendations**: Consider user location for logistics
5. **Real-time Promotions**: Show current discounts and coupons