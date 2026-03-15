---
name: pywencai
description: "Tonghuashun WenCai natural language data query tool — query A-share, index, fund, HK/US stock, convertible bond, and other market data using Chinese natural language."
homepage: https://github.com/zsrl/pywencai
---

# PyWenCai (Tonghuashun WenCai Data Query)

Query A-share and other market data from [Tonghuashun WenCai](https://www.iwencai.com/) using Chinese natural language via Python.

> ⚠️ **Cookie Required**: You must provide a valid cookie from the WenCai website. See how to obtain a cookie below.

## Requirements

- **Python 3.7+**
- **Node.js v16+** (pywencai internally executes JS code)
- **pip** package manager

## Installation

```bash
pip install pywencai --upgrade
```

## How to Obtain a Cookie

1. Open https://www.iwencai.com/ in your browser and log in.
2. Press F12 to open Developer Tools → switch to the Network tab.
3. Perform any query on the WenCai page.
4. Find a request to `iwencai.com` and copy the `Cookie` value from the request headers.
5. Use that string as the `cookie` parameter.

## Basic Usage

```python
import pywencai

# Query the top 10 stocks by today's gain; a valid cookie is required
res = pywencai.get(query='今日涨幅前10', cookie='your_cookie_here')
print(res)
```

## API Reference: `pywencai.get(**kwargs)`

### Required Parameters

- **query** — Chinese natural language query string, e.g. `'今日涨停股票'`, `'市盈率小于20的股票'`
- **cookie** — Cookie string obtained from the WenCai website (required)


### Optional Parameters

- **sort_key** — Sort field name, e.g. `'退市@退市日期'`
- **sort_order** — Sort direction: `'asc'` (ascending) or `'desc'` (descending)
- **page** — Page number (default: `1`)
- **perpage** — Results per page (default and max: `100`)
- **loop** — Set to `True` to fetch all pages; or set to an integer `n` to fetch the first `n` pages
- **query_type** — Query category (default: `'stock'`), possible values:
  - `stock` — A-share stocks
  - `zhishu` — Indices
  - `fund` — Funds
  - `hkstock` — Hong Kong stocks
  - `usstock` — US stocks
  - `threeboard` — New Third Board (NEEQ)
  - `conbond` — Convertible bonds
  - `insurance` — Insurance
  - `futures` — Futures
  - `lccp` — Wealth management products
- **retry** — Number of retries on failure (default: `10`)
- **sleep** — Delay in seconds between paginated requests (default: `0`)
- **log** — Set to `True` to print logs to the console
- **pro** — Set to `True` to use the paid version (requires a corresponding cookie)
- **no_detail** — Set to `True` to always return a `DataFrame` or `None` (never returns a dict)
- **find** — List of stock codes to prioritize, e.g. `['600519', '000010']`
- **request_params** — Extra parameters passed to `requests`, e.g. `{'proxies': proxies}`

### Return Values

- **List-type queries** → returns a `pandas.DataFrame`
- **Detail-type queries** → returns a `dict` (may contain text and DataFrames)


## Usage Examples

### Query Stocks with P/E Ratio Below 20

```python
import pywencai

# Use natural language to query low P/E ratio stocks
res = pywencai.get(query='市盈率小于20的股票', cookie='xxx')
print(res)
```

### Get Delisted Stocks Sorted by Date

```python
import pywencai

# Query delisted stocks, sorted by delisting date in ascending order
res = pywencai.get(
    query='退市股票',
    sort_key='退市@退市日期',  # Specify the sort field
    sort_order='asc',          # Ascending order
    cookie='xxx'
)
print(res)
```

### Paginate Through All Data with a Proxy

```python
import pywencai

# Configure HTTP proxy
proxies = {'http': 'http://proxy:8080', 'https': 'http://proxy:8080'}

# loop=True auto-paginates to fetch all data; log=True prints request logs
res = pywencai.get(
    query='昨日涨幅',
    sort_order='asc',          # Ascending order
    loop=True,                 # Fetch all pages automatically
    log=True,                  # Print log messages
    cookie='xxx',
    request_params={'proxies': proxies}  # Pass proxy configuration
)
print(res)
```

### Query Index Data

```python
import pywencai

# Set query_type='zhishu' to query index data
res = pywencai.get(
    query='上证指数近5日涨跌幅',
    query_type='zhishu',       # Set query type to index
    cookie='xxx'
)
print(res)
```

### Query Convertible Bond Data

```python
import pywencai

# Set query_type='conbond' to query convertible bond data
res = pywencai.get(
    query='可转债溢价率小于10%',
    query_type='conbond',      # Set query type to convertible bond
    cookie='xxx'
)
print(res)
```


## Tips

- **Use sparingly** — High-frequency calls may get you blocked by the WenCai server.
- Always use the **latest version**: `pip install pywencai --upgrade`
- Query strings use **Chinese natural language** — write queries as you would search on the WenCai website.
- When `loop=True` and `find` is set, `loop` is ignored and only the first 100 results are returned.
- For paid data, set `pro=True` and provide a valid `cookie`.

---

## Advanced Examples

### Query Limit-Up Stock Details

```python
import pywencai

# Query stocks that hit the daily limit up today, get detailed info
res = pywencai.get(
    query='今日涨停的股票',
    cookie='xxx'
)
# Returns a DataFrame with: stock code, name, limit-up time, bid amount, etc.
print(res)
```

### Query Consecutive Limit-Up Stocks

```python
import pywencai

# Query stocks with more than 2 consecutive limit-up days
res = pywencai.get(
    query='连续涨停天数大于2天的股票',
    cookie='xxx'
)
print(res)
```

### Query Financial Data

```python
import pywencai

# Query stocks with ROE > 15% and revenue growth > 20%
res = pywencai.get(
    query='ROE大于15%且营收同比增长率大于20%的股票',
    cookie='xxx'
)
print(res)

# Query stocks with P/E < 10 and P/B < 1 (undervalued screening)
res = pywencai.get(
    query='市盈率小于10且市净率小于1的股票',
    cookie='xxx'
)
print(res)
```


### Query Technical Indicator Data

```python
import pywencai

# Query stocks with a MACD golden cross today
res = pywencai.get(
    query='今日MACD金叉的股票',
    cookie='xxx'
)
print(res)

# Query stocks with KDJ oversold signal
res = pywencai.get(
    query='KDJ的J值小于0的股票',
    cookie='xxx'
)
print(res)

# Query stocks with volume breakout
res = pywencai.get(
    query='今日成交量是5日均量2倍以上且涨幅大于5%的股票',
    cookie='xxx'
)
print(res)
```

### Query Capital Flow Data

```python
import pywencai

# Query top 20 stocks by net main capital inflow today
res = pywencai.get(
    query='今日主力资金净流入前20的股票',
    cookie='xxx'
)
print(res)

# Query stocks with the highest northbound capital holding ratio
res = pywencai.get(
    query='北向资金持股比例最高的前20只股票',
    cookie='xxx'
)
print(res)
```

### Query Fund Data

```python
import pywencai

# Query top 20 funds by return rate over the past year
res = pywencai.get(
    query='近一年收益率最高的前20只基金',
    query_type='fund',     # Set query type to fund
    cookie='xxx'
)
print(res)
```

### Query Hong Kong Stock Data

```python
import pywencai

# Query the largest HK stocks by market cap
res = pywencai.get(
    query='港股市值最大的前20只股票',
    query_type='hkstock',  # Set query type to HK stock
    cookie='xxx'
)
print(res)
```


### Multi-Criteria Stock Screening

```python
import pywencai

# Complex multi-criteria screening: undervalued + high growth + institutional holdings
res = pywencai.get(
    query='市盈率小于20且营收同比增长大于30%且机构持仓比例大于10%的股票',
    cookie='xxx'
)
print(res)

# Technical + fundamental combined screening
res = pywencai.get(
    query='今日站上20日均线且市盈率小于30且ROE大于10%的股票',
    cookie='xxx'
)
print(res)
```

### Retrieve Historical Data

```python
import pywencai

# Query data for a specific date
res = pywencai.get(
    query='2024年1月2日涨幅前10的股票',
    cookie='xxx'
)
print(res)

# Query gain over a date range
res = pywencai.get(
    query='2024年上半年涨幅最大的前20只股票',
    cookie='xxx'
)
print(res)
```

### Full Example: Automated Stock Screening and Export

```python
import pywencai
import pandas as pd
import time

cookie = 'your_cookie_here'

# Define multiple screening strategies
strategies = {
    "低估值高分红": "市盈率小于15且股息率大于3%的股票",
    "高成长": "营收同比增长大于30%且净利润同比增长大于30%的股票",
    "技术突破": "今日放量突破20日均线且涨幅大于3%的股票",
    "机构关注": "近一个月机构调研次数大于3次的股票",
    "北向资金": "北向资金今日净买入前20的股票",
}

results = {}
for name, query in strategies.items():
    try:
        res = pywencai.get(query=query, cookie=cookie, no_detail=True)
        if res is not None and not res.empty:
            results[name] = res
            print(f"Strategy [{name}] selected {len(res)} stocks")
        else:
            print(f"Strategy [{name}] returned no results")
    except Exception as e:
        print(f"Strategy [{name}] query failed: {e}")
    time.sleep(2)  # Wait 2 seconds between queries to avoid being blocked

# Save results to Excel (one sheet per strategy)
if results:
    with pd.ExcelWriter("选股结果.xlsx") as writer:
        for name, df in results.items():
            df.to_excel(writer, sheet_name=name, index=False)
    print("Screening results saved to 选股结果.xlsx")
```

---

## 社区与支持

由 **大佬量化 (Boss Quant)** 维护 — 量化交易教学与策略研发团队。

微信客服: **bossquant1** · [Bilibili](https://space.bilibili.com/48693330) · 搜索 **大佬量化** on 微信公众号 / Bilibili / 抖音