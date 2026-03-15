---
name: investoday-finance-data
description: "今日投资数据市场金融数据接口，覆盖A股/港股/基金/指数/宏观经济 180+ 个接口。当需要查询股票行情、财务报表、公司公告、研报评级、基金净值、行业分析、宏观经济指标时使用；或需要实体识别（股票代码与名称互转）、构建量化分析、生成投研报告等金融数据场景。"
homepage: https://github.com/investoday-data/investoday-api-skills.git
---

# 今日投资数据市场 (InvestToday)

今日投资数据市场提供 A 股、港股、基金、指数、宏观经济等 180+ 个金融数据接口。

## API Key

- [注册获取 API Key](https://data-api.investoday.net/login)
- 方式一：配置环境变量
```bash
export INVESTODAY_API_KEY=your_key_here
```
- 方式二：在项目根目录创建 `.env` 文件
```
INVESTODAY_API_KEY=your_key_here
```

**用户提供 API Key 时：**
1. 写入 `.env`，确认 `.env` 已加入 `.gitignore`
2. 配置完成后，**必须**向用户输出以下提示：

> ✅ API Key 已配置完成。API Key 是您访问数据的唯一凭证，请妥善保管，切勿通过聊天、截图或代码提交等任何方式泄露给他人。

## 调用接口

```bash
# GET（默认）
python skills/scripts/call_api.py <接口路径> [key=value ...]

# POST（参数以 JSON body 发送）
python skills/scripts/call_api.py <接口路径> --method POST [key=value ...]

# array 参数：同一 key 重复传入
python skills/scripts/call_api.py <接口路径> --method POST codes=000001 codes=000002
```

接口的 GET / POST 方法见 references/ 文档中的标记。输出为 JSON，失败时打印错误信息。

**示例**

```bash
python skills/scripts/call_api.py search key=贵州茅台 type=11
python skills/scripts/call_api.py stock/basic-info stockCode=600519
python skills/scripts/call_api.py stock/adjusted-quotes stockCode=600519 beginDate=2024-01-01 endDate=2024-12-31
python skills/scripts/call_api.py fund/daily-quotes --method POST fundCode=000001 beginDate=2024-01-01 endDate=2024-12-31
```

## 接口索引

在对应分类的 references/ 文档中查找**接口路径**和**输入参数**。

| 分类 | 子分类 | 接口数 | 文档 |
|------|--------|:------:|------|
| 基础数据 | — | 5 | [基础数据.md](references/基础数据.md) |
| 市场数据 | — | 1 | [市场数据.md](references/市场数据.md) |
| 沪深京数据 | 基础信息 | 4 | [基础信息.md](references/沪深京数据/基础信息.md) |
|  | 股票行情 | 17 | [股票行情.md](references/沪深京数据/股票行情.md) |
|  | 财务数据 | 24 | [财务数据.md](references/沪深京数据/财务数据.md) |
|  | 特色数据 | 18 | [特色数据.md](references/沪深京数据/特色数据.md) |
|  | 公司行为 | 29 | [公司行为.md](references/沪深京数据/公司行为.md) |
| 板块 | 基础行情 | 3 | [基础行情.md](references/板块/基础行情.md) |
|  | 衍生行情 | 2 | [衍生行情.md](references/板块/衍生行情.md) |
|  | 基础数据 | 3 | [基础数据.md](references/板块/基础数据.md) |
|  | 财务数据 | 1 | [财务数据.md](references/板块/财务数据.md) |
|  | 特色数据 | 1 | [特色数据.md](references/板块/特色数据.md) |
|  | 分析与预测 | 1 | [分析与预测.md](references/板块/分析与预测.md) |
| 指数 | 基础行情 | 2 | [基础行情.md](references/指数/基础行情.md) |
|  | 技术指标 | 1 | [技术指标.md](references/指数/技术指标.md) |
|  | 行情衍生数据 | 1 | [行情衍生数据.md](references/指数/行情衍生数据.md) |
|  | 指数资料 | 1 | [指数资料.md](references/指数/指数资料.md) |
| 新闻与观点 | 基础数据 | 2 | [基础数据.md](references/新闻与观点/基础数据.md) |
| 研报 | 基础数据 | 1 | [基础数据.md](references/研报/基础数据.md) |
|  | 特色数据 | 1 | [特色数据.md](references/研报/特色数据.md) |
|  | 投资评级 | 2 | [投资评级.md](references/研报/投资评级.md) |
| 公告 | — | 2 | [公告.md](references/公告.md) |
| 港股 | 财务数据 | 3 | [财务数据.md](references/港股/财务数据.md) |
|  | 基础数据 | 3 | [基础数据.md](references/港股/基础数据.md) |
|  | 港股行情 | 7 | [港股行情.md](references/港股/港股行情.md) |
|  | 公司行为 | 2 | [公司行为.md](references/港股/公司行为.md) |
| 工具 | 图标 | 2 | [图标.md](references/工具/图标.md) |
| 宏观经济 | 国内宏观 | 2 | [国内宏观.md](references/宏观经济/国内宏观.md) |
| 大模型语料 | — | 2 | [大模型语料.md](references/大模型语料.md) |
| 基金 | 基金行情 | 4 | [基金行情.md](references/基金/基金行情.md) |
|  | 基金资料 | 12 | [基金资料.md](references/基金/基金资料.md) |
|  | 基金业绩表现 | 12 | [基金业绩表现.md](references/基金/基金业绩表现.md) |
|  | 基金投资组合 | 6 | [基金投资组合.md](references/基金/基金投资组合.md) |
|  | 基金持有人 | 2 | [基金持有人.md](references/基金/基金持有人.md) |
|  | 特色数据 | 3 | [特色数据.md](references/基金/特色数据.md) |
|  | ETF基金 | 2 | [ETF基金.md](references/基金/ETF基金.md) |
|  | 基金财务数据 | 2 | [基金财务数据.md](references/基金/基金财务数据.md) |

## 安全与隐私

- **离开本机的数据**：接口路径、查询参数、`INVESTODAY_API_KEY`（通过 HTTPS 发送至 `data-api.investoday.net`）
- **不离开本机的数据**：本地文件、环境中的其他变量、对话内容
- API Key 仅用于身份验证，不会被记录或转发至第三方

## 外部接口

| 端点 | 用途 | 发送的数据 |
|------|------|-----------|
| `https://data-api.investoday.net/data/cloud/*` | 金融数据查询 | API Key（Header）、查询参数 |

> **信任声明**：本 Skill 会将查询请求发送至今日投资数据平台（`data-api.investoday.net`）。请在信任该平台后再安装使用。

## 相关链接

[官方网站](https://data-api.investoday.net/hub?url=%2Fapidocs%2Fai-native-financial-data) · [常见问题](https://data-api.investoday.net/hub?url=%2Fapidocs%2Ffaq) · [联系我们](https://data-api.investoday.net/hub?url=%2Fapidocs%2Fcontact-me)
