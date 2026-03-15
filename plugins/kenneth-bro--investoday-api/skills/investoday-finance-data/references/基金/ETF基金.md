# 基金 / ETF基金

---

#### ETF申购赎回清单基本信息

接口：`list_etf_sub_red_lists`　**`POST`**

根据基金代码和日期范围（格式为yyyy-MM-dd HH:mm:ss）查询ETF基金的申购赎回清单基本信息，包括基金代码、名称、标的指数、发布及上一交易日日期、现金差额、最小申赎单位资产净值、基金份额净值、预估现金部分、现金替代比例上限、最小申赎单位、单位分红金额、IOPV收盘价以及申购赎回相关的各类状态和限额信息，适用于投资者进行ETF申赎操作前的详细规则查询和投资决策分析。

**输入参数**

| 参数名 | 必填 | 类型 | 说明 | 示例 |
|--------|:----:|------|------|------|
| `fundCode` | — | string | 基金代码【与fundCodes组成多选一参数，必须且只能传递其中一个】 | `000001` |
| `fundCodes` | — | array | 基金代码列表【与fundCode组成多选一参数，必须且只能传递其中一个】 | `['000001', '000006']` |
| `beginDate` | — | string | 开始日期（格式yyyy-MM-dd） | `2025-01-01` |
| `endDate` | — | string | 结束日期（格式yyyy-MM-dd） | `2025-01-01` |
| `pageNum` | — | integer | 页码。 最小值:1; | `1` |
| `pageSize` | — | integer | 页长。 最小值:1; 最大值:500; | `10` |

**接口示例**

```bash
# 可选参数: fundCode, fundCodes, beginDate, endDate, pageNum, pageSize
python skills/scripts/call_api.py fund/etf-sub-redemption-list --method POST
```

---

#### ETF申购赎回成份股信息

接口：`list_etf_constituent_stks`　**`POST`**

通过ETF基金代码和日期范围（格式为yyyy-MM-dd HH:mm:ss），查询ETF申购赎回清单中的成分股信息，包括成分股代码、名称、数量、现金替代标志及比例、申购赎回的现金替代溢价/折扣比例、固定及申购赎回替代金额、以及成分股市值占比等详细数据，适用于分析ETF持仓结构、现金替代机制和投资组合管理。

**输入参数**

| 参数名 | 必填 | 类型 | 说明 | 示例 |
|--------|:----:|------|------|------|
| `fundCode` | — | string | 基金代码【与fundCodes组成多选一参数，必须且只能传递其中一个】 | `000001` |
| `fundCodes` | — | array | 基金代码列表【与fundCode组成多选一参数，必须且只能传递其中一个】 | `['000001', '000006']` |
| `beginDate` | — | string | 开始日期（格式yyyy-MM-dd） | `2025-01-01` |
| `endDate` | — | string | 结束日期（格式yyyy-MM-dd） | `2025-01-01` |
| `pageNum` | — | integer | 页码。 最小值:1; | `1` |
| `pageSize` | — | integer | 页长。 最小值:1; 最大值:500; | `10` |

**接口示例**

```bash
# 可选参数: fundCode, fundCodes, beginDate, endDate, pageNum, pageSize
python skills/scripts/call_api.py fund/etf-constituent-stocks --method POST
```

---
