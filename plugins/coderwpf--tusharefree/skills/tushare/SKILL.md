---
name: tushare
description: "Tushare Pro Financial Big Data Platform — Provides A-share, index, fund, futures, bond, and macro data, accessed via Token authentication."
homepage: https://tushare.pro
---

# Tushare Pro (Big Data Open Community)

[Tushare Pro](https://tushare.pro) is a widely used financial data platform in China, serving over 300,000 users. It provides a standardized Python API covering A-shares, indices, funds, futures, bonds, and macro data. All interfaces return `pandas.DataFrame`.

> ⚠️ **Token Required**: Register at https://tushare.pro and obtain your personal Token from the User Center. Some interfaces require a higher credit level. See the Credit System section below.

## Installation

```bash
pip install tushare --upgrade
```

## Initialization & Basic Usage

```python
import tushare as ts

# Set Token (only needs to be set once per session)
ts.set_token('your_token_here')

# Initialize the Pro API
pro = ts.pro_api()

# Call any data interface
df = pro.daily(ts_code='000001.SZ', start_date='20240101', end_date='20240630')
print(df)
```

You can also pass the Token directly during initialization:

```python
# Initialize with Token directly
pro = ts.pro_api('your_token_here')
```

## Stock Code Format (ts_code)

- Shanghai: `600000.SH`, `601398.SH`
- Shenzhen: `000001.SZ`, `300750.SZ`
- Beijing: `430047.BJ`
- Indices: `000001.SH` (SSE Composite Index), `399001.SZ` (SZSE Component Index)

---

## Shanghai & Shenzhen Stock Data

### Stock List

```python
# Get basic information for all currently listed stocks
df = pro.stock_basic(
    exchange='',
    list_status='L',      # L=Listed, D=Delisted, P=Suspended
    fields='ts_code,symbol,name,area,industry,list_date'
)
```

Credit requirement: 120

### Daily K-Line Data

```python
# Get daily market data for a specified stock
df = pro.daily(
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20240630'
)
# Returned fields: ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount
```

Credit requirement: 120

### Weekly / Monthly Data

```python
# Get weekly data
df = pro.weekly(ts_code='000001.SZ', start_date='20240101', end_date='20240630')
# Get monthly data
df = pro.monthly(ts_code='000001.SZ', start_date='20240101', end_date='20240630')
```

### Minute-Level K-Line Data

```python
# Get minute-level K-line data
df = pro.stk_mins(
    ts_code='000001.SZ',
    freq='5min',           # Options: 1min, 5min, 15min, 30min, 60min
    start_date='2024-01-02 09:30:00',
    end_date='2024-01-02 15:00:00'
)
```

Credit requirement: 2000+

### Adjustment Factor

```python
# Get adjustment factors for calculating forward/backward adjusted prices
df = pro.adj_factor(ts_code='000001.SZ', trade_date='20240102')
```

### Daily Indicators

```python
# Get daily market indicator data (PE ratio, PB ratio, turnover rate, market cap, etc.)
df = pro.daily_basic(
    ts_code='000001.SZ',
    trade_date='20240102',
    fields='ts_code,trade_date,turnover_rate,volume_ratio,pe,pe_ttm,pb,ps,ps_ttm,dv_ratio,dv_ttm,total_mv,circ_mv'
)
```

Credit requirement: 120

### Suspension & Resumption Information

```python
# Get suspension & resumption info, S=Suspended
df = pro.suspend_d(ts_code='000001.SZ', suspend_type='S')
```

---

## Financial Data

### Income Statement

```python
# Get listed company income statement data
df = pro.income(ts_code='000001.SZ', period='20231231')
```

### Balance Sheet

```python
# Get listed company balance sheet data
df = pro.balancesheet(ts_code='000001.SZ', period='20231231')
```

### Cash Flow Statement

```python
# Get listed company cash flow statement data
df = pro.cashflow(ts_code='000001.SZ', period='20231231')
```

### Financial Indicators

```python
# Get financial indicator data (ROE, EPS, revenue growth rate, net profit growth rate, etc.)
df = pro.fina_indicator(ts_code='000001.SZ', period='20231231')
```

### Earnings Forecast

```python
# Get listed company earnings forecast data
df = pro.forecast(ts_code='000001.SZ', period='20231231')
```

### Earnings Express Report

```python
# Get listed company earnings express report data
df = pro.express(ts_code='000001.SZ', period='20231231')
```

### Dividends & Share Distribution

```python
# Get listed company dividend and share distribution data
df = pro.dividend(ts_code='000001.SZ')
```

---

## Market Reference Data

### Individual Stock Money Flow

```python
# Get individual stock money flow data
df = pro.moneyflow(ts_code='000001.SZ', start_date='20240101', end_date='20240630')
```

Credit requirement: 2000+

### Top List (Dragon & Tiger List)

```python
# Get Dragon & Tiger list data
df = pro.top_list(trade_date='20240102')
```

### Block Trades

```python
# Get block trade data
df = pro.block_trade(ts_code='000001.SZ', start_date='20240101', end_date='20240630')
```

### Margin Trading

```python
# Get margin trading detail data
df = pro.margin_detail(trade_date='20240102')
```

### Shareholder Increase/Decrease in Holdings

```python
# Get shareholder increase/decrease in holdings data
df = pro.stk_holdertrade(ts_code='000001.SZ', start_date='20240101', end_date='20240630')
```

---

## Index Data

### Index Daily K-Line

```python
# Get index daily market data
df = pro.index_daily(ts_code='000300.SH', start_date='20240101', end_date='20240630')
```

### Index Constituents

```python
# Get index constituents and weights
df = pro.index_weight(index_code='000300.SH', start_date='20240101', end_date='20240630')
```

### Index Basic Information

```python
# Get index basic information; market options: SSE (Shanghai Stock Exchange), SZSE (Shenzhen Stock Exchange), etc.
df = pro.index_basic(market='SSE')
```

---

## Fund Data

### Fund List

```python
# Get fund list; E=Exchange-traded, O=OTC (over-the-counter)
df = pro.fund_basic(market='E')
```

### Fund Daily Market Data

```python
# Get exchange-traded fund daily market data
df = pro.fund_daily(ts_code='510300.SH', start_date='20240101', end_date='20240630')
```

### Fund Net Asset Value

```python
# Get OTC fund net asset value data
df = pro.fund_nav(ts_code='000001.OF')
```

---

## Futures Data

### Futures Daily Data

```python
# Get futures daily market data
df = pro.fut_daily(ts_code='IF2401.CFX', start_date='20240101', end_date='20240131')
```

### Futures Basic Information

```python
# Get futures contract basic information
# exchange options: CFFEX (China Financial Futures Exchange), SHFE (Shanghai Futures Exchange), DCE (Dalian Commodity Exchange), CZCE (Zhengzhou Commodity Exchange), INE (Shanghai International Energy Exchange)
df = pro.fut_basic(exchange='CFFEX', fut_type='1')
```

---

## Bond Data

### Convertible Bond List

```python
# Get convertible bond basic information
df = pro.cb_basic()
```

### Convertible Bond Daily Data

```python
# Get convertible bond daily market data
df = pro.cb_daily(ts_code='113009.SH', start_date='20240101', end_date='20240630')
```

---

## Macroeconomic Data

### Shibor Rate

```python
# Get Shanghai Interbank Offered Rate
df = pro.shibor(start_date='20240101', end_date='20240630')
```

### GDP

```python
# Get China GDP data
df = pro.cn_gdp()
```

### CPI

```python
# Get China Consumer Price Index
df = pro.cn_cpi(start_m='202401', end_m='202406')
```

### PPI

```python
# Get China Producer Price Index
df = pro.cn_ppi(start_m='202401', end_m='202406')
```

### Money Supply

```python
# Get China money supply data (M0, M1, M2)
df = pro.cn_m(start_m='202401', end_m='202406')
```

---

## Trading Calendar

```python
# Get trading calendar
df = pro.trade_cal(
    exchange='SSE',        # Exchange: SSE (Shanghai), SZSE (Shenzhen), BSE (Beijing)
    start_date='20240101',
    end_date='20241231',
    fields='exchange,cal_date,is_open,pretrade_date'
)
```

---

## Full Example: Download Stock Data and Save as CSV

```python
import tushare as ts
import pandas as pd

ts.set_token('your_token_here')
pro = ts.pro_api()

# Get Kweichow Moutai daily K-line data
df = pro.daily(ts_code='600519.SH', start_date='20240101', end_date='20241231')

# Get adjustment factors and calculate forward-adjusted closing price
adj = pro.adj_factor(ts_code='600519.SH', start_date='20240101', end_date='20241231')
df = df.merge(adj[['trade_date', 'adj_factor']], on='trade_date')
df['adj_close'] = df['close'] * df['adj_factor']  # Calculate forward-adjusted price

# Save as CSV file
df.to_csv('moutai_2024.csv', index=False)
print(df.head())
```

## Credit System

| Level | Credits | Example Available Interfaces |
|---|---|---|
| **Basic** | 120 | `stock_basic`, `daily`, `weekly`, `monthly`, `trade_cal`, `daily_basic` |
| **Intermediate** | 2000 | `stk_mins` (minute data), `moneyflow`, `margin_detail`, `fina_indicator` |
| **Advanced** | 5000+ | Tick data, large order data, higher rate limits |

### How to Earn Credits for Free

1. Register and complete your profile → Earn 120 credits
2. Daily check-in at tushare.pro
3. Community contributions (sharing, answering questions)
4. Invite friends to register

## Usage Tips

- **Token is required** — Register for free at https://tushare.pro to obtain one (User Center).
- **Date format**: `YYYYMMDD` (no hyphens); all date parameters use this format.
- **ts_code format**: `{code}.{exchange}` — e.g., `000001.SZ`, `600519.SH`.
- All interfaces return **pandas DataFrame**.
- Rate limits depend on your credit level — higher credits allow more calls per minute.
- Use the `fields` parameter to select only the fields you need, improving query performance.
- Cache reference data (stock list, trading calendar) locally to avoid repeated calls.
- Documentation: https://tushare.pro/document/2

---

## Advanced Examples

### Batch Download Multiple Stocks

```python
import tushare as ts
import pandas as pd
import time

ts.set_token('your_token_here')
pro = ts.pro_api()

# Define the list of stocks to download
stock_list = ['000001.SZ', '600519.SH', '300750.SZ', '601318.SH', '000858.SZ']

all_data = []
for ts_code in stock_list:
    # Get daily K-line data
    df = pro.daily(ts_code=ts_code, start_date='20240101', end_date='20240630')
    all_data.append(df)
    print(f"Downloaded {ts_code}, {len(df)} records")
    time.sleep(0.3)  # Throttle request frequency to avoid rate limiting

# Combine all data
combined = pd.concat(all_data, ignore_index=True)
combined.to_csv("multi_stock_tushare.csv", index=False)
print(f"Combined total: {len(combined)} records")
```

### Calculate Forward-Adjusted Prices

```python
import tushare as ts
import pandas as pd

ts.set_token('your_token_here')
pro = ts.pro_api()

ts_code = '600519.SH'

# Get daily K-line and adjustment factors
df = pro.daily(ts_code=ts_code, start_date='20240101', end_date='20241231')
adj = pro.adj_factor(ts_code=ts_code, start_date='20240101', end_date='20241231')

# Merge data
df = df.merge(adj[['trade_date', 'adj_factor']], on='trade_date')

# Calculate forward-adjusted prices (using the latest date's adjustment factor as the base)
latest_factor = df['adj_factor'].iloc[0]  # Latest adjustment factor
df['adj_open'] = df['open'] * df['adj_factor'] / latest_factor
df['adj_high'] = df['high'] * df['adj_factor'] / latest_factor
df['adj_low'] = df['low'] * df['adj_factor'] / latest_factor
df['adj_close'] = df['close'] * df['adj_factor'] / latest_factor

print(df[['trade_date', 'close', 'adj_factor', 'adj_close']].head(10))
```

### Get Market-Wide Daily Indicators and Filter

```python
import tushare as ts
import pandas as pd

ts.set_token('your_token_here')
pro = ts.pro_api()

# Get market-wide daily indicators for a given date
df = pro.daily_basic(trade_date='20240628',
    fields='ts_code,trade_date,close,turnover_rate,pe_ttm,pb,ps_ttm,dv_ratio,total_mv,circ_mv')

# Filter criteria: PE between 5-20, PB between 0.5-3, dividend yield above 2%
filtered = df[
    (df['pe_ttm'] > 5) & (df['pe_ttm'] < 20) &
    (df['pb'] > 0.5) & (df['pb'] < 3) &
    (df['dv_ratio'] > 2)
].sort_values('pe_ttm')

print(f"Filtered {len(filtered)} stocks")
print(filtered[['ts_code', 'close', 'pe_ttm', 'pb', 'dv_ratio', 'total_mv']].head(20))
```

### Get Financial Data and Analyze

```python
import tushare as ts
import pandas as pd

ts.set_token('your_token_here')
pro = ts.pro_api()

# Get CSI 300 constituents
hs300 = pro.index_weight(index_code='000300.SH', start_date='20240601', end_date='20240630')
stock_codes = hs300['con_code'].unique().tolist()

# Get financial indicators (first 10 stocks as example)
fin_data = []
for code in stock_codes[:10]:
    df = pro.fina_indicator(ts_code=code, period='20231231',
        fields='ts_code,ann_date,roe,roa,grossprofit_margin,netprofit_yoy,or_yoy')
    if not df.empty:
        fin_data.append(df.iloc[0])

fin_df = pd.DataFrame(fin_data)
print("CSI 300 Selected Constituent Financial Indicators:")
print(fin_df[['ts_code', 'roe', 'roa', 'grossprofit_margin', 'netprofit_yoy']].to_string())
```

### Get Money Flow Data

```python
import tushare as ts

ts.set_token('your_token_here')
pro = ts.pro_api()

# Get individual stock money flow (requires 2000+ credits)
df = pro.moneyflow(ts_code='000001.SZ', start_date='20240601', end_date='20240630')
# Fields include: buy_sm_vol (small order buy volume), sell_sm_vol (small order sell volume),
#                 buy_md_vol (medium order buy volume), buy_lg_vol (large order buy volume),
#                 buy_elg_vol (extra-large order buy volume), etc.
print(df.head())
```

### Full Example: Simple Backtesting Framework

```python
import tushare as ts
import pandas as pd
import numpy as np

ts.set_token('your_token_here')
pro = ts.pro_api()

# Get Ping An Bank daily K-line data
df = pro.daily(ts_code='000001.SZ', start_date='20230101', end_date='20231231')
df = df.sort_values('trade_date').reset_index(drop=True)  # Sort by date ascending

# Get adjustment factors and calculate forward-adjusted closing price
adj = pro.adj_factor(ts_code='000001.SZ', start_date='20230101', end_date='20231231')
df = df.merge(adj[['trade_date', 'adj_factor']], on='trade_date')
latest_factor = df['adj_factor'].iloc[-1]
df['adj_close'] = df['close'] * df['adj_factor'] / latest_factor

# Calculate dual moving averages
df['MA5'] = df['adj_close'].rolling(5).mean()
df['MA20'] = df['adj_close'].rolling(20).mean()

# Simple backtest
initial_cash = 100000
cash = initial_cash
shares = 0
trades = []

for i in range(20, len(df)):
    # Golden cross — buy signal
    if df['MA5'].iloc[i] > df['MA20'].iloc[i] and df['MA5'].iloc[i-1] <= df['MA20'].iloc[i-1]:
        if cash > 0:
            price = df['adj_close'].iloc[i]
            shares = int(cash / price / 100) * 100
            cash -= shares * price
            trades.append(f"{df['trade_date'].iloc[i]} BUY {shares} shares @ {price:.2f}")
    # Death cross — sell signal
    elif df['MA5'].iloc[i] < df['MA20'].iloc[i] and df['MA5'].iloc[i-1] >= df['MA20'].iloc[i-1]:
        if shares > 0:
            price = df['adj_close'].iloc[i]
            cash += shares * price
            trades.append(f"{df['trade_date'].iloc[i]} SELL {shares} shares @ {price:.2f}")
            shares = 0

final_value = cash + shares * df['adj_close'].iloc[-1]
print(f"Initial capital: {initial_cash:.2f}")
print(f"Final portfolio value: {final_value:.2f}")
print(f"Return: {(final_value/initial_cash - 1)*100:.2f}%")
for t in trades:
    print(f"  {t}")
```

---

## 社区与支持

由 **大佬量化 (Boss Quant)** 维护 — 量化交易教学与策略研发团队。

微信客服: **bossquant1** · [Bilibili](https://space.bilibili.com/48693330) · 搜索 **大佬量化** on 微信公众号 / Bilibili / 抖音
