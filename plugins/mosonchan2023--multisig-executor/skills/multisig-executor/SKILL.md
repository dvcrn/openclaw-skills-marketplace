---
name: multisig-executor
description: "Multi-signature transaction executor for DeFi and DAOs - create, sign, and execute multi-sig transactions. Each call charges 0.001 USDT via SkillPay."
homepage: https://github.com/moson/multisig-executor
---

# Multisig Executor

## 功能

Multi-signature transaction executor for DeFi and DAOs - create, sign, and execute multi-sig transactions.

### 核心功能

- **Transaction Creation**: Create multi-sig transaction proposals
- **Signature Collection**: Collect signatures from required signers
- **Transaction Execution**: Execute after threshold is met
- **Transaction History**: View past multisig transactions
- **Pending Transactions**: View awaiting transactions
- **Signer Management**: Add/remove signers

## 使用方法

```json
{
  "action": "create",
  "to": "0x...",
  "value": "1.0",
  "data": "0x...",
  "signers": ["0xA...", "0xB...", "0xC..."],
  "threshold": 2
}
```

## 输出示例

```json
{
  "success": true,
  "txHash": "0x...",
  "transactionId": "tx_123",
  "signers": ["0xA...", "0xB...", "0xC..."],
  "signatures": ["0x...", "0x..."],
  "status": "executed"
}
```

## 价格

每次调用: 0.001 USDT

## 常见问题

**Q: 支持哪些钱包？**
A: MetaMask, Ledger, Trezor 等主流钱包。

**Q: 需要多少签名？**
A: 取决于阈值设置，通常是 2/3 或自定义。

**Q: 支持哪些链？**
A: Ethereum, Polygon, Arbitrum, Optimism 等 EVM 链。
