---
name: polymarket-proxy-trader
description: "专治 Polymarket proxy_wallet read balance 问题，同时支持 reading balance 和 execute trade。每次调用自动扣费 0.001 USDT（SkillPay 集成）"
homepage: https://github.com/moson/polymarket-proxy-trader
---

# Polymarket Proxy Wallet Trader + Balance Fix

## 功能

这个 Skill 专治 Polymarket proxy_wallet read balance 问题，同时支持：

1. **Reading Balance** - 正确读取 Polymarket proxy wallet 余额（修复官方 SDK 的 proxy wallet bug）
2. **Execute Trade** - 执行买卖订单（支持 limit 和 market order）
3. **自动收费** - 每次调用通过 SkillPay.me 自动收取 0.001 USDT

## 使用示例

```
- "查询我的 Polymarket proxy 余额"
- "用 proxy wallet 在 Polymarket 下单买 YES 100 USDC"
- "执行 Polymarket trade market buy CONDITION 50 USDC"
- "check polymarket balance"
- "execute trade on polymarket"
```

## 技术细节

### Proxy Wallet Balance Bug 修复

官方 `py-clob-client` 和 `@polymarket/clob-client` 在使用 `signature_type=2` (Gnosis Safe/proxy wallet) 时存在已知 bug：
- ** Buying 正常**：USDC 从 proxy wallet 正确扣除
- ** Selling 失败**：API 检查的是 signing wallet (EOA) 的 conditional token 余额，而不是 proxy wallet

本 Skill 修复方法：
- 强制使用 `funder` 参数指定 proxy wallet 地址
- 使用正确的 `asset_type` 查询

### SkillPay 集成

```javascript
// 3 行代码集成 SkillPay
const chargeResult = await skillpay.charge({
  apiKey: SKILLPAY_API_KEY,
  userId: userId,
  amount: 0.001,
  skillSlug: 'polymarket-proxy-trader'
});
```

## 配置要求

在 OpenClaw 配置中添加以下环境变量：

```json
{
  "skills": {
    "entries": {
      "polymarket-proxy-trader": {
        "enabled": true,
        "env": {
          "SKILLPAY_API_KEY": "你的 SkillPay API Key",
          "PRIVATE_KEY": "你的 Polymarket 私钥",
          "PROXY_ADDRESS": "你的 Proxy Wallet 地址（可选）"
        }
      }
    }
  }
}
```

## 风险提示

- 交易有风险，资金自负
- 私钥只本地使用，不上传到 ClawHub
- 使用前请先本地测试
