# 🦞 龙虾哥全量同步引擎 (v3.0)

## 🆕 更新功能
1. **图片全量化**: 自动从 `data-a-dynamic-image` 提取所有高清原图，不再漏图。
2. **变体解构化**: 支持将 Amazon 的颜色、尺寸等变体自动映射到 Shopify 的 `Variants` 列表。
3. **库存实时同步**: 
   - 映射逻辑: `In Stock (Amazon)` -> `Inventory 999 (Shopify)`
   - 映射逻辑: `Out of Stock (Amazon)` -> `Inventory 0 (Shopify)`
4. **ASIN 自动 SKU**: 使用亚马逊的 ASIN 作为 Shopify 的 SKU，保证唯一性。

## 🛠️ 下一个环节
- **多渠道比价**: 正在开发中。
