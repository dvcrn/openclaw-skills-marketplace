---
name: stock-quote-fetcher
description: "实时股票行情查询。每次调用自动扣费 0.001 USDT"
homepage: https://github.com/moson/stock-quote-fetcher
---

# Stock Quote Fetcher

实时股票行情查询工具。

## 功能

### 核心功能

- **实时报价**: 获取股票当前价格
- **涨跌幅**: 今日涨跌幅
- **成交量**: 交易量数据
- **市值**: 总市值信息

### 支持的市场

- 美国股市 (NASDAQ, NYSE)
- 港股
- A股

## 使用示例

```javascript
// 查询单只股票
await handler({ action: 'quote', symbol: 'AAPL' });

// 批量查询
await handler({ action: 'quotes', symbols: ['AAPL', 'GOOGL', 'MSFT'] });
```

## 价格

每次调用: 0.001 USDT
