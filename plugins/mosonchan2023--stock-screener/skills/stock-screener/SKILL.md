---
name: stock-screener
description: "股票筛选器。每次调用自动扣费 0.001 USDT"
homepage: https://github.com/moson/stock-screener
---

# Stock Screener

股票筛选器。

## 功能

### 筛选条件

- **市盈率 (PE)**: 低/高PE筛选
- **市净率 (PB)**: 价值股筛选
- **股息率**: 高股息筛选
- **成交量**: 活跃度筛选
- **市值**: 大盘/中小盘筛选

### 筛选条件组合

- 价值股筛选
- 成长股筛选
- 高股息筛选
- 活跃股筛选

## 使用示例

```javascript
// 筛选低PE股票
await handler({ action: 'screen', criteria: { pe: 'low' } });

// 筛选高股息
await handler({ action: 'screen', criteria: { dividend: 'high' } });
```

## 价格

每次调用: 0.001 USDT
