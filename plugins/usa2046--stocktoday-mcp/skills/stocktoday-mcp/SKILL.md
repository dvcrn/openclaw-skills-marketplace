---
name: stocktoday-mcp
description: "Stocktoday Mcp"
---

# StockToday MCP

股票数据 MCP 服务器，提供 155+ Tushare API 接口。

## 功能

- 股票基础数据（代码、财务、股东等）
- 实时行情数据
- 财务数据（资产负债表、利润表、现金流）
- 资金流向
- 指数数据
- 基金/期货/期权数据
- 特色数据（龙虎榜、融资融券等）

## 配置

### 环境变量

```bash
# 设置 token
export STOCKTODAY_TOKEN="your_token"
```

### 参数调用

每个 API 调用可传入 `token` 参数：

```json
{
  "token": "your_token",
  "api_name": "stock_basic",
  "params": {"list_status": "L"}
}
```

## 后端

使用自定义后端服务: `https://tushare.citydata.club/`

不需要 Tushare 官方 Token。

---

*Published via ClawHub*
