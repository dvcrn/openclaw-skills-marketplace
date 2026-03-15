# Futu Trade Bot Skills 📈

## 🎯 概述

**English Version:**
A trading bot skill based on Futu OpenAPI that enables natural language trading. This skill encapsulates Futu's market quote and order execution APIs, allowing agents to perform real-time trading operations through simple commands or scripts. Perfect for implementing natural language trading strategies and automated workflows.

**中文版本:**
基于富途牛牛API接口的交易机器人技能，帮助用户用自然语言进行交易。本技能已将富途牛牛的行情报价、下单交易等功能做了完整封装，可供智能助手随时调用。建议通过命令行或脚本来实现自然语言的策略生成和交易执行。

---

## 功能特性 / Features
- 账户查询 / Account Query：`get_account_info()`
- 交易解锁 / Trade Unlock：`unlock_trade(password=None, password_md5=None)`
- 交易锁定 / Trade Lock：`lock_trade(password=None, password_md5=None)`
- 下单 / Order Submission：`submit_order(...)`
- 改单/撤单 / Order Modification/Cancellation：`modify_order(...)`、`cancel_order(...)`、`cancel_all_orders(...)`

## 当前行为说明
- `submit_order` 必须显式传入 `acc_id` 和 `trd_env`（`REAL` / `SIMULATE`）。
- 不再支持 `switch_account_env`。
- 不再有幂等去重校验。
- `get_account_info` 每次调用都会覆盖写入 `json/account_info.json`。
- `unlock_trade` / `lock_trade` 支持 MD5 密码：
  - 优先使用 `password_md5`
  - 若仅提供明文 `password`，会在运行时自动转 MD5 后调用富途接口

## 安装
```bash
pip install -r requirements.txt
```

推荐（开发环境）：
```bash
pip install -e .
```
安装后可直接 `import quote_service/trade_service/account_manager/config_manager`，
无需再手动设置 `PYTHONPATH` 或在脚本里写 `sys.path`。

## 配置
配置文件路径：`json/config.json`

最小模板：
```json
{
  "futu_api": {
    "host": "127.0.0.1",
    "port": 11111,
    "security_firm": "FUTUSECURITIES",
    "trade_password": "",
    "trade_password_md5": "",
    "default_env": "SIMULATE"
  }
}
```

说明：
- `trade_password_md5` 优先级高于 `trade_password`
- `json/config.json` 含敏感信息，已建议加入 `.gitignore`

## 示例
```python
from account_manager import get_account_info, unlock_trade, lock_trade
from trade_service import submit_order

print(get_account_info())
print(unlock_trade())  # 使用配置密码（支持MD5）

print(submit_order(
    code="HK.00700",
    side="BUY",
    qty=200,
    price=150,
    order_type="NORMAL",
    acc_id=6017237,
    trd_env="SIMULATE"
))

print(lock_trade())  # 用完建议锁回去
```

## 运行要求
- 本机已安装并运行 Futu OpenD
- OpenD 地址与 `json/config.json` 一致（默认 `127.0.0.1:11111`）
- 真实交易前先确认账户已解锁且参数正确

## 详细文档
- 交易模块：[docs/trade.md](/Users/chengling/Documents/Trade%20Bot%20Skills/docs/trade.md)
- 账户模块：[docs/account.md](/Users/chengling/Documents/Trade%20Bot%20Skills/docs/account.md)
- 配置模块：[docs/config.md](/Users/chengling/Documents/Trade%20Bot%20Skills/docs/config.md)

## 📜 License / 许可证

This project is licensed under the **MIT License**.

**MIT许可证要点：**
- ✅ 可以自由使用、修改、分发
- ✅ 可以用于商业项目
- ✅ **需要保留版权声明和许可证**
- ✅ **需要注明原作者**

完整许可证内容见 [LICENSE](LICENSE) 文件。

---

**Copyright © 2026 jeffersonling1217-png**
