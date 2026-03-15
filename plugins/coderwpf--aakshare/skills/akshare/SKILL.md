---
name: akshare
description: "Comprehensive free financial data API library — supports A-shares, Hong Kong stocks, US stocks, futures, options, funds, bonds, forex, and macro data, no API key required."
homepage: https://github.com/akfamily/akshare
---

# AKShare (Open-Source Financial Data API Library)

[AKShare](https://github.com/akfamily/akshare) is a comprehensive, free Python financial data API library covering A-shares, Hong Kong stocks, US stocks, futures, options, funds, bonds, forex, and macroeconomic data. No registration or API key is required, and all functions return `pandas.DataFrame`.

> Documentation: https://akshare.akfamily.xyz/

## Installation

```bash
pip install akshare --upgrade
```

Requires Python 3.9+ (64-bit).

## Basic Usage

```python
import akshare as ak

# Get daily candlestick data for Ping An Bank
df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20240101", end_date="20240630")
print(df)
```

## Function Naming Convention

```
{asset_type}_{market}_{data_type}_{data_source}
```

- **Asset type**: `stock` (stocks), `futures` (futures), `fund` (funds), `bond` (bonds), `forex` (foreign exchange), `option` (options), `macro` (macroeconomics), `index` (indices)
- **Market**: `zh` (China), `us` (United States), `hk` (Hong Kong), or exchange codes
- **Data type**: `spot` (real-time), `hist` (historical), `daily` (daily bars), `minute` (minute bars)
- **Data source**: `em` (East Money), `sina` (Sina Finance), exchange abbreviations

---

## Stock Data (A-Shares)

### Real-Time Quotes — All A-Shares

```python
import akshare as ak

# Get real-time quotes for all A-shares
df = ak.stock_zh_a_spot_em()
# Returned columns: 序号 (index), 代码 (code), 名称 (name), 最新价 (latest price), 涨跌幅 (change %), 涨跌额 (change amount), 成交量 (volume), 成交额 (turnover), 振幅 (amplitude), 最高 (high), 最低 (low), 今开 (open), 昨收 (prev close), 量比 (volume ratio), 换手率 (turnover rate), 市盈率 (P/E ratio), 市净率 (P/B ratio), ...
```

### Historical Candlestick Data

```python
# Get historical daily candlestick data for a specific stock
df = ak.stock_zh_a_hist(
    symbol="000001",       # Stock code (without prefix)
    period="daily",        # Period: "daily", "weekly", "monthly"
    start_date="20240101", # Start date, format YYYYMMDD
    end_date="20240630",   # End date
    adjust=""              # Adjustment: "" (unadjusted), "qfq" (forward-adjusted), "hfq" (backward-adjusted)
)
# Returned columns: 日期 (date), 开盘 (open), 收盘 (close), 最高 (high), 最低 (low), 成交量 (volume), 成交额 (turnover), 振幅 (amplitude), 涨跌幅 (change %), 涨跌额 (change amount), 换手率 (turnover rate)
```

### Minute-Level Candlestick Data

```python
# Get minute-level candlestick data
df = ak.stock_zh_a_hist_min_em(
    symbol="000001",
    period="5",            # Minute interval: "1", "5", "15", "30", "60"
    start_date="2024-01-02 09:30:00",
    end_date="2024-01-02 15:00:00",
    adjust=""              # Adjustment type
)
```

### Individual Stock Basic Info

```python
# Get basic information for an individual stock
df = ak.stock_individual_info_em(symbol="000001")
# Returned columns: 总市值 (total market cap), 流通市值 (circulating market cap), 行业 (industry), 上市时间 (listing date), 股票代码 (stock code), 股票简称 (stock name), 总股本 (total shares), 流通股 (circulating shares) ...
```

---

## Hong Kong Stock Data

```python
# Hong Kong stock real-time quotes
df = ak.stock_hk_spot_em()

# Hong Kong stock historical candlestick data
df = ak.stock_hk_hist(
    symbol="00700",        # Tencent Holdings
    period="daily",        # Daily bars
    start_date="20240101",
    end_date="20240630",
    adjust="qfq"           # Forward-adjusted
)
```

---

## US Stock Data

```python
# US stock daily candlestick data
df = ak.stock_us_daily(symbol="AAPL", adjust="qfq")

# US stock real-time quotes
df = ak.stock_us_spot_em()
```

---

## Index Data

```python
# A-share index historical data (e.g., Shanghai Composite Index 000001)
df = ak.stock_zh_index_daily_em(symbol="sh000001")

# Index constituents (e.g., CSI 300)
df = ak.index_stock_cons_csindex(symbol="000300")
```

---

## Fund Data

```python
# ETF real-time quotes
df = ak.fund_etf_spot_em()

# ETF historical candlestick data
df = ak.fund_etf_hist_em(
    symbol="510300",       # CSI 300 ETF
    period="daily",
    start_date="20240101",
    end_date="20240630",
    adjust="qfq"
)

# Open-end fund daily NAV
df = ak.fund_open_fund_daily_em(symbol="000001")

# Fund ratings
df = ak.fund_rating_all()
```

---

## Futures Data

```python
# Futures daily data (aggregated by exchange)
from akshare import get_futures_daily
df = get_futures_daily(start_date="20240101", end_date="20240102", market="CFFEX")
# market options: "CFFEX" (China Financial Futures Exchange), "SHFE" (Shanghai Futures Exchange), "DCE" (Dalian Commodity Exchange), "CZCE" (Zhengzhou Commodity Exchange), "INE" (Shanghai International Energy Exchange), "GFEX" (Guangzhou Futures Exchange)

# Futures real-time quotes
df = ak.futures_zh_spot()

# Futures inventory data
df = ak.futures_inventory_99(symbol="豆一")
```

---

## Options Data

```python
# Exchange options historical data
df = ak.option_hist_dce(symbol="豆粕期权")

# SSE 50 ETF options
df = ak.option_sse_spot_price(symbol="510050")
```

---

## Bond Data

```python
# Convertible bond list
df = ak.bond_zh_cov()

# Convertible bond historical candlestick data
df = ak.bond_zh_hs_cov_daily(symbol="sz123456")

# China bond spot quotes
df = ak.bond_spot_quote()
```

---

## Forex Data

```python
# Forex real-time quotes (East Money)
df = ak.forex_spot_em()

# Forex spot quotes (China Foreign Exchange Trade System)
df = ak.fx_spot_quote()

# Forex swap quotes
df = ak.fx_swap_quote()
```

---

## Macroeconomic Data

```python
# China CPI annual data
df = ak.macro_china_cpi_yearly()

# China GDP annual data
df = ak.macro_china_gdp_yearly()

# China PMI data
df = ak.macro_china_pmi()

# US Non-Farm Payrolls data
df = ak.macro_usa_non_farm()

# US CPI monthly data
df = ak.macro_usa_cpi_monthly()
```

---

## News and Sentiment

```python
# Individual stock financial news (East Money)
df = ak.stock_news_em(symbol="000001")

# CCTV news
df = ak.news_cctv(date="20240101")
```

---

## Complete Example: Download Data and Plot a Candlestick Chart

```python
import akshare as ak
import pandas as pd
import mplfinance as mpf  # pip install mplfinance

# Get forward-adjusted daily candlestick data for Kweichow Moutai
df = ak.stock_zh_a_hist(
    symbol="600519",
    period="daily",
    start_date="20240101",
    end_date="20240630",
    adjust="qfq"
)

# Set date index and rename columns to English (required by mplfinance)
df.index = pd.to_datetime(df["日期"])  # 日期 = Date
df.rename(columns={
    "开盘": "Open",    # 开盘 = Open price
    "收盘": "Close",   # 收盘 = Close price
    "最高": "High",    # 最高 = High price
    "最低": "Low",     # 最低 = Low price
    "成交量": "Volume" # 成交量 = Volume
}, inplace=True)

# Plot candlestick chart with 5/10/20-day moving averages and volume
mpf.plot(df, type="candle", mav=(5, 10, 20), volume=True)
```

## Usage Tips

- **No API key or registration required** — works out of the box.
- All functions return **pandas DataFrame** — ready for analysis, export, and visualization.
- A-share data columns are in **Chinese**; US/HK stock data columns are in English.
- Use `--upgrade` to keep akshare up to date — interfaces update frequently due to upstream data source changes.
- Non-Python users can use the [AKTools](https://aktools.readthedocs.io/) HTTP API wrapper.
- Data is for **academic research** only — not investment advice.
- Full API reference: https://akshare.akfamily.xyz/data/index.html

---

## Advanced Examples

### Batch Download Multiple Stocks

```python
import akshare as ak
import pandas as pd

# Define the list of stocks to download
stock_list = ["000001", "600519", "300750", "601318", "000858"]

all_data = {}
for symbol in stock_list:
    # Download forward-adjusted daily candlestick data for each stock
    df = ak.stock_zh_a_hist(
        symbol=symbol,
        period="daily",
        start_date="20240101",
        end_date="20240630",
        adjust="qfq"
    )
    df["股票代码"] = symbol  # Add stock code column (股票代码) for later merging
    all_data[symbol] = df
    print(f"Downloaded {symbol}, {len(df)} records")

# Merge all stock data into one large DataFrame
combined = pd.concat(all_data.values(), ignore_index=True)
combined.to_csv("multi_stock_data.csv", index=False)
print(f"Combined total: {len(combined)} records")
```

### Calculate Technical Indicators (Moving Averages, MACD, RSI)

```python
import akshare as ak
import pandas as pd
import numpy as np

# Get forward-adjusted daily candlestick data for Kweichow Moutai
df = ak.stock_zh_a_hist(symbol="600519", period="daily",
                         start_date="20240101", end_date="20241231", adjust="qfq")

# Convert close price to float (收盘 = close price)
df["收盘"] = df["收盘"].astype(float)

# Calculate moving averages
df["MA5"] = df["收盘"].rolling(window=5).mean()    # 5-day moving average
df["MA10"] = df["收盘"].rolling(window=10).mean()   # 10-day moving average
df["MA20"] = df["收盘"].rolling(window=20).mean()   # 20-day moving average
df["MA60"] = df["收盘"].rolling(window=60).mean()   # 60-day moving average

# Calculate MACD indicator
ema12 = df["收盘"].ewm(span=12, adjust=False).mean()  # 12-day exponential moving average
ema26 = df["收盘"].ewm(span=26, adjust=False).mean()  # 26-day exponential moving average
df["DIF"] = ema12 - ema26                              # Fast line (DIF)
df["DEA"] = df["DIF"].ewm(span=9, adjust=False).mean() # Slow line (DEA)
df["MACD"] = 2 * (df["DIF"] - df["DEA"])               # MACD histogram

# Calculate RSI indicator (14-day)
delta = df["收盘"].diff()
gain = delta.where(delta > 0, 0)       # Upward movement
loss = -delta.where(delta < 0, 0)      # Downward movement
avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()
rs = avg_gain / avg_loss
df["RSI14"] = 100 - (100 / (1 + rs))   # RSI value

# Calculate Bollinger Bands (20-day)
df["BOLL_MID"] = df["收盘"].rolling(window=20).mean()           # Middle band
df["BOLL_UP"] = df["BOLL_MID"] + 2 * df["收盘"].rolling(window=20).std()  # Upper band
df["BOLL_DN"] = df["BOLL_MID"] - 2 * df["收盘"].rolling(window=20).std()  # Lower band

# 日期 = date, 收盘 = close price
print(df[["日期", "收盘", "MA5", "MA20", "DIF", "DEA", "MACD", "RSI14"]].tail(10))
```

### Filter Limit-Up Stocks

```python
import akshare as ak

# Get real-time quotes for all A-shares
df = ak.stock_zh_a_spot_em()

# Filter stocks with gain > 9.5% (near daily limit-up)
df["涨跌幅"] = df["涨跌幅"].astype(float)  # 涨跌幅 = change percentage
limit_up = df[df["涨跌幅"] >= 9.5].sort_values("涨跌幅", ascending=False)
print(f"Today's limit-up / near limit-up stocks: {len(limit_up)} total")
# 代码 = code, 名称 = name, 最新价 = latest price, 涨跌幅 = change %, 成交额 = turnover, 换手率 = turnover rate
print(limit_up[["代码", "名称", "最新价", "涨跌幅", "成交额", "换手率"]].head(20))
```

### Get Dragon-Tiger List Data

```python
import akshare as ak

# Get Dragon-Tiger list detail data
df = ak.stock_lhb_detail_em(start_date="20240101", end_date="20240131")
print(df.head())

# Get Dragon-Tiger list brokerage branch rankings
df_dept = ak.stock_lhb_hyyyb_em(start_date="20240101", end_date="20240131")
print(df_dept.head())
```

### Get Margin Trading Data

```python
import akshare as ak

# Get Shanghai-Shenzhen margin trading summary data
df = ak.stock_margin_sse(start_date="20240101", end_date="20240630")
print(df.head())

# Get individual stock margin trading details
df_detail = ak.stock_margin_detail_sse(date="20240102")
print(df_detail.head())
```

### Get Northbound Capital (Stock Connect) Data

```python
import akshare as ak

# Get northbound capital historical data
df = ak.stock_hsgt_hist_em(symbol="北向资金")  # 北向资金 = Northbound capital
print(df.tail(10))

# Get northbound capital stock holdings details
df_hold = ak.stock_hsgt_hold_stock_em(market="北向", indicator="今日排行")  # 北向 = Northbound, 今日排行 = Today's ranking
print(df_hold.head(20))
```

### Get Shareholder Data

```python
import akshare as ak

# Get top 10 shareholders
df = ak.stock_gdfx_top_10_em(symbol="600519", date="20231231")
print(df)

# Get top 10 tradable shareholders
df_float = ak.stock_gdfx_free_top_10_em(symbol="600519", date="20231231")
print(df_float)
```

### Get Sector Quotes Data

```python
import akshare as ak

# Get industry sector quotes
df_industry = ak.stock_board_industry_name_em()
print(df_industry.head(20))

# Get concept sector quotes
df_concept = ak.stock_board_concept_name_em()
print(df_concept.head(20))

# Get constituent stocks of a specific sector
df_stocks = ak.stock_board_industry_cons_em(symbol="银行")  # 银行 = Banking
print(df_stocks)
```

### Get Lock-Up Share Release Data

```python
import akshare as ak

# Get lock-up share release data
df = ak.stock_restricted_release_queue_em(symbol="全部A股")  # 全部A股 = All A-shares
print(df.head(20))
```

### Get Market Capital Flow

```python
import akshare as ak

# Get overall market capital flow
df = ak.stock_market_fund_flow()
print(df.tail(10))

# Get individual stock capital flow
df_stock = ak.stock_individual_fund_flow(stock="000001", market="sz")
print(df_stock.tail(10))
```

### Complete Example: Multi-Factor Stock Screening

```python
import akshare as ak
import pandas as pd

# Step 1: Get all A-share real-time quotes
df = ak.stock_zh_a_spot_em()

# Step 2: Convert data types
for col in ["市盈率-动态", "市净率", "换手率", "涨跌幅", "成交额"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Step 3: Multi-factor screening
# Condition 1: PE between 5-30 (exclude loss-making and overvalued)
# Condition 2: PB between 0.5-5
# Condition 3: Turnover rate > 1% (reasonable liquidity)
# Condition 4: Daily change between -3% and 3% (exclude abnormal volatility)
filtered = df[
    (df["市盈率-动态"] > 5) & (df["市盈率-动态"] < 30) &
    (df["市净率"] > 0.5) & (df["市净率"] < 5) &
    (df["换手率"] > 1) &
    (df["涨跌幅"] > -3) & (df["涨跌幅"] < 3)
].copy()

# Step 4: Sort by PE, select top 20 lowest PE stocks
result = filtered.sort_values("市盈率-动态").head(20)
print(f"Selected {len(result)} stocks:")
print(result[["代码", "名称", "最新价", "市盈率-动态", "市净率", "换手率", "涨跌幅"]])
```

---

## 社区与支持

由 **大佬量化 (Boss Quant)** 维护 — 量化交易教学与策略研发团队。

微信客服: **bossquant1** · [Bilibili](https://space.bilibili.com/48693330) · 搜索 **大佬量化** on 微信公众号 / Bilibili / 抖音
