---
name: mx-macrodata
description: "MX Macro Data"
---

﻿---
name: MX_MacroData
description: 通过自然语言查询宏观经济数据，结果转为 CSV 并生成描述文件。支持查询 GDP、CPI、货币供应量等宏观指标。需要配置EM_API_KEY环境变量。
metadata:
  {
    "openclaw": {
      "requires": {
        "env": ["EM_API_KEY"],
        "bins": ["python3", "pip3"]
      },
      "install": [
        {
          "id": "pip-deps",
          "kind": "python",
          "package": "httpx pandas",
          "label": "Install Python dependencies"
        }
      ]
    }
  }
---

# 宏观经济数据查询 (MX_MacroData)

通过**文本输入**查询宏观经济数据，接口返回 JSON 后会自动转换为 **CSV** 并生成对应的**内容描述 txt** 文件。

## ⚠️ 核心输入约束 (Critical Input Constraints)

- **时间维度**：支持相对时间表述（如“今年”、“过去三年”、“上月”）。
- **地域维度**：支持宏观地区表述（如“中国”、“美国”、“欧元区”、“华东地区”、“中国各省”），无需拆解为具体省市列表。

### 1. 禁止模糊商品类别 (No Ambiguous Commodities)
- **禁止输入**：大类统称（如“稀土金属”、“有色金属”、“农产品”、“能源”、“科技股”）。
- **要求**：必须解包为具体的**交易品种名称或代码**。
  - ❌ 错误：`"查询稀土价格走势"`
  - ✅ 正确：`"查询氧化镨钕、氧化镝、氧化铽的价格走势"`

### 2. 禁止宏观泛指指标 (No Macro Generalizations without Metrics)
- **禁止输入**：宽泛的经济概念而无具体指标（如“中国经济”、“美国制造业状况”、“全球通胀情况”）。
- **要求**：必须指定具体的**指标名称**（如 GDP、CPI、PMI、失业率、工业增加值等）。
  - ❌ 错误：`"查询中国经济数据"`
  - ✅ 正确：`"查询中国 GDP 同比增速、中国 CPI 同比"`
  - ✅ 正确：`"查询美国制造业 PMI"` (地域允许宏观，但指标必须具体)

### 3. 时间与地域的灵活性 (Flexible Time & Region)
- **时间**：无需绝对日期。
  - ✅ 允许：`"查询中国过去五年的M2增速"`、`"查询上个月美国的非农数据"`、`"查询黄金今日价格"`。
  - ✅ 允许（缺省）：`"查询德国失业率"`。
- **地域**：无需拆解为子集列表。
  - ✅ 允许：`"查询华东地区GDP"`,`"查询中国各省GDP"`。
  - ⚠️ 注意：若涉及“主要新兴市场”、“Top 5 国家”等动态排名指代，仍建议上层模型解包为具体国家列表（如 `"查询中国、印度、巴西的M2"`），以确保数据源一致性。
---

## 功能范围

### 基础查询能力
- **经济指标**：GDP、CPI、PPI、PMI、失业率、工业增加值等（支持指定国家/地区及具体指标名）。
- **货币金融**：M1/M2 货币供应量、社融规模、国债利率、汇率（支持指定币种对）。
- **商品价格**：黄金、白银、原油、铜、特定稀土氧化物等（**必须**指定具体品种）。
- **时间频率**：自动识别相对时间（年、季、月、周、日）并匹配对应频率数据；若未指定，返回最新数据。

### 查询示例对照表

| 类型     | ❌ 禁止的模糊查询 (指标/品种不明)      | ✅ 允许的明确查询 (时间/地区可灵活)             |
|----------|--------------------------------------|------------------------------------------------|
| 国内经济 | 查询华东地区GDP                        | 查询华东地区 GDP                              |
| 货币供应 | 查询主要新兴市场货币供应                | 查询中国、印度、巴西的 M2 货币供应量             |
| 商品价格 | 查询稀土和有色金属价格                 | 查询氧化镨钕、铜、铝的现货价格走势                |
| 全球宏观 | 查询 Top 3 经济体非农数据              | 查询美国、中国、德国的非农就业数据                |
| 时间灵活 | (无)                                  | 查询美国过去十年的失业率趋势                    |
| 默认时间 | (无)                                  | 查询日本最新的核心 CPI 数据                     |

## 错误处理机制

若接收到违反上述约束的输入，工具将直接返回错误信息，**不执行任何数据检索**，并提示用户或上层模型进行修正：
- `Error: Ambiguous Region Detected. Please provide specific city/country names instead of "[Input]".`
- `Error: Ambiguous Commodity Category. Please specify exact commodity names instead of "[Input]".`
- `Error: Relative Time/Ranking Detected. Please resolve to specific dates or entity lists before calling.`
- 

## 前提条件

### 1. 注册东方财富账号

访问 https://ai.eastmoney.com/mxClaw 注册账号并获取API_KEY。

### 2. 配置 Token

```bash
# 添加到 ~/.zshrc
export EM_API_KEY="your_api_key_here"
```

然后执行：

```bash
source ~/.zshrc
```

### 3. 安装依赖


```bash
pip3 install httpx pandas pypinyin --user
```

## 快速开始

### 1. 命令行调用

在项目根目录或配置的工作目录下执行：

```bash
python3 -m scripts.get_data --query 中国GDP
```
**参数说明：**

| 参数            | 说明             | 必填 |
| --------------- | ---------------- | ---- |
| `--query`       | 自然语言查询条件 | ✅    |
```
### 2. 代码调用

​```python
import asyncio
from pathlib import Path
from scripts.get_data import query_macro_data

async def main():
    result = await query_macro_data(
        query="中国近五年GDP",
        output_dir=Path("workspace/MX_MacroData"),
    )
    if "error" in result:
        print(result["error"])
    else:
        print(f"CSV: {r['csv_paths']}")
        print(f"描述: {r['description_path']}")
        print(f"行数: {r['row_counts']}")

asyncio.run(main())
```

输出示例：
```
CSV: /path/to/workspace/MX_MacroData/MX_MacroData_中国GDP_年.csv
CSV: /path/to/workspace/MX_MacroData/MX_MacroData_中国GDP_季.csv
CSV: /path/to/workspace/MX_MacroData/MX_MacroData_中国GDP_月.csv
描述:/path/to/workspace/MX_MacroData/MX_MacroData_中国GDP_description.txt
行数: 年: 10行, 季: 20行, 月: 40行
```

## 输出文件说明

| 文件 | 说明 |
|------|------|
| `MX_MacroData_<查询摘要>_<频率>.csv` | 按频率分组的宏观数据表，UTF-8 编码，可直接用 Excel 或 pandas 打开。 |
| `MX_MacroData_<查询摘要>_description.txt` | 说明文件，含各频率数据统计、数据来源和单位等信息。 |

## 环境变量

| 变量                      | 说明                                  | 默认                     |
| ------------------------- | ------------------------------------- | ------------------------ |
| `MX_MacroData_OUTPUT_DIR` | CSV 与描述文件的输出目录（可选）      | `workspace/MX_MacroData` |
| `EM_API_KEY`              | 东方财富宏观查数工具 API 密钥（必备） | 无                       |

## 常见问题

**错误：请设置 EM_API_KEY 环境变量**

1. 请访问 https://ai.eastmoney.com/mxClaw 获取`API_KEY`。
2. 配置`EM_API_KEY`环境变量


**如何指定输出目录？**

```bash
export MX_MacroData_OUTPUT_DIR="/path/to/output"
python3 scripts/get_data.py --query "查询内容" 
```