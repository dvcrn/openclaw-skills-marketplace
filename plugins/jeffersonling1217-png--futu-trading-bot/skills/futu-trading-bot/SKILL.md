---
name: futu-trading-bot
description: "Use Futu Trade Bot Skills to run account, quote, and trade workflows with real HK market data."
---

# Futu Trade Bot Skills 📈

## 🎯 Overview / 概述

**English Version:**
A trading bot skill based on Futu OpenAPI that enables natural language trading. This skill encapsulates Futu's market quote and order execution APIs, allowing agents to perform real-time trading operations through simple commands or scripts. Perfect for implementing natural language trading strategies and automated workflows.

**中文版本:**
基于富途牛牛API接口的交易机器人技能，帮助用户用自然语言进行交易。本技能已将富途牛牛的行情报价、下单交易等功能做了完整封装，可供智能助手随时调用。建议通过命令行或脚本来实现自然语言的策略生成和交易执行。

---

## When to Use This Skill / 使用场景

Use this skill when the user asks for any of the following:
- account query / unlock / lock
- HK quote pull or quote subscription callback
- order submission / modification / cancellation

## Quick Start / 快速开始

**Prerequisites / 前提条件:**
- Ensure Futu OpenD is running and HK quote entitlement is available.
- 确保富途OpenD正在运行且拥有港股行情权限。

**Setup Steps / 安装步骤:**
1. Create virtual environment (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install package:
   ```bash
   pip install -e .
   ```

3. Configure credentials:
   ```bash
   cp json/config_example.json json/config.json
   # Edit json/config.json with your Futu credentials
   # 编辑json/config.json填写你的富途账户信息
   ```

## Module Map

- Account: `account_manager`
  - `get_account_info()`
  - `unlock_trade(password=None, password_md5=None)`
  - `lock_trade(password=None, password_md5=None)`
- Quote: `quote_service`
  - Stage 1: `get_stock_basicinfo`, `get_market_state`
  - Stage 2: `subscribe`, `unsubscribe`, `unsubscribe_all`, `query_subscription`, callbacks
  - Stage 3: `get_market_snapshot`, `get_cur_kline`, `request_history_kline`, `get_rt_ticker`
- Trade: `trade_service`
  - `submit_order`, `modify_order`, `cancel_order`, `cancel_all_orders`

## Standard Workflow

1. Call `get_account_info()` and select target account.
2. Pull quote/snapshot for the target symbol (default HK use case: `HK.00700`).
3. For real trading, call `unlock_trade(...)`.
4. Submit or manage orders with explicit `acc_id` and `trd_env`.
5. After real operation, call `lock_trade(...)`.

## Canonical Imports

```python
from account_manager import get_account_info, unlock_trade, lock_trade
from quote_service import (
    get_stock_basicinfo, get_market_state, get_market_snapshot,
    get_cur_kline, request_history_kline, get_rt_ticker,
    subscribe, unsubscribe, unsubscribe_all, query_subscription,
    set_quote_callback, set_orderbook_callback
)
from trade_service import submit_order, modify_order, cancel_order, cancel_all_orders
```

## Account Usage

```python
get_account_info()
unlock_trade()  # uses config password/md5
lock_trade()
```

## Quote Usage

```python
get_stock_basicinfo(market="HK", sec_type="STOCK", code_list=["HK.00700"])
get_market_state(["HK.00700"])
get_market_snapshot(["HK.00700"])
get_cur_kline(code="HK.00700", num=5, ktype="K_DAY", autype="QFQ")
request_history_kline(code="HK.00700", start="2026-02-20", end="2026-03-06")
get_rt_ticker(code="HK.00700", num=10)
```

### Quote Subscription Callback Example

```python
def on_quote(payload):
    print(payload)

set_quote_callback(on_quote)
subscribe(["HK.00700"], ["QUOTE"], is_first_push=True, subscribe_push=True)
query_subscription()
```

## Trade Usage

```python
submit_order(
    code="HK.00700",
    side="BUY",
    qty=200,
    acc_id=6017237,
    trd_env="SIMULATE",
    price=150,
    order_type="NORMAL",
)

modify_order(op="NORMAL", order_id="...", trd_env="SIMULATE", price=151, qty=200, acc_id=6017237)
cancel_order(order_id="...", trd_env="SIMULATE", acc_id=6017237)
cancel_all_orders(trd_env="SIMULATE", acc_id=6017237)
```

## Runtime Conventions
- Prefer `.venv/bin/python`.
- With editable install, direct imports work from any directory.
- If editable install is unavailable, fallback:
  - `PYTHONPATH=src python3 <script.py>`

## Config
- Config file: `json/config.json`
- Required:
  - `futu_api.host`
  - `futu_api.port`
  - `futu_api.security_firm`
- Password strategy:
  - `trade_password_md5` preferred
  - fallback to `trade_password` (auto-md5 in runtime)
- Account cache output:
  - `json/account_info.json`

## Error Handling

- Always check `success` first.
- Quote/trade functions return structured dictionaries with `message`.
- If OpenD connection fails, recheck OpenD status, host/port config, and entitlement.

## 📜 License

This skill is licensed under the **MIT License**.

**Key points:**
- ✅ Free to use, modify, and redistribute
- ✅ Can be used in commercial projects
- ✅ **Must retain copyright notice and license**
- ✅ **Must give attribution to the original author**

See [LICENSE](LICENSE) for full terms.

---

**Copyright © 2026 jeffersonling1217-png**
