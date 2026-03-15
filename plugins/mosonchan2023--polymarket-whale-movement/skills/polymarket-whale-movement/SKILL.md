---
name: polymarket-whale-movement
description: "追踪 Polymarket 鲸鱼（大额交易者）活动，支持 Copy Trade 功能。每次调用自动扣费 0.001 USDT"
homepage: https://github.com/moson/polymarket-whale-movement
---

# Polymarket Whale Movement Tracker

## 功能

这个 Skill 提供以下核心功能：

### 1. 鲸鱼追踪 (Whale Tracking)
- 追踪已知的 Polymarket 大额交易者
- 实时监控鲸鱼钱包活动
- 显示交易量、平均仓位、胜率等统计信息

### 2. 交易信号 (Trading Signals)
- 获取鲸鱼最新交易信号
- 过滤大额交易（默认 $10,000+）
- 显示交易方向、价格、数量

### 3. Copy Trade (跟随交易)
- 自动跟随鲸鱼下单
- 支持 YES/NO 交易
- 可设置仓位大小

### 4. 市场搜索
- 搜索 Polymarket 市场
- 获取实时价格和流动性
- 查看订单簿深度

### 5. 自动收费
- 每次调用通过 SkillPay.me 自动收取 0.001 USDT

## 使用示例

```
# 获取鲸鱼列表
{ action: 'whales' }

# 获取所有鲸鱼最新活动
{ action: 'activity' }

# 获取特定鲸鱼交易
{ action: 'trades', wallet: '0x6a72D33ee2Fc03dF0889d6D4f2fD1c5f6Ea33ee' }

# 搜索市场
{ action: 'search', query: 'BTC 100k' }

# 市场详情
{ action: 'market', query: 'Will BTC reach $100k?' }

# Copy Trade 跟随买入
{ action: 'copy', market: 'Will BTC reach $100k by 2025?', side: 'YES', size: 100, price: 0.5 }
```

## 配置要求

在 OpenClaw 配置中添加以下环境变量：

```json
{
  "skills": {
    "entries": {
      "polymarket-whale-movement": {
        "enabled": true,
        "env": {
          "SKILLPAY_API_KEY": "你的 SkillPay API Key",
          "PRIVATE_KEY": "你的 Polymarket 私钥",
          "WHALE_WALLETS": "0x...,0x...",
          "MIN_TRADE_SIZE": 10000
        }
      }
    }
  }
}
```

## 技术细节

### Polymarket Data API
- 使用 `data-api.polymarket.com` 获取交易历史
- 使用 `clob.polymarket.com` 获取订单簿和执行交易
- 支持代理钱包 (Proxy Wallet) 交易

### 鲸鱼定义
- 交易量 $100,000+
- 平均仓位 $10,000+
- 胜率 55%+

### Copy Trade 策略
1. 监控鲸鱼钱包
2. 检测到大额交易时获取信号
3. 自动跟随下单（同方向、同比例）
4. 设置止盈止损（可选）

## 风险提示

- 交易有风险，资金自负
- 鲸鱼不总是正确的 - 复制交易需谨慎
- 私钥只本地使用，不上传到 ClawHub
- 使用前请先本地测试
- 建议设置止损，不要 FOMO 跟单
