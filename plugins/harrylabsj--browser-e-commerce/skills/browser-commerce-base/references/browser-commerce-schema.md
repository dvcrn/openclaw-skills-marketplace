# Browser Commerce Schema

Use this schema when extracting shopping/comparison results from browser pages.

## Candidate item

```json
{
  "platform": "taobao",
  "page_type": "search_result",
  "title": "商品标题",
  "price_current": "199",
  "price_final": "179",
  "currency": "CNY",
  "store": "旗舰店名称",
  "seller_type": "flagship | self-operated | third-party | regular",
  "sales_hint": "已售 5000+",
  "rating_hint": "4.8",
  "coupon_hint": "满199减20",
  "shipping_hint": "48小时发货 / 次日达 / 免配送费",
  "location_hint": "北京可送",
  "sku_hint": ["黑色", "256G"],
  "risk_notes": ["第三方店铺", "价格异常低需复核"],
  "url": "https://...",
  "evidence": {
    "screenshot": "/tmp/...png"
  }
}
```

## Summary output

Use this section order when replying:

1. 结论
2. 候选项对比
3. 推荐项
4. 风险提醒
5. 证据截图 / 链接

## Page types

- `search_result`
- `product_detail`
- `cart`
- `order`
- `coupon`
- `store`
- `delivery_check`

## Seller type mapping

- Taobao/Tmall: `flagship | authorized | crown | diamond | regular`
- JD: `self-operated | flagship | authorized | third-party`
- PDD: `brand | flagship | specialty | regular`
- Meituan/Eleme/Dianping: `official | chain | local | unknown`
