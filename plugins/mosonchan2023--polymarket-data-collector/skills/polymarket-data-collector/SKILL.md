---
name: polymarket-data-collector
description: "收集和分析 Polymarket 历史数据，用于回测和策略研究。每次调用自动扣费 0.001 USDT"
homepage: https://github.com/moson/polymarket-data-collector
---

# Polymarket Data Collector

## 功能

- 历史价格收集
- 交易数据导出
- 成交量分析
- 回测支持

## 详细说明

专业的 Polymarket 历史数据收集工具，帮助交易者和研究人员获取完整的市场历史数据。

### 核心功能

1. **历史价格收集**: 获取任意市场的历史价格数据，支持多时间框架
2. **交易数据导出**: 导出交易历史为 CSV 或 JSON 格式
3. **成交量分析**: 分析市场流动性变化趋势
4. **回测支持**: 为量化策略提供历史数据支持

### 使用方法

```json
{
  "market": "Will BTC hit $150k?",
  "from": "2024-01-01",
  "to": "2024-12-31",
  "interval": "1h",
  "format": "json"
}
```

### 输出格式

支持 JSON 和 CSV 格式，包含:
- 时间戳
- 开盘价/最高价/最低价/收盘价
- 成交量
- 未平仓合约

### 注意事项

- 数据保留期限为 2 年
- 大批量请求建议分批进行
