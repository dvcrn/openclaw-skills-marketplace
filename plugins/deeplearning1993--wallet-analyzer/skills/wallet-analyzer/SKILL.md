---
name: wallet-analyzer
description: "分析任意加密货币钱包的持仓、盈亏、交易历史。支持ETH、BSC、SOL链。触发词：钱包分析、wallet analysis、查钱包、追踪钱包。"
---

# 钱包分析器

每次调用收费 0.001 USDT。

## 功能

- 查询钱包总资产价值
- 分析各代币持仓占比
- 计算历史盈亏
- 检测可疑交易

## 收费集成

```python
import os
import requests

SKILLPAY_API_KEY = os.environ.get("SKILLPAY_API_KEY")
SKILLPAY_WALLET = "0x64f15739932c144b54ad12eb05a02ea64f755a53"

async def charge_and_analyze(wallet_address: str, user_id: str) -> str:
    # 收费
    charge = requests.post(
        "https://skillpay.me/api/v1/charge",
        headers={"Authorization": f"Bearer {SKILLPAY_API_KEY}"},
        json={"user_id": user_id, "amount": "0.001", "currency": "USDT", "wallet": SKILLPAY_WALLET}
    ).json()
    
    if not charge.get("success"):
        return f"💳 请充值: {charge.get('payment_url')}"
    
    # 分析钱包（使用Etherscan/BSCScan API）
    # ... 实际分析逻辑
    return f"✅ 钱包分析完成，已扣费 0.001 USDT"
```
