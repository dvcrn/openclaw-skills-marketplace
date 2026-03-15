---
name: whale-alerts
description: "巨鲸地址监控警报系统 - 追踪聪明钱地址，大额转账实时警报，DeFi 巨鲸动向分析。每次调用自动扣费 0.001 USDT"
---

# Whale Alerts - 巨鲸警报系统

## 功能

### 1. 巨鲸追踪
- 监控已知巨鲸地址
- 大额转账实时推送
- 多链支持 (ETH, BSC, Polygon, Arbitrum, Optimism)

### 2. 智能分析
- 巨鲸建仓/清仓信号
- 趋势判断
- 历史交易分析

### 3. 自定义警报
- 设置阈值 (>$10k, >$100k, >$1M)
- 涨跌提醒

## 使用示例

```javascript
// 追踪地址
{ action: "track", address: "0x1234..." }

// 查询巨鲸动向
{ action: "whales", token: "BTC" }

// 设置警报
{ action: "alert", address: "0x...", threshold: 10000 }
```

## 配置

设置环境变量添加监控地址。
