---
name: baostock
description: "Free China A-share data platform — supports K-line, financial data, and industry classification queries with no registration required."
homepage: https://www.baostock.com
---

# BaoStock (Free China A-Share Data Platform)

[BaoStock](https://www.baostock.com) is a free, open-source data platform for China A-share securities. No registration or API key is required, and it returns `pandas.DataFrame`.

## Installation

```bash
pip install baostock --upgrade
```

Verify the installation:

```bash
python3 -c "import baostock as bs; lg = bs.login(); print(lg.error_msg); bs.logout()"
```

Expected output: `login success!`.

## Basic Usage

Each session must begin with `bs.login()` and end with `bs.logout()`:

```python
import baostock as bs
import pandas as pd

# Log in to the system
lg = bs.login()

# ... perform data queries here ...

# Log out of the system
bs.logout()
```

Use `.get_data()` to retrieve the DataFrame from query results:

```python
rs = bs.query_all_stock()
df = rs.get_data()
```

## Core API

### 1. query_all_stock — Get All Securities List

Retrieves all stock/index codes for a specified trading day.

```python
# Get all securities codes for a specified date
rs = bs.query_all_stock(day="2024-01-02")
df = rs.get_data()
# Returns fields: code (securities code), tradeStatus (trading status), code_name (securities name)
```

- **day** — Date string `YYYY-MM-DD` (default: today). Returns an empty DataFrame on non-trading days.

### 2. query_history_k_data_plus — K-Line Data

Retrieves historical K-line data (OHLCV + indicators).

```python
# Get daily K-line data for ICBC
rs = bs.query_history_k_data_plus(
    "sh.601398",
    "date,code,open,high,low,close,volume,amount,pctChg",
    start_date="2024-01-01",
    end_date="2024-06-30",
    frequency="d",       # Frequency: d (daily), w (weekly), m (monthly), 5/15/30/60 (minute)
    adjustflag="3"       # Adjustment: 1 (forward), 2 (backward), 3 (none, default)
)
df = rs.get_data()
```

**Parameters:**

- **code** — Stock code, format `sh.600000` or `sz.000001`
- **fields** — Comma-separated field names (see below)
- **start_date / end_date** — `YYYY-MM-DD` format
- **frequency** — `d` (daily), `w` (weekly), `m` (monthly), `5`/`15`/`30`/`60` (minute). Indices have no minute-level data.
- **adjustflag** — `1` (forward adjustment), `2` (backward adjustment), `3` (no adjustment, default)

**Available fields for daily data:**

`date` (date), `code` (securities code), `open` (open price), `high` (high price), `low` (low price), `close` (close price), `preclose` (previous close price), `volume` (volume), `amount` (turnover), `adjustflag` (adjustment flag), `turn` (turnover rate), `tradestatus` (trading status), `pctChg` (percent change), `peTTM` (trailing P/E ratio), `pbMRQ` (P/B ratio), `psTTM` (trailing P/S ratio), `pcfNcfTTM` (trailing P/CF ratio), `isST` (is ST stock)

**Available fields for minute data:**

`date` (date), `time` (time), `code` (securities code), `open` (open price), `high` (high price), `low` (low price), `close` (close price), `volume` (volume), `amount` (turnover), `adjustflag` (adjustment flag)

### 3. query_trade_dates — Trading Calendar

```python
# Get the trading calendar for a specified range
rs = bs.query_trade_dates(start_date="2024-01-01", end_date="2024-12-31")
df = rs.get_data()
# Returns fields: calendar_date (calendar date), is_trading_day (whether it is a trading day)
```

### 4. query_stock_industry — Industry Classification

```python
# Get industry classification for all stocks
rs = bs.query_stock_industry()
df = rs.get_data()
# Returns fields: updateDate (update date), code (securities code), code_name (securities name), industry (industry), industryClassification (industry classification)
```

### 5. query_stock_basic — Stock Basic Information

```python
# Get basic information for a specified stock
rs = bs.query_stock_basic(code="sh.601398")
df = rs.get_data()
# Returns fields: code (securities code), code_name (securities name), ipoDate (IPO date), outDate (delisting date), type (type), status (status)
```

- **type** — `1` stock, `2` index, `3` other
- **status** — `1` listed, `0` delisted

### 6. query_dividend_data — Dividend Information

```python
# Get dividend data for a specified stock
rs = bs.query_dividend_data(code="sh.601398", year="2023", yearType="report")
df = rs.get_data()
```

- **yearType** — `report` (reporting period) or `operate` (implementation period)

### 7. Financial Data (Quarterly)

#### Profitability

```python
# Get profitability indicators (ROE, net profit margin, gross margin, etc.)
rs = bs.query_profit_data(code="sh.601398", year=2023, quarter=4)
df = rs.get_data()
```

#### Operational Efficiency

```python
# Get operational efficiency indicators (inventory turnover, accounts receivable turnover, etc.)
rs = bs.query_operation_data(code="sh.601398", year=2023, quarter=4)
df = rs.get_data()
```

#### Growth Capability

```python
# Get growth indicators (YoY revenue growth, YoY net profit growth, etc.)
rs = bs.query_growth_data(code="sh.601398", year=2023, quarter=4)
df = rs.get_data()
```

#### Solvency

```python
# Get solvency indicators (current ratio, quick ratio, etc.)
rs = bs.query_balance_data(code="sh.601398", year=2023, quarter=4)
df = rs.get_data()
```

#### Cash Flow

```python
# Get cash flow data
rs = bs.query_cash_flow_data(code="sh.601398", year=2023, quarter=4)
df = rs.get_data()
```

#### DuPont Analysis

```python
# Get DuPont analysis data (ROE decomposition: profit margin × asset turnover × equity multiplier)
rs = bs.query_dupont_data(code="sh.601398", year=2023, quarter=4)
df = rs.get_data()
```

### 8. Index Data

#### Index Constituent Stocks

```python
# Get CSI 300 constituent stocks
rs = bs.query_hs300_stocks()
df = rs.get_data()

# Get SSE 50 constituent stocks
rs = bs.query_sz50_stocks()
df = rs.get_data()

# Get CSI 500 constituent stocks
rs = bs.query_zz500_stocks()
df = rs.get_data()
```

## Full Example: Download Daily K-Line Data and Save as CSV

```python
import baostock as bs
import pandas as pd

# Log in to the system
bs.login()

# Get Kweichow Moutai 2024 daily K-line data (backward adjusted)
rs = bs.query_history_k_data_plus(
    "sh.600519",
    "date,code,open,high,low,close,volume,amount,pctChg,peTTM",
    start_date="2024-01-01",
    end_date="2024-12-31",
    frequency="d",
    adjustflag="2"  # Backward adjustment
)
df = rs.get_data()

# Save to CSV file
df.to_csv("kweichow_moutai_2024.csv", index=False)
print(df.head())

# Log out of the system
bs.logout()
```

## Stock Code Format

- Shanghai: `sh.600000`, `sh.601398`
- Shenzhen: `sz.000001`, `sz.300750`
- Beijing: `bj.430047`
- Indices: `sh.000001` (SSE Composite Index), `sh.000300` (CSI 300)

## Usage Tips

- **No registration or API key required** — just call `bs.login()` to get started.
- Sessions may time out after prolonged inactivity — simply call `bs.login()` again.
- **Not thread-safe** — for parallel downloads, use `multiprocessing` (multi-process), not threading (multi-thread).
- Data coverage: A-shares from 1990 to present.
- Financial data is provided quarterly, with approximately a 2-month delay after the reporting period ends.
- Documentation: http://baostock.com/baostock/index.php/Python_API%E6%96%87%E6%A1%A3

---

## Advanced Examples

### Batch Download Data for Multiple Stocks

```python
import baostock as bs
import pandas as pd

bs.login()

# Define the list of stocks to download
stock_list = ["sh.600519", "sh.601398", "sz.000001", "sz.300750", "sh.601318"]

all_data = []
for code in stock_list:
    # Get daily K-line data (forward adjusted)
    rs = bs.query_history_k_data_plus(
        code,
        "date,code,open,high,low,close,volume,amount,pctChg,turn,peTTM,pbMRQ",
        start_date="2024-01-01",
        end_date="2024-06-30",
        frequency="d",
        adjustflag="1"  # Forward adjustment
    )
    df = rs.get_data()
    all_data.append(df)
    print(f"Downloaded {code}, {len(df)} records")

# Merge all data
combined = pd.concat(all_data, ignore_index=True)
combined.to_csv("multi_stock_baostock.csv", index=False)
print(f"Total merged records: {len(combined)}")

bs.logout()
```

### Get Full Market Stock List and Filter

```python
import baostock as bs
import pandas as pd

bs.login()

# Get all securities for a specified date
rs = bs.query_all_stock(day="2024-06-28")
df = rs.get_data()

# Filter actively trading stocks (exclude indices and suspended stocks)
stocks = df[df["tradeStatus"] == "1"]
# Filter Shanghai A-shares (starting with sh.6)
sh_stocks = stocks[stocks["code"].str.startswith("sh.6")]
print(f"Shanghai A-shares: {len(sh_stocks)} stocks")

# Filter Shenzhen main board (starting with sz.00)
sz_main = stocks[stocks["code"].str.startswith("sz.00")]
print(f"Shenzhen main board: {len(sz_main)} stocks")

# Filter ChiNext board (starting with sz.30)
gem = stocks[stocks["code"].str.startswith("sz.30")]
print(f"ChiNext board: {len(gem)} stocks")

bs.logout()
```

### Calculate Technical Indicators

```python
import baostock as bs
import pandas as pd
import numpy as np

bs.login()

# Get Ping An Bank daily K-line data
rs = bs.query_history_k_data_plus(
    "sz.000001",
    "date,close,volume",
    start_date="2024-01-01",
    end_date="2024-12-31",
    frequency="d",
    adjustflag="1"
)
df = rs.get_data()
df["close"] = df["close"].astype(float)
df["volume"] = df["volume"].astype(float)

# Calculate moving averages
df["MA5"] = df["close"].rolling(5).mean()
df["MA10"] = df["close"].rolling(10).mean()
df["MA20"] = df["close"].rolling(20).mean()

# Calculate MACD
ema12 = df["close"].ewm(span=12, adjust=False).mean()
ema26 = df["close"].ewm(span=26, adjust=False).mean()
df["DIF"] = ema12 - ema26
df["DEA"] = df["DIF"].ewm(span=9, adjust=False).mean()
df["MACD"] = 2 * (df["DIF"] - df["DEA"])

# Calculate volume moving averages
df["VOL_MA5"] = df["volume"].rolling(5).mean()
df["VOL_MA10"] = df["volume"].rolling(10).mean()

# Detect golden cross / death cross signals
df["signal"] = 0
df.loc[(df["MA5"] > df["MA20"]) & (df["MA5"].shift(1) <= df["MA20"].shift(1)), "signal"] = 1   # Golden cross
df.loc[(df["MA5"] < df["MA20"]) & (df["MA5"].shift(1) >= df["MA20"].shift(1)), "signal"] = -1  # Death cross

golden_cross = df[df["signal"] == 1]
death_cross = df[df["signal"] == -1]
print(f"Golden crosses: {len(golden_cross)}, Death crosses: {len(death_cross)}")
print("Golden cross dates:", golden_cross["date"].tolist())

bs.logout()
```

### Get CSI 300 Constituent Stocks and Download Data

```python
import baostock as bs
import pandas as pd

bs.login()

# Get CSI 300 constituent stocks
rs = bs.query_hs300_stocks()
hs300 = rs.get_data()
print(f"CSI 300 has {len(hs300)} constituent stocks")

# Download daily K-line data for the first 10 constituent stocks
for _, row in hs300.head(10).iterrows():
    code = row["code"]
    name = row["code_name"]
    rs = bs.query_history_k_data_plus(
        code,
        "date,code,close,pctChg,turn",
        start_date="2024-06-01",
        end_date="2024-06-30",
        frequency="d",
        adjustflag="1"
    )
    df = rs.get_data()
    print(f"{name}({code}): {len(df)} records")

bs.logout()
```

### Get Financial Data and Analyze

```python
import baostock as bs
import pandas as pd

bs.login()

# Get profitability data for multiple bank stocks
bank_codes = ["sh.601398", "sh.601939", "sh.601288", "sh.600036", "sh.601166"]
profit_data = []

for code in bank_codes:
    rs = bs.query_profit_data(code=code, year=2023, quarter=4)
    df = rs.get_data()
    if not df.empty:
        profit_data.append(df.iloc[0])

profit_df = pd.DataFrame(profit_data)
# View ROE and net profit margin
print(profit_df[["code", "roeAvg", "npMargin", "gpMargin"]])

# Get growth capability data
growth_data = []
for code in bank_codes:
    rs = bs.query_growth_data(code=code, year=2023, quarter=4)
    df = rs.get_data()
    if not df.empty:
        growth_data.append(df.iloc[0])

growth_df = pd.DataFrame(growth_data)
# View revenue growth rate and net profit growth rate
print(growth_df[["code", "YOYEquity", "YOYAsset", "YOYNI"]])

bs.logout()
```

### Full Example: Simple Backtesting Framework

```python
import baostock as bs
import pandas as pd
import numpy as np

bs.login()

# Get Ping An Bank 2023 daily K-line data (forward adjusted)
rs = bs.query_history_k_data_plus(
    "sz.000001",
    "date,open,high,low,close,volume",
    start_date="2023-01-01",
    end_date="2023-12-31",
    frequency="d",
    adjustflag="1"
)
df = rs.get_data()
for col in ["open", "high", "low", "close", "volume"]:
    df[col] = df[col].astype(float)

# Dual moving average strategy backtest
df["MA5"] = df["close"].rolling(5).mean()
df["MA20"] = df["close"].rolling(20).mean()

initial_cash = 100000  # Initial capital: 100,000
cash = initial_cash
shares = 0             # Shares held
trades = []            # Trade log

for i in range(20, len(df)):
    # Golden cross buy signal
    if df["MA5"].iloc[i] > df["MA20"].iloc[i] and df["MA5"].iloc[i-1] <= df["MA20"].iloc[i-1]:
        if cash > 0:
            buy_price = df["close"].iloc[i]
            shares = int(cash / buy_price / 100) * 100  # Round down to lots (100 shares)
            cost = shares * buy_price
            cash -= cost
            trades.append({"date": df["date"].iloc[i], "action": "BUY",
                          "price": buy_price, "shares": shares, "cash": cash})

    # Death cross sell signal
    elif df["MA5"].iloc[i] < df["MA20"].iloc[i] and df["MA5"].iloc[i-1] >= df["MA20"].iloc[i-1]:
        if shares > 0:
            sell_price = df["close"].iloc[i]
            cash += shares * sell_price
            trades.append({"date": df["date"].iloc[i], "action": "SELL",
                          "price": sell_price, "shares": shares, "cash": cash})
            shares = 0

# Calculate final returns
final_value = cash + shares * df["close"].iloc[-1]
total_return = (final_value - initial_cash) / initial_cash * 100

print(f"Initial capital: {initial_cash:.2f}")
print(f"Final portfolio value: {final_value:.2f}")
print(f"Total return: {total_return:.2f}%")
print(f"Number of trades: {len(trades)}")
for t in trades:
    print(f"  {t['date']} {t['action']} {t['shares']} shares @ {t['price']:.2f}")

bs.logout()
```

---

## 社区与支持

由 **大佬量化 (Boss Quant)** 维护 — 量化交易教学与策略研发团队。

微信客服: **bossquant1** · [Bilibili](https://space.bilibili.com/48693330) · 搜索 **大佬量化** on 微信公众号 / Bilibili / 抖音
