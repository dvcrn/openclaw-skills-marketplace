---
name: tqsdk
description: "TqSdk — open-source Python SDK for futures/options trading by Shinny Tech, providing real-time quotes, backtesting, and live trading."
homepage: https://github.com/shinnytech/tqsdk-python
---

# TqSdk (Tianqin Quantitative SDK)

[TqSdk](https://github.com/shinnytech/tqsdk-python) is an open-source Python SDK by Shinny Tech for futures and options quantitative trading. It provides real-time market data, historical data, backtesting, and live trading through a unified async API.

> Docs: https://doc.shinnytech.com/tqsdk/latest/
> Free tier available (delayed quotes). Pro version for real-time data.

## Installation

```bash
pip install tqsdk
```

## Quick Start

```python
from tqsdk import TqApi, TqAuth, TqBacktest
from datetime import date

# Live mode (free account with delayed quotes)
api = TqApi(auth=TqAuth("your_username", "your_password"))

# Get real-time quote
quote = api.get_quote("SHFE.cu2401")  # Shanghai copper futures
print(f"Last price: {quote.last_price}, Volume: {quote.volume}")

# Get K-line data
klines = api.get_kline_serial("SHFE.cu2401", duration_seconds=60)  # 1-min bars
print(klines.tail())

# Close API
api.close()
```

## Symbol Format

```
EXCHANGE.CONTRACT
```

| Exchange | Code | Example |
|---|---|---|
| Shanghai Futures (SHFE) | `SHFE` | `SHFE.cu2401` (Copper) |
| Dalian Commodity (DCE) | `DCE` | `DCE.m2405` (Soybean meal) |
| Zhengzhou Commodity (CZCE) | `CZCE` | `CZCE.CF405` (Cotton) |
| CFFEX (Financial) | `CFFEX` | `CFFEX.IF2401` (CSI 300 futures) |
| Shanghai Energy (INE) | `INE` | `INE.sc2407` (Crude oil) |
| Guangzhou Futures (GFEX) | `GFEX` | `GFEX.si2407` (Industrial silicon) |
| SSE Options | `SSE` | `SSE.10004816` (50ETF option) |
| SZSE Options | `SZSE` | `SZSE.90000001` (300ETF option) |

---

## Market Data

### Real-time Quotes

```python
from tqsdk import TqApi, TqAuth

api = TqApi(auth=TqAuth("user", "pass"))

quote = api.get_quote("CFFEX.IF2401")
# Key fields:
# quote.last_price      — Last traded price
# quote.bid_price1      — Best bid price
# quote.ask_price1      — Best ask price
# quote.bid_volume1     — Best bid volume
# quote.ask_volume1     — Best ask volume
# quote.highest         — Day high
# quote.lowest          — Day low
# quote.open            — Open price
# quote.close           — Previous close
# quote.volume          — Total volume
# quote.amount          — Total turnover
# quote.open_interest   — Open interest
# quote.upper_limit     — Upper price limit
# quote.lower_limit     — Lower price limit
# quote.pre_settlement  — Previous settlement price
# quote.settlement      — Today's settlement price

# Wait for quote update
while True:
    api.wait_update()
    if api.is_changing(quote, "last_price"):
        print(f"Price update: {quote.last_price}")
```

### K-line Data

```python
# Get K-line series (returns pandas DataFrame)
klines = api.get_kline_serial(
    "SHFE.cu2401",
    duration_seconds=60,     # Bar duration: 60=1min, 300=5min, 3600=1hour, 86400=daily
    data_length=200          # Number of bars to fetch
)
# Columns: datetime, open, high, low, close, volume, open_oi, close_oi

# Multiple durations
klines_1m = api.get_kline_serial("SHFE.cu2401", 60)
klines_5m = api.get_kline_serial("SHFE.cu2401", 300)
klines_1d = api.get_kline_serial("SHFE.cu2401", 86400)
```

### Tick Data

```python
ticks = api.get_tick_serial("SHFE.cu2401", data_length=500)
# Columns: datetime, last_price, highest, lowest, bid_price1, ask_price1,
#          bid_volume1, ask_volume1, volume, amount, open_interest
```

---

## Trading

### Place Orders

```python
from tqsdk import TqApi, TqAuth

api = TqApi(auth=TqAuth("user", "pass"))

# Limit order — buy open 2 lots
order = api.insert_order(
    symbol="SHFE.cu2401",
    direction="BUY",           # "BUY" or "SELL"
    offset="OPEN",             # "OPEN", "CLOSE", "CLOSETODAY"
    volume=2,                  # Number of lots
    limit_price=68000.0        # Limit price (None for market order)
)

# Market order (FAK — Fill and Kill)
order = api.insert_order(
    symbol="SHFE.cu2401",
    direction="BUY",
    offset="OPEN",
    volume=2
)

# Cancel order
api.cancel_order(order)

# Check order status
while True:
    api.wait_update()
    if order.status == "FINISHED":
        print(f"Order finished: filled={order.volume_orign - order.volume_left}")
        break
```

### Position & Account

```python
# Get account info
account = api.get_account()
# account.balance        — Account balance
# account.available      — Available funds
# account.margin         — Used margin
# account.float_profit   — Floating PnL
# account.position_profit — Position PnL
# account.commission     — Today's commission

# Get position
position = api.get_position("SHFE.cu2401")
# position.pos_long      — Long position volume
# position.pos_short     — Short position volume
# position.pos_long_today — Today's long position
# position.float_profit_long  — Long floating PnL
# position.float_profit_short — Short floating PnL
# position.open_price_long    — Long average open price
# position.open_price_short   — Short average open price
```

---

## Backtesting

```python
from tqsdk import TqApi, TqAuth, TqBacktest, TqSim
from datetime import date

# Create backtest API
api = TqApi(
    backtest=TqBacktest(
        start_dt=date(2024, 1, 1),
        end_dt=date(2024, 6, 30)
    ),
    account=TqSim(init_balance=1000000),  # Simulated account with 1M initial
    auth=TqAuth("user", "pass")
)

# Strategy logic (same code works for live and backtest)
klines = api.get_kline_serial("CFFEX.IF2401", 60 * 60)  # 1-hour bars
position = api.get_position("CFFEX.IF2401")

while True:
    api.wait_update()
    if api.is_changing(klines.iloc[-1], "close"):
        ma5 = klines["close"].iloc[-5:].mean()
        ma20 = klines["close"].iloc[-20:].mean()

        if ma5 > ma20 and position.pos_long == 0:
            api.insert_order("CFFEX.IF2401", "BUY", "OPEN", 1, klines.iloc[-1]["close"])
        elif ma5 < ma20 and position.pos_long > 0:
            api.insert_order("CFFEX.IF2401", "SELL", "CLOSE", 1, klines.iloc[-1]["close"])

api.close()
```

---

## Advanced Examples

### Dual-Contract Spread Trading

```python
from tqsdk import TqApi, TqAuth

api = TqApi(auth=TqAuth("user", "pass"))

quote_near = api.get_quote("SHFE.rb2401")   # Near-month rebar
quote_far = api.get_quote("SHFE.rb2405")    # Far-month rebar
pos_near = api.get_position("SHFE.rb2401")
pos_far = api.get_position("SHFE.rb2405")

SPREAD_OPEN = 100    # Open spread threshold
SPREAD_CLOSE = 20    # Close spread threshold

while True:
    api.wait_update()
    spread = quote_near.last_price - quote_far.last_price

    if spread > SPREAD_OPEN and pos_near.pos_short == 0:
        # Spread too wide: sell near, buy far
        api.insert_order("SHFE.rb2401", "SELL", "OPEN", 1, quote_near.bid_price1)
        api.insert_order("SHFE.rb2405", "BUY", "OPEN", 1, quote_far.ask_price1)
        print(f"Open spread trade: spread={spread:.0f}")

    elif spread < SPREAD_CLOSE and pos_near.pos_short > 0:
        # Spread converged: close both legs
        api.insert_order("SHFE.rb2401", "BUY", "CLOSE", 1, quote_near.ask_price1)
        api.insert_order("SHFE.rb2405", "SELL", "CLOSE", 1, quote_far.bid_price1)
        print(f"Close spread trade: spread={spread:.0f}")
```

### ATR-Based Stop Loss Strategy

```python
from tqsdk import TqApi, TqAuth
import numpy as np

api = TqApi(auth=TqAuth("user", "pass"))

symbol = "CFFEX.IF2401"
klines = api.get_kline_serial(symbol, 86400, data_length=50)  # Daily bars
position = api.get_position(symbol)

ATR_PERIOD = 14
ATR_MULTIPLIER = 2.0
entry_price = 0.0

while True:
    api.wait_update()
    if not api.is_changing(klines.iloc[-1], "close"):
        continue

    # Calculate ATR
    highs = klines["high"].iloc[-ATR_PERIOD-1:]
    lows = klines["low"].iloc[-ATR_PERIOD-1:]
    closes = klines["close"].iloc[-ATR_PERIOD-1:]
    tr = np.maximum(highs.values[1:] - lows.values[1:],
                    np.abs(highs.values[1:] - closes.values[:-1]),
                    np.abs(lows.values[1:] - closes.values[:-1]))
    atr = np.mean(tr[-ATR_PERIOD:])

    current_price = klines.iloc[-1]["close"]
    ma20 = klines["close"].iloc[-20:].mean()

    if position.pos_long == 0:
        # Entry: price above 20-day MA
        if current_price > ma20:
            api.insert_order(symbol, "BUY", "OPEN", 1, current_price)
            entry_price = current_price
            print(f"Entry: price={current_price:.2f}, ATR={atr:.2f}")
    else:
        # ATR trailing stop
        stop_price = entry_price - ATR_MULTIPLIER * atr
        if current_price < stop_price:
            api.insert_order(symbol, "SELL", "CLOSE", position.pos_long, current_price)
            print(f"Stop loss: price={current_price:.2f}, stop={stop_price:.2f}")

api.close()
```

---

## Tips

- Free tier provides delayed quotes (15-min delay). Pro version needed for real-time data.
- Same code works for both backtesting and live trading — just change the API initialization.
- `api.wait_update()` is the core event loop — all data updates are received through it.
- Use `api.is_changing()` to check if specific data has been updated.
- Supports both futures and options across all major Chinese exchanges.
- Docs: https://doc.shinnytech.com/tqsdk/latest/

---

## 社区与支持

由 **大佬量化 (Boss Quant)** 维护 — 量化交易教学与策略研发团队。

微信客服: **bossquant1** · [Bilibili](https://space.bilibili.com/48693330) · 搜索 **大佬量化** on 微信公众号 / Bilibili / 抖音
