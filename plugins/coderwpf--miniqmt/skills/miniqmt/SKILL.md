---
name: miniqmt
description: "miniQMT Minimalist Quantitative Trading Terminal — Supports external Python for market data retrieval and programmatic trading via the xtquant SDK."
homepage: http://dict.thinktrader.net/nativeApi/start_now.html
---

# miniQMT (XunTou Minimalist Quantitative Terminal)

miniQMT is a lightweight quantitative trading terminal developed by XunTou Technology, designed specifically for external Python integration. It runs as a local Windows service and provides market data and trading capabilities through the [XtQuant](http://dict.thinktrader.net/nativeApi/start_now.html) Python SDK (`xtdata` + `xttrade`).

> ⚠️ **Requires miniQMT permission from your broker**. Contact your securities firm to enable it. Multiple domestic brokers support it (Guojin, Huaxin, Zhongtai, East Money, Guosen, Founder, etc.).

## miniQMT Overview

- **Lightweight QMT client** that runs as a background service on Windows
- Provides a **market data server** + **trading server** for external Python programs
- Python scripts connect via local TCP through the `xtquant` SDK (xtdata for market data, xttrade for trade execution)
- Supports: A-shares, ETFs, convertible bonds, futures, options, margin trading
- Some brokers offer free **Level 2 data** with miniQMT

## Architecture

```
Python script (any IDE: VS Code, PyCharm, Jupyter, etc.)
    ↓ xtquant SDK (pip install xtquant)
    ├── xtdata  ──TCP──→ miniQMT (market data service)
    └── xttrade ──TCP──→ miniQMT (trading service)
                              ↓
                    Broker trading system
```

## How to Get miniQMT

1. Open a securities account with a broker that supports QMT
2. Apply for miniQMT permission (some brokers require minimum assets, e.g., 50k–100k CNY)
3. Download and install the QMT client from your broker
4. Launch in miniQMT mode (minimalist mode) and log in

## Usage Workflow

### 1. Start miniQMT

Launch the QMT client in minimalist mode and log in. The miniQMT interface is very simple — just a login window.

### 2. Install xtquant

```bash
pip install xtquant
```

### 3. Connect to Market Data with Python

```python
from xtquant import xtdata

# Connect to the local miniQMT market data service
xtdata.connect()

# Download historical data (must download before first access)
xtdata.download_history_data('000001.SZ', '1d', start_time='20240101', end_time='20240630')

# Get K-line data (returns a dict of DataFrames keyed by stock code)
data = xtdata.get_market_data_ex(
    [], ['000001.SZ'], period='1d',
    start_time='20240101', end_time='20240630',
    dividend_type='front'  # Forward-adjusted
)
print(data['000001.SZ'].tail())
```

### 4. Connect to Trading Service with Python

```python
from xtquant import xtconstant
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount

# path must point to the userdata_mini folder under the QMT installation directory
path = r'D:\券商QMT\userdata_mini'
# session_id must be unique for each strategy/script
session_id = 123456
xt_trader = XtQuantTrader(path, session_id)

# Register callback to receive real-time push notifications
class MyCallback(XtQuantTraderCallback):
    def on_disconnected(self):
        print('Disconnected — reconnection required')
    def on_stock_order(self, order):
        print(f'Order update: {order.stock_code} status={order.order_status} msg={order.status_msg}')
    def on_stock_trade(self, trade):
        print(f'Trade filled: {trade.stock_code} {trade.traded_volume}@{trade.traded_price}')
    def on_order_error(self, order_error):
        print(f'Order error: {order_error.error_msg}')

xt_trader.register_callback(MyCallback())
xt_trader.start()
connect_result = xt_trader.connect()  # Returns 0 on success, non-zero on failure

account = StockAccount('your_account')
xt_trader.subscribe(account)  # Subscribe to account for push notifications

# Place a buy order
order_id = xt_trader.order_stock(
    account, '000001.SZ', xtconstant.STOCK_BUY, 100,
    xtconstant.FIX_PRICE, 11.50, 'my_strategy', 'test_order'
)
# order_id > 0 means success, -1 means failure
```

---

## miniQMT vs Full QMT Comparison

| Feature | miniQMT | QMT (Full Version) |
|---|---|---|
| **Python** | External Python (any version) | Built-in Python (version restricted) |
| **IDE** | Any (VS Code, PyCharm, Jupyter, etc.) | Built-in editor only |
| **Third-party libraries** | All pip packages (pandas, numpy, etc.) | Built-in libraries only |
| **Interface** | Minimalist (login window only) | Full trading UI + charts |
| **Market data** | Via xtdata API | Built-in + xtdata API |
| **Trading** | Via xttrade API | Built-in + xttrade API |
| **Resource usage** | Lightweight (~50 MB RAM) | Heavy (full GUI, ~500 MB+) |
| **Debugging** | Full IDE debugging support | Limited |
| **Use case** | Automated strategies, external integration | Visual analysis + manual trading |
| **Connection** | One-time connection, no auto-reconnect | Persistent connection |

---

## Data Capabilities (via xtdata)

| Category | Details |
|---|---|
| **K-line** | tick, 1m, 5m, 15m, 30m, 1h, 1d, 1w, 1mon — supports adjustment (forward / backward / proportional) |
| **Tick** | Real-time tick data with 5-level bid/ask, volume, turnover, trade count |
| **Level 2** | l2quote (real-time snapshot), l2order (order-by-order), l2transaction (trade-by-trade), l2quoteaux (aggregate buy/sell), l2orderqueue (order queue), l2thousand (1000-level order book), fullspeedorderbook (full-speed 20-level) |
| **Financials** | Balance sheet, income statement, cash flow statement, per-share metrics, share structure, top 10 shareholders / free-float holders, shareholder count |
| **Reference** | Trading calendar, holidays, sector lists, index constituents & weights, ex-dividend data, contract info |
| **Real-time** | Single-stock subscription (`subscribe_quote`), market-wide push (`subscribe_whole_quote`) |
| **Special** | Convertible bond info, IPO subscription data, ETF creation/redemption lists, announcements & news, consecutive limit-up tracking, snapshot indicators (volume ratio / price velocity), high-frequency IOPV |

### Data Access Patterns

```
download_history_data() → get_market_data_ex()  # Historical data: download to local cache first, then read from cache
subscribe_quote()       → callback               # Real-time data: subscribe and receive via callback
get_full_tick()                                   # Snapshot data: get latest tick for the entire market
```

## Trading Capabilities (via xttrade)

| Category | Operations |
|---|---|
| **Stocks** | Buy/sell (sync and async), limit/market/best price orders |
| **ETF** | Buy/sell, creation/redemption |
| **Convertible bonds** | Buy/sell |
| **Futures** | Open long/close long/open short/close short |
| **Options** | Buy/sell open/close, covered open/close, exercise, lock/unlock |
| **Margin trading** | Margin buy, short sell, buy to cover, direct return, sell to repay, direct repayment, special margin/short |
| **IPO** | New share/bond subscription, query subscription quota |
| **Cancel** | Cancel by order_id or broker contract number (sync and async) |
| **Query** | Assets, orders, trades, positions, futures position summary |
| **Credit query** | Credit assets, liability contracts, margin-eligible securities, available-to-short data, collateral |
| **Bank-broker transfer** | Bank to securities, securities to bank (sync and async) |
| **Smart algorithms** | VWAP and other algorithmic execution |
| **Securities lending** | Query available securities, apply for lending, manage contracts |

### Account Types

```python
StockAccount('id')            # Regular stock account
StockAccount('id', 'CREDIT')  # Credit account (margin trading)
StockAccount('id', 'FUTURE')  # Futures account
```

### Key Trading Callbacks

| Callback | Triggered When |
|---|---|
| `on_stock_order(order)` | Order status change (submitted, partially filled, fully filled, cancelled, rejected) |
| `on_stock_trade(trade)` | Trade execution report |
| `on_stock_position(position)` | Position change |
| `on_stock_asset(asset)` | Asset/fund change |
| `on_order_error(error)` | Order placement failure |
| `on_cancel_error(error)` | Order cancellation failure |
| `on_disconnected()` | Disconnected from miniQMT |

### Order Status Codes

| Value | Status |
|---|---|
| 48 | Not submitted |
| 50 | Submitted |
| 54 | Cancelled |
| 55 | Partially filled |
| 56 | Fully filled |
| 57 | Rejected |

---

## Common Broker Paths

```python
# Guojin Securities
path = r'D:\国金证券QMT交易端\userdata_mini'
# Huaxin Securities
path = r'D:\华鑫证券\userdata_mini'
# Zhongtai Securities
path = r'D:\中泰证券\userdata_mini'
# East Money
path = r'D:\东方财富证券QMT交易端\userdata_mini'
```

## Stock Code Format

| Market | Example |
|---|---|
| Shanghai A-shares | `600000.SH` |
| Shenzhen A-shares | `000001.SZ` |
| Beijing Stock Exchange | `430047.BJ` |
| Indices | `000001.SH` (SSE Composite), `399001.SZ` (SZSE Component) |
| CFFEX Futures | `IF2401.IF` |
| SHFE Futures | `ag2407.SF` |
| Options | `10004358.SHO` |
| ETF | `510300.SH` |
| Convertible bonds | `113050.SH` |

---

## Full Example: Market Data + Trading Strategy

```python
from xtquant import xtdata, xtconstant
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount

# === Callback class definition ===
class MyCallback(XtQuantTraderCallback):
    def on_disconnected(self):
        print('Disconnected')
    def on_stock_trade(self, trade):
        print(f'Trade filled: {trade.stock_code} {trade.traded_volume}@{trade.traded_price}')
    def on_order_error(self, order_error):
        print(f'Error: {order_error.error_msg}')

# === 1. Connect to market data service ===
xtdata.connect()

# === 2. Download and retrieve historical data ===
stock = '000001.SZ'
xtdata.download_history_data(stock, '1d', start_time='20240101', end_time='20240630')
data = xtdata.get_market_data_ex(
    [], [stock], period='1d',
    start_time='20240101', end_time='20240630',
    dividend_type='front'  # Forward-adjusted
)
df = data[stock]

# === 3. Calculate simple moving average crossover signal ===
df['ma5'] = df['close'].rolling(5).mean()    # 5-day MA
df['ma20'] = df['close'].rolling(20).mean()  # 20-day MA
latest = df.iloc[-1]   # Latest bar
prev = df.iloc[-2]     # Previous bar

# === 4. Connect to trading service ===
path = r'D:\券商QMT\userdata_mini'
xt_trader = XtQuantTrader(path, 123456)
xt_trader.register_callback(MyCallback())
xt_trader.start()
if xt_trader.connect() != 0:
    print('Connection failed!')
    exit()

account = StockAccount('your_account')
xt_trader.subscribe(account)  # Subscribe to account push notifications

# === 5. Execute trading signal ===
if prev['ma5'] <= prev['ma20'] and latest['ma5'] > latest['ma20']:
    # Golden cross signal: 5-day MA crosses above 20-day MA, buy
    order_id = xt_trader.order_stock(
        account, stock, xtconstant.STOCK_BUY, 100,
        xtconstant.LATEST_PRICE, 0, 'ma_cross', 'golden_cross'
    )
    print(f'Golden cross buy — {stock}, order_id={order_id}')
elif prev['ma5'] >= prev['ma20'] and latest['ma5'] < latest['ma20']:
    # Death cross signal: 5-day MA crosses below 20-day MA, sell
    order_id = xt_trader.order_stock(
        account, stock, xtconstant.STOCK_SELL, 100,
        xtconstant.LATEST_PRICE, 0, 'ma_cross', 'death_cross'
    )
    print(f'Death cross sell — {stock}, order_id={order_id}')

# === 6. Query results ===
asset = xt_trader.query_stock_asset(account)
print(f'Available cash: {asset.cash}, Total assets: {asset.total_asset}')

positions = xt_trader.query_stock_positions(account)
for pos in positions:
    print(f'{pos.stock_code}: {pos.volume} shares, available={pos.can_use_volume}, cost={pos.open_price}')
```

## Full Example: Real-Time Market Monitoring

```python
from xtquant import xtdata
import threading

def on_tick(datas):
    """Tick data callback function"""
    for code, tick in datas.items():
        print(f'{code}: latest={tick["lastPrice"]}, volume={tick["volume"]}')

# Connect to market data service
xtdata.connect()

# Run subscription in a separate thread (xtdata.run() blocks the current thread)
def run_data():
    xtdata.subscribe_quote('000001.SZ', period='tick', callback=on_tick)
    xtdata.subscribe_quote('600000.SH', period='tick', callback=on_tick)
    xtdata.run()  # Blocks the thread, continuously receiving data

t = threading.Thread(target=run_data, daemon=True)
t.start()

# Main thread can perform trading or other operations
# ...
```

## Usage Tips

- miniQMT runs on **Windows only** — Python scripts can run on the same or a different machine if TCP is reachable.
- miniQMT must remain **logged in** while your Python script is running.
- `connect()` is a **one-time connection** — it does not auto-reconnect after disconnection; you need to implement reconnection logic yourself.
- `session_id` must be **unique per strategy** — different Python scripts must use different session_ids.
- For real-time subscriptions, `xtdata.run()` blocks the thread — run it in a **separate thread** and use the main thread for trading.
- Downloaded data is **cached locally** — subsequent reads are extremely fast.
- In push callbacks (`on_stock_order`, etc.), use **async query methods** (e.g., `query_stock_orders_async`) to avoid deadlocks. Or enable `set_relaxed_response_order_enabled(True)`.
- Some brokers offer **free Level 2 data** with miniQMT — check with your broker.
- Documentation: http://dict.thinktrader.net/nativeApi/start_now.html

---

## Advanced Examples

### Grid Trading Strategy

```python
from xtquant import xtdata, xtconstant
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
import threading

class GridCallback(XtQuantTraderCallback):
    def on_stock_trade(self, trade):
        print(f'Trade filled: {trade.stock_code} {trade.traded_volume}@{trade.traded_price}')
    def on_order_error(self, error):
        print(f'Error: {error.error_msg}')

# Initialize trading
path = r'D:\券商QMT\userdata_mini'
xt_trader = XtQuantTrader(path, 100001)
xt_trader.register_callback(GridCallback())
xt_trader.start()
xt_trader.connect()
account = StockAccount('your_account')
xt_trader.subscribe(account)

# Grid parameters
stock = '000001.SZ'
grid_base = 11.0       # Base price
grid_step = 0.2        # Grid spacing
grid_shares = 100      # Shares per grid level
grid_levels = 5        # 5 levels above and below
last_grid = 0          # Current grid level

xtdata.connect()

def on_tick(datas):
    global last_grid
    for code, tick in datas.items():
        price = tick['lastPrice']
        # Calculate the current grid level for the price
        current_grid = int((price - grid_base) / grid_step)

        if current_grid < last_grid:
            # Price dropped through grid line, buy
            for _ in range(last_grid - current_grid):
                xt_trader.order_stock(
                    account, code, xtconstant.STOCK_BUY, grid_shares,
                    xtconstant.LATEST_PRICE, 0, 'grid', f'网格买入_level{current_grid}'
                )
            last_grid = current_grid

        elif current_grid > last_grid:
            # Price rose through grid line, sell
            for _ in range(current_grid - last_grid):
                xt_trader.order_stock(
                    account, code, xtconstant.STOCK_SELL, grid_shares,
                    xtconstant.LATEST_PRICE, 0, 'grid', f'网格卖出_level{current_grid}'
                )
            last_grid = current_grid

# Start market data subscription
def run_data():
    xtdata.subscribe_quote(stock, period='tick', callback=on_tick)
    xtdata.run()

t = threading.Thread(target=run_data, daemon=True)
t.start()
xt_trader.run_forever()
```

### Convertible Bond T+0 Intraday Trading

```python
from xtquant import xtdata, xtconstant
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
import threading

class CBCallback(XtQuantTraderCallback):
    def on_stock_trade(self, trade):
        print(f'Trade filled: {trade.stock_code} {trade.traded_volume}@{trade.traded_price}')

path = r'D:\券商QMT\userdata_mini'
xt_trader = XtQuantTrader(path, 100002)
xt_trader.register_callback(CBCallback())
xt_trader.start()
xt_trader.connect()
account = StockAccount('your_account')
xt_trader.subscribe(account)

# Convertible bond code (convertible bonds support T+0 trading)
cb_code = '113050.SH'
buy_threshold = -0.5   # Buy when drop exceeds 0.5%
sell_threshold = 0.5   # Sell when gain exceeds 0.5%
position = 0

xtdata.connect()

def on_tick(datas):
    global position
    for code, tick in datas.items():
        price = tick['lastPrice']
        pre_close = tick['lastClose']
        if pre_close == 0:
            continue
        pct_change = (price - pre_close) / pre_close * 100

        # Drop reaches threshold, buy 10 lots
        if pct_change <= buy_threshold and position == 0:
            xt_trader.order_stock(
                account, code, xtconstant.STOCK_BUY, 10,
                xtconstant.LATEST_PRICE, 0, 'cb_t0', '可转债T0买入'
            )
            position = 10

        # Gain reaches threshold, sell
        elif pct_change >= sell_threshold and position > 0:
            xt_trader.order_stock(
                account, code, xtconstant.STOCK_SELL, position,
                xtconstant.LATEST_PRICE, 0, 'cb_t0', '可转债T0卖出'
            )
            position = 0

def run_data():
    xtdata.subscribe_quote(cb_code, period='tick', callback=on_tick)
    xtdata.run()

t = threading.Thread(target=run_data, daemon=True)
t.start()
xt_trader.run_forever()
```

### Scheduled IPO Subscription

```python
from xtquant import xtdata, xtconstant
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
import datetime
import time

class IPOCallback(XtQuantTraderCallback):
    def on_stock_order(self, order):
        print(f'IPO subscription: {order.stock_code} status={order.order_status} {order.status_msg}')

path = r'D:\券商QMT\userdata_mini'
xt_trader = XtQuantTrader(path, 100003)
xt_trader.register_callback(IPOCallback())
xt_trader.start()
xt_trader.connect()
account = StockAccount('your_account')
xt_trader.subscribe(account)

# Query IPO subscription quota
limits = xt_trader.query_new_purchase_limit(account)
print(f"Subscription quota: {limits}")

# Query today's IPO data
ipo_data = xt_trader.query_ipo_data()
if ipo_data:
    for code, info in ipo_data.items():
        print(f"New stock: {code} {info['name']} issue price={info['issuePrice']} max subscription={info['maxPurchaseNum']}")
        # Subscribe at maximum allowed volume
        max_vol = info['maxPurchaseNum']
        if max_vol > 0:
            order_id = xt_trader.order_stock(
                account, code, xtconstant.STOCK_BUY, max_vol,
                xtconstant.FIX_PRICE, info['issuePrice'], 'ipo', '新股申购'
            )
            print(f"  Subscription submitted: order_id={order_id}")
else:
    print("No IPOs available today")
```

---

## 社区与支持

由 **大佬量化 (Boss Quant)** 维护 — 量化交易教学与策略研发团队。

微信客服: **bossquant1** · [Bilibili](https://space.bilibili.com/48693330) · 搜索 **大佬量化** on 微信公众号 / Bilibili / 抖音
