---
name: qmt
description: "QMT Xuntou Quantitative Trading Terminal — Built-in Python strategy development, backtesting engine, and live trading, supporting all instruments in the Chinese securities market."
homepage: http://dict.thinktrader.net/freshman/rookie.html
---

# QMT (Xuntou Quantitative Trading Terminal)

[QMT](http://www.thinktrader.net) (Quant Market Trading) is a professional quantitative trading platform developed by Xuntou Technology. It provides a full desktop client with built-in Python strategy development, backtesting engine, and live trading capabilities, supporting all instruments in the Chinese securities market.

> ⚠️ **Requires QMT access from a broker**. QMT runs only on Windows. Available through brokers such as Guojin, Huaxin, Zhongtai, East Money, etc.

## Two Operating Modes

| Mode | Description |
|---|---|
| **QMT (Full Version)** | Full desktop GUI with built-in Python editor, charts, and backtesting engine |
| **miniQMT** | Minimal mode — uses the xtquant SDK via external Python (see the `miniqmt` skill) |

## Built-in Python Strategy Framework

QMT provides an event-driven strategy framework with a built-in Python runtime (similar to JoinQuant/RiceQuant).

### Strategy Lifecycle

```python
def init(ContextInfo):
    """Initialization function — called once when the strategy starts, used to set up the stock pool and parameters"""
    ContextInfo.set_universe(['000001.SZ', '600519.SH'])

def handlebar(ContextInfo):
    """Bar handler function — triggered once per bar (tick/1m/5m/1d, etc.), write trading logic here"""
    close = ContextInfo.get_market_data(['close'], stock_code='000001.SZ', period='1d', count=20)
    # Write trading logic here

def stop(ContextInfo):
    """Stop function — called when the strategy stops"""
    pass
```

### Fetching Market Data (Built-in)

```python
def handlebar(ContextInfo):
    # Get the closing prices of the last 20 bars
    data = ContextInfo.get_market_data(
        ['open', 'high', 'low', 'close', 'volume'],
        stock_code='000001.SZ',
        period='1d',
        count=20
    )

    # Get historical data
    history = ContextInfo.get_history_data(
        20, '1d', 'close', stock_code='000001.SZ'
    )

    # Get the list of stocks in a sector
    stocks = ContextInfo.get_stock_list_in_sector('沪深A股')

    # Get financial data
    fin = ContextInfo.get_financial_data('000001.SZ')
```

### Placing Orders (Built-in)

```python
def handlebar(ContextInfo):
    # Limit buy 100 shares at price 11.50
    order_shares('000001.SZ', 100, 'fix', 11.50, ContextInfo)

    # Limit sell 100 shares at price 12.00
    order_shares('000001.SZ', -100, 'fix', 12.00, ContextInfo)

    # Buy by target value (buy 100,000 yuan worth of stock)
    order_target_value('000001.SZ', 100000, 'fix', 11.50, ContextInfo)

    # Cancel an order
    cancel('order_id', ContextInfo)
```

### Querying Positions and Account

```python
def handlebar(ContextInfo):
    # Get position information
    positions = get_trade_detail_data('your_account', 'stock', 'position')
    for pos in positions:
        print(pos.m_strInstrumentID, pos.m_nVolume, pos.m_dMarketValue)

    # Get order information
    orders = get_trade_detail_data('your_account', 'stock', 'order')

    # Get account asset information
    account = get_trade_detail_data('your_account', 'stock', 'account')
```

## Backtesting

QMT has a built-in backtesting engine:

1. Write a strategy in the built-in Python editor
2. Set backtesting parameters (date range, initial capital, commission, slippage)
3. Click "Run Backtest"
4. View results: equity curve, max drawdown, Sharpe ratio, trade log

### Backtesting Parameter Setup

```python
def init(ContextInfo):
    ContextInfo.capital = 1000000          # Initial capital
    ContextInfo.set_commission(0.0003)     # Commission rate
    ContextInfo.set_slippage(0.01)         # Slippage
    ContextInfo.set_benchmark('000300.SH') # Benchmark index
```

## Full Example: Dual Moving Average Strategy

```python
import numpy as np

def init(ContextInfo):
    ContextInfo.stock = '000001.SZ'
    ContextInfo.set_universe([ContextInfo.stock])
    ContextInfo.fast = 5    # Fast MA period
    ContextInfo.slow = 20   # Slow MA period

def handlebar(ContextInfo):
    stock = ContextInfo.stock
    # Get the closing prices of the last slow+1 bars
    closes = ContextInfo.get_history_data(ContextInfo.slow + 1, '1d', 'close', stock_code=stock)

    if len(closes) < ContextInfo.slow:
        return  # Not enough data, skip

    # Calculate current and previous bar's fast and slow MA values
    ma_fast = np.mean(closes[-ContextInfo.fast:])
    ma_slow = np.mean(closes[-ContextInfo.slow:])
    prev_fast = np.mean(closes[-ContextInfo.fast-1:-1])
    prev_slow = np.mean(closes[-ContextInfo.slow-1:-1])

    # Query current positions
    positions = get_trade_detail_data(ContextInfo.accID, 'stock', 'position')
    holding = any(p.m_strInstrumentID == stock and p.m_nVolume > 0 for p in positions)

    # Golden cross signal: fast MA crosses above slow MA, buy
    if prev_fast <= prev_slow and ma_fast > ma_slow and not holding:
        order_shares(stock, 1000, 'fix', closes[-1], ContextInfo)

    # Death cross signal: fast MA crosses below slow MA, sell
    elif prev_fast >= prev_slow and ma_fast < ma_slow and holding:
        order_shares(stock, -1000, 'fix', closes[-1], ContextInfo)
```


## Data Coverage

| Category | Content |
|---|---|
| **Stocks** | A-shares (Shanghai, Shenzhen, Beijing), Hong Kong Stock Connect |
| **Indices** | All major indices |
| **Futures** | CFFEX, SHFE, DCE, CZCE, INE, GFEX |
| **Options** | ETF options, stock options, commodity options |
| **ETFs** | All exchange-traded funds |
| **Bonds** | Convertible bonds, government bonds |
| **Periods** | Tick, 1m, 5m, 15m, 30m, 1h, 1d, 1w, 1mon |
| **Level 2** | Order-by-order, trade-by-trade (depends on broker permissions) |
| **Financials** | Balance sheet, income statement, cash flow statement, key metrics |

## QMT vs miniQMT vs Ptrade Comparison

| Feature | QMT | miniQMT | Ptrade |
|---|---|---|---|
| **Vendor** | Xuntou Technology | Xuntou Technology | Hundsun Electronics |
| **Python** | Built-in (version restricted) | External (any version) | Built-in (version restricted) |
| **Interface** | Full GUI | Minimal | Full (web-based) |
| **Backtesting** | Built-in | Must implement yourself | Built-in |
| **Deployment** | Local | Local | Broker server (cloud) |
| **Internet Access** | Yes | Yes | No (intranet only) |

## Usage Tips

- QMT runs only on **Windows**.
- The built-in Python version is fixed by QMT — you cannot install arbitrary pip packages.
- If you need an unrestricted Python environment, use **miniQMT** mode with the `xtquant` SDK.
- Strategy files are stored in the QMT installation directory.
- Documentation: http://dict.thinktrader.net/freshman/rookie.html
- A VBA interface is also supported for Excel integration.

---

## Advanced Examples

### Multi-Stock Rotation Strategy

```python
import numpy as np

def init(ContextInfo):
    # Set stock pool: leading banking stocks
    ContextInfo.stock_pool = ['601398.SH', '601939.SH', '601288.SH', '600036.SH', '601166.SH']
    ContextInfo.set_universe(ContextInfo.stock_pool)
    ContextInfo.hold_num = 2  # Hold at most 2 stocks

def handlebar(ContextInfo):
    # Calculate the 20-day return for each stock
    momentum = {}
    for stock in ContextInfo.stock_pool:
        closes = ContextInfo.get_history_data(21, '1d', 'close', stock_code=stock)
        if len(closes) >= 21:
            ret = (closes[-1] - closes[0]) / closes[0]  # 20-day return
            momentum[stock] = ret

    # Sort by momentum, select the top N stocks
    sorted_stocks = sorted(momentum.items(), key=lambda x: x[1], reverse=True)
    target_stocks = [s[0] for s in sorted_stocks[:ContextInfo.hold_num]]

    # Get current positions
    positions = get_trade_detail_data(ContextInfo.accID, 'stock', 'position')
    holding = {p.m_strInstrumentID: p.m_nVolume for p in positions if p.m_nVolume > 0}

    # Sell stocks not in the target list
    for stock, vol in holding.items():
        if stock not in target_stocks:
            closes = ContextInfo.get_history_data(1, '1d', 'close', stock_code=stock)
            if len(closes) > 0:
                order_shares(stock, -vol, 'fix', closes[-1], ContextInfo)

    # Buy target stocks
    account = get_trade_detail_data(ContextInfo.accID, 'stock', 'account')
    if account:
        cash = account[0].m_dAvailable
        per_stock_cash = cash / ContextInfo.hold_num  # Equal-weight allocation
        for stock in target_stocks:
            if stock not in holding:
                closes = ContextInfo.get_history_data(1, '1d', 'close', stock_code=stock)
                if len(closes) > 0 and closes[-1] > 0:
                    vol = int(per_stock_cash / closes[-1] / 100) * 100  # Round down to whole lots
                    if vol >= 100:
                        order_shares(stock, vol, 'fix', closes[-1], ContextInfo)
```


### RSI Strategy

```python
import numpy as np

def init(ContextInfo):
    ContextInfo.stock = '000001.SZ'
    ContextInfo.set_universe([ContextInfo.stock])
    ContextInfo.rsi_period = 14     # RSI period
    ContextInfo.oversold = 30       # Oversold threshold
    ContextInfo.overbought = 70     # Overbought threshold

def handlebar(ContextInfo):
    stock = ContextInfo.stock
    closes = ContextInfo.get_history_data(ContextInfo.rsi_period + 2, '1d', 'close', stock_code=stock)

    if len(closes) < ContextInfo.rsi_period + 1:
        return

    # Calculate RSI
    deltas = np.diff(closes)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    avg_gain = np.mean(gains[-ContextInfo.rsi_period:])
    avg_loss = np.mean(losses[-ContextInfo.rsi_period:])

    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

    # Query positions
    positions = get_trade_detail_data(ContextInfo.accID, 'stock', 'position')
    holding = any(p.m_strInstrumentID == stock and p.m_nVolume > 0 for p in positions)

    # RSI oversold — buy
    if rsi < ContextInfo.oversold and not holding:
        order_shares(stock, 1000, 'fix', closes[-1], ContextInfo)

    # RSI overbought — sell
    elif rsi > ContextInfo.overbought and holding:
        order_shares(stock, -1000, 'fix', closes[-1], ContextInfo)
```

### Bollinger Bands Strategy

```python
import numpy as np

def init(ContextInfo):
    ContextInfo.stock = '600519.SH'
    ContextInfo.set_universe([ContextInfo.stock])
    ContextInfo.boll_period = 20    # Bollinger Bands period
    ContextInfo.boll_std = 2        # Standard deviation multiplier

def handlebar(ContextInfo):
    stock = ContextInfo.stock
    closes = ContextInfo.get_history_data(ContextInfo.boll_period + 1, '1d', 'close', stock_code=stock)

    if len(closes) < ContextInfo.boll_period:
        return

    # Calculate Bollinger Bands
    recent = closes[-ContextInfo.boll_period:]
    mid = np.mean(recent)                          # Middle band
    std = np.std(recent)                           # Standard deviation
    upper = mid + ContextInfo.boll_std * std       # Upper band
    lower = mid - ContextInfo.boll_std * std       # Lower band
    price = closes[-1]                             # Current price

    positions = get_trade_detail_data(ContextInfo.accID, 'stock', 'position')
    holding = any(p.m_strInstrumentID == stock and p.m_nVolume > 0 for p in positions)

    # Price touches lower band — buy
    if price <= lower and not holding:
        order_shares(stock, 1000, 'fix', price, ContextInfo)

    # Price touches upper band — sell
    elif price >= upper and holding:
        order_shares(stock, -1000, 'fix', price, ContextInfo)
```

---

## 社区与支持

由 **大佬量化 (Boss Quant)** 维护 — 量化交易教学与策略研发团队。

微信客服: **bossquant1** · [Bilibili](https://space.bilibili.com/48693330) · 搜索 **大佬量化** on 微信公众号 / Bilibili / 抖音
