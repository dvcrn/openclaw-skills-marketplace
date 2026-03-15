# StockToday MCP

A-stock (A股) market data MCP server - 基于 Tushare API 封装。

## 功能 (Features)

### 行情数据
| Tool | 说明 | 参数 |
|------|------|------|
| `stock_daily` | 日线行情 | ts_code, start_date, end_date, trade_date |
| `stock_weekly` | 周线行情 | ts_code, start_date, end_date, trade_date |
| `stock_monthly` | 月线行情 | ts_code, start_date, end_date, trade_date |
| `stock_pro_bar` | 行情（复权） | ts_code, start_date, end_date, adj, freq |
| `stock_adj_factor` | 复权因子 | ts_code, start_date, end_date |
| `stock_daily_basic` | 每日指标 | ts_code, trade_date, fields |

### 基础数据
| Tool | 说明 | 参数 |
|------|------|------|
| `stock_basic` | 股票基本信息 | exchange, list_status, ts_code, market, fields |
| `stock_company` | 上市公司信息 | ts_code, exchange |
| `trade_cal` | 交易日历 | exchange, start_date, end_date |
| `stock_namechange` | 名称变更 | ts_code, start_date, end_date |
| `hs_const` | 沪深股通成分 | hs_type, is_new |
| `stk_managers` | 公司管理层 | ts_code |
| `stk_rewards` | 高管薪酬 | ts_code |

### 涨跌停
| Tool | 说明 | 参数 |
|------|------|------|
| `stock_stk_limit` | 涨跌停数据 | ts_code, trade_date |
| `stock_suspend` | 停复牌信息 | ts_code, trade_date, suspend_type |

### 财务数据
| Tool | 说明 | 参数 |
|------|------|------|
| `stock_income` | 利润表 | ts_code, start_date, end_date |
| `stock_balancesheet` | 资产负债表 | ts_code, start_date, end_date |
| `stock_cashflow` | 现金流量表 | ts_code, start_date, end_date |
| `stock_dividend` | 分红送股 | ts_code |
| `stock_fina_indicator` | 财务指标 | ts_code |

### 参考数据
| Tool | 说明 | 参数 |
|------|------|------|
| `stock_top10_holders` | 十大股东 | ts_code, start_date, end_date |
| `stock_top10_floatholders` | 十大流通股东 | ts_code, start_date, end_date |
| `stock_concept` | 概念列表 | - |
| `stock_concept_detail` | 概念详情 | id, ts_code |

### 资金流向
| Tool | 说明 | 参数 |
|------|------|------|
| `stock_moneyflow` | 资金流向 | ts_code, trade_date, start_date, end_date |

### 龙虎榜
| Tool | 说明 | 参数 |
|------|------|------|
| `stock_top_list` | 龙虎榜上榜 | trade_date |
| `stock_top_inst` | 龙虎榜机构 | trade_date |
| `stock_limit_list` | 涨停列表 | trade_date, limit_type |

### 两融数据
| Tool | 说明 | 参数 |
|------|------|------|
| `stock_margin` | 融资融券 | trade_date |
| `stock_margin_detail` | 融资融券明细 | trade_date |

### 特色数据
| Tool | 说明 | 参数 |
|------|------|------|
| `stock_stk_factor` | 股票因子 | ts_code, start_date, end_date, fields |

### 指数数据
| Tool | 说明 | 参数 |
|------|------|------|
| `index_basic` | 指数基本信息 | market |
| `index_daily` | 指数日线 | ts_code, start_date, end_date |
| `index_weekly` | 指数周线 | ts_code, start_date, end_date |
| `index_monthly` | 指数月线 | ts_code, start_date, end_date |
| `index_weight` | 指数成分 | index_code, start_date, end_date |
| `index_classify` | 指数分类 | level, src |

### 基金数据
| Tool | 说明 | 参数 |
|------|------|------|
| `fund_basic` | 基金基本信息 | market |
| `fund_company` | 基金公司 | - |
| `fund_manager` | 基金经理 | ts_code |
| `fund_nav` | 基金净值 | ts_code |
| `fund_daily` | 基金日线 | ts_code, start_date, end_date |

### 期货数据
| Tool | 说明 | 参数 |
|------|------|------|
| `fut_basic` | 期货基本信息 | exchange, fut_type |
| `fut_daily` | 期货日线 | ts_code, trade_date, start_date, end_date |

### 沪深股通
| Tool | 说明 | 参数 |
|------|------|------|
| `hsgt_top10` | 沪深股通前十成交 | trade_date, market_type |

## 安装

```bash
cd stocktoday-mcp
npm install
npm run build
```

## 配置 Token

支持两种方式：

### 方式1: TUSHARE_TOKEN
```bash
export TUSHARE_TOKEN="your_tushare_token"
```

### 方式2: 直接 Token
```bash
export STOCKTODAY_TOKEN="citydata"
```

## 使用示例

```
User: 查一下茅台今天的行情
→ stock_pro_bar { "ts_code": "600519.SH", "start_date": "20260313", "end_date": "20260313" }

User: 上证指数今天怎么样？
→ index_daily { "ts_code": "000001.SH", "trade_date": "20260313" }

User: 今天龙虎榜有哪些？
→ stock_top_list { "trade_date": "20260313" }

User: 茅台的财务数据
→ stock_income { "ts_code": "600519.SH" }

User: 现在两融情况
→ stock_margin { "trade_date": "20260313" }
```

## OpenClaw 配置

在 mcporter.json 添加:

```json
{
  "mcpServers": {
    "stocktoday": {
      "command": "node",
      "args": ["dist/index.js"],
      "env": {
        "TUSHARE_TOKEN": "your_token_here"
      }
    }
  }
}
```

## 发布

```bash
npx clawhub publish stocktoday-mcp
```

## License

MIT
