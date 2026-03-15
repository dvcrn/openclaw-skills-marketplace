---
name: ptrade
description: "Ptrade Hundsun Quantitative Trading Platform — Strategies run on broker servers with low-latency execution, supporting A-shares, futures, margin trading, and other China securities markets."
homepage: https://ptradeapi.com
---

# Ptrade (Hundsun Quantitative Trading Platform)

[Ptrade](https://ptradeapi.com) is a professional quantitative trading platform developed by Hundsun Electronics. Strategies run on **broker servers** (intranet) for low-latency execution. It uses an event-driven Python strategy framework.

> ⚠️ **Requires broker Ptrade access authorization**. Strategies run on the broker's cloud — no external network access. Cannot install pip packages; only built-in third-party libraries are available.

## Supported Markets & Business Types

**Backtesting support:**
1. Regular stock trading (unit: shares)
2. Convertible bond trading (unit: lots, T+0)
3. Margin trading collateral buy/sell (unit: shares)
4. Futures speculative trading (unit: contracts, T+0)
5. LOF fund trading (unit: shares)
6. ETF fund trading (unit: shares)

**Live trading support:**
1. Regular stock trading (unit: shares)
2. Convertible bond trading (T+0)
3. Margin trading (unit: shares)
4. ETF creation/redemption, arbitrage (unit: shares)
5. Treasury reverse repo (unit: shares)
6. Futures speculative trading (unit: contracts, T+0)
7. ETF fund trading (unit: shares)

**Level2 10-level market data supported by default**. Some brokers provide free L2 tick-by-tick data.

### Price Precision Rules

| Asset Type | Minimum Tick | Decimal Places |
|---|---|---|
| Stocks | 0.01 | 2 |
| Convertible Bonds | 0.001 | 3 |
| LOF / ETF | 0.001 | 3 |
| Treasury Reverse Repo | 0.005 | 3 |
| Stock Index Futures | 0.2 | 1 |
| Treasury Bond Futures | 0.005 | 3 |
| ETF Options | 0.0001 | 4 |

> ⚠️ When placing orders with `limit_price`, the price must conform to the correct decimal precision, otherwise the order will be rejected.

## Stock Code Format

- Shanghai: `600570.SS`
- Shenzhen: `000001.SZ`
- Index: `000300.SS` (CSI 300)

---

## Strategy Lifecycle (Event-Driven)

```python
def initialize(context):
    """Required — Called once at startup. Used to set stock pool, benchmark, and scheduled tasks."""
    g.security = '600570.SS'
    set_universe(g.security)

def before_trading_start(context, data):
    """Optional — Called before market open.
    Backtest mode: Executes at 8:30 each trading day.
    Live mode: Executes immediately on first start, then at 9:10 daily (default, broker-configurable)."""
    log.info('Pre-market preparation')

def handle_data(context, data):
    """Required — Triggered on each bar.
    Daily mode: Executes once at 14:50 daily (default).
    Minute mode: Executes at each minute bar close.
    data[sid] provides: open, high, low, close, price, volume, money."""
    current_price = data[g.security]['close']
    cash = context.portfolio.cash

def after_trading_end(context, data):
    """Optional — Called at 15:30 after market close."""
    log.info('Trading day ended')

def tick_data(context, data):
    """Optional — Triggered every 3 seconds during market hours (9:30-14:59, live only).
    Must use order_tick() to place orders in this function.
    data format: {stock_code: {'order': DataFrame/None, 'tick': DataFrame, 'transcation': DataFrame/None}}"""
    for stock, d in data.items():
        tick = d['tick']
        price = tick['last_px']           # Latest price
        bid1 = tick['bid_grp'][1]         # Best bid [price, volume, count]
        ask1 = tick['offer_grp'][1]       # Best ask [price, volume, count]
        log.info(f'{stock}: {price}, upper_limit={tick["up_px"]}, lower_limit={tick["down_px"]}')
        # Level2 fields (requires L2 access, otherwise None):
        order_data = d['order']           # Tick-by-tick orders
        trans_data = d['transcation']     # Tick-by-tick trades

def on_order_response(context, order_list):
    """Optional — Triggered on order status changes (faster than get_orders).
    order_list is a list of dicts containing: entrust_no, stock_code, amount, price,
    business_amount, status, order_id, entrust_type, entrust_prop, error_info, order_time."""
    for o in order_list:
        log.info(f'Order {o["stock_code"]}: status={o["status"]}, filled={o["business_amount"]}/{o["amount"]}')

def on_trade_response(context, trade_list):
    """Optional — Triggered on trade execution (faster than get_trades).
    trade_list is a list of dicts containing: entrust_no, stock_code, business_amount,
    business_price, business_balance, business_id, status, order_id, entrust_bs, business_time.
    Note: status=9 means rejected order."""
    for t in trade_list:
        direction = 'Buy' if t['entrust_bs'] == '1' else 'Sell'
        log.info(f'{direction} {t["stock_code"]}: {t["business_amount"]}@{t["business_price"]}')
```

### Strategy Execution Frequency

| Mode | Frequency | Execution Time |
|---|---|---|
| **Daily** | Once per day | Backtest: 15:00, Live: 14:50 (configurable) |
| **Minute** | Once per minute | At each minute bar close |
| **Tick** | Every 3 seconds | 9:30–14:59, via `tick_data` or `run_interval` |

### Time Reference

| Phase | Time | Available Functions |
|---|---|---|
| **Pre-market** | Before 9:30 | `before_trading_start`, `run_daily(time='09:15')` |
| **Market hours** | 9:30–15:00 | `handle_data`, `run_daily`, `run_interval`, `tick_data` |
| **Post-market** | 15:30 | `after_trading_end`, `run_daily(time='15:10')` |

---

## Initialization Setup Functions (Use Only in initialize)

### Stock Pool & Benchmark

```python
def initialize(context):
    set_universe(['600570.SS', '000001.SZ'])   # Required: Set stock pool
    set_benchmark('000300.SS')                  # Backtest benchmark index
```

### Commission & Slippage (Backtest Only)

```python
def initialize(context):
    # Set commission: buy 0.03%, sell 0.13% (incl. stamp tax), based on trade value, min 5 CNY
    set_commission(PerTrade(buy_cost=0.0003, sell_cost=0.0013, unit='perValue', min_cost=5))
    set_slippage(FixedSlippage(0.02))           # Fixed slippage of 0.02 CNY
    set_volume_ratio(0.025)                     # Max fill ratio of daily volume
    set_limit_mode(0)                           # 0=limit by volume ratio, 1=limit by fixed quantity
```

### Scheduled Tasks

```python
def initialize(context):
    # run_daily: Execute function at specified time each day
    run_daily(context, my_morning_task, time='09:31')
    run_daily(context, my_afternoon_task, time='14:50')

    # run_interval: Execute function every N seconds (live only, min 3 seconds)
    run_interval(context, my_tick_handler, seconds=10)
```

### Strategy Parameters (Configurable from UI)

```python
def initialize(context):
    # Set parameters that can be dynamically modified from the Ptrade UI without code changes
    set_parameters(
        context,
        ma_fast=5,         # Fast moving average period
        ma_slow=20,        # Slow moving average period
        position_ratio=0.95  # Position ratio
    )
```

---

## Data Functions

### get_history — Get Recent N Bars

```python
get_history(count, frequency='1d', field='close', security_list=None, fq=None, include=False, fill='nan', is_dict=False)
```

```python
# Get OHLCV data for the last 20 trading days
df = get_history(20, '1d', ['open', 'high', 'low', 'close', 'volume'], '600570.SS', fq='pre')

# Bar periods: 1m, 5m, 15m, 30m, 60m, 120m, 1d, 1w/weekly, mo/monthly, 1q/quarter, 1y/yearly
# fq adjustment: None (unadjusted), 'pre' (forward-adjusted), 'post' (backward-adjusted), 'dypre' (dynamic forward-adjusted)
# Available fields: open, high, low, close, volume, money, price, is_open, preclose, high_limit, low_limit, unlimited (daily only)
```

### get_price — Query by Date Range

```python
get_price(security, start_date=None, end_date=None, frequency='1d', fields=None, fq=None, count=None, is_dict=False)
```

```python
# Query by date range
df = get_price('600570.SS', start_date='20240101', end_date='20240630', frequency='1d',
               fields=['open', 'high', 'low', 'close', 'volume'])

# Query by count (last N bars)
df = get_price('600570.SS', end_date='20240630', frequency='1d', count=20)

# Multi-stock query
df = get_price(['600570.SS', '000001.SZ'], start_date='20240101', end_date='20240630')

# Minute data query
df = get_price('600570.SS', start_date='2024-06-01 09:30', end_date='2024-06-01 15:00', frequency='5m')
```

> ⚠️ `get_history` and `get_price` cannot be called concurrently from different threads (e.g., when `run_daily` and `handle_data` execute simultaneously).

### get_snapshot — Real-time Market Snapshot (Live Only)

```python
snapshot = get_snapshot('600570.SS')
# Returns a dict with fields:
# last_px (latest price), open_px (open price), high_px (high price), low_px (low price), preclose_px (previous close)
# up_px (upper limit price), down_px (lower limit price), business_amount (total volume), business_balance (total turnover)
# bid_grp (bid levels: {1:[price,volume,count], 2:...}), offer_grp (ask levels)
# pe_rate (dynamic P/E ratio), pb_rate (P/B ratio), turnover_ratio (turnover rate), vol_ratio (volume ratio)
# entrust_rate (order ratio), entrust_diff (order difference), wavg_px (VWAP), px_change_rate (price change %)
# circulation_amount (circulating shares), trade_status (trading status)
# business_amount_in (inner volume), business_amount_out (outer volume)

# Multi-stock query
snapshots = get_snapshot(['600570.SS', '000001.SZ'])
price = snapshots['600570.SS']['last_px']
```

### get_gear_price — Order Book Depth (Live Only)

```python
gear = get_gear_price('600570.SS')
# Returns: {'bid_grp': {1: [price, volume, count], 2: ...}, 'offer_grp': {1: [price, volume, count], 2: ...}}
bid1_price, bid1_vol, bid1_count = gear['bid_grp'][1]   # Best bid
ask1_price, ask1_vol, ask1_count = gear['offer_grp'][1] # Best ask

# Multi-stock query
gears = get_gear_price(['600570.SS', '000001.SZ'])
```

### Level2 Data (Requires L2 Access)

```python
# Tick-by-tick order data
entrust = get_individual_entrust(
    stocks=['600570.SS'],
    data_count=50,       # Max 200 records
    start_pos=0,         # Start position
    search_direction=1,  # 1=forward, 2=backward
    is_dict=False        # True returns dict format (faster)
)
# Fields: business_time (time), hq_px (price), business_amount (volume), order_no (order number),
#         business_direction (direction: 0=sell, 1=buy), trans_kind (type: 1=market, 2=limit, 3=best)

# Tick-by-tick trade data
transaction = get_individual_transaction(
    stocks=['600570.SS'],
    data_count=50,
    is_dict=False
)
# Fields: business_time, hq_px, business_amount, trade_index, business_direction, buy_no, sell_no, trans_flag
```

---

## Stock & Reference Data

### Basic Information

```python
name = get_stock_name('600570.SS')               # Get stock name
info = get_stock_info('600570.SS')                # Get basic information
status = get_stock_status('600570.SS')            # Get status (suspended/limit up/down, etc.)
exrights = get_stock_exrights('600570.SS')        # Get ex-rights/ex-dividend info
blocks = get_stock_blocks('600570.SS')            # Get sector/block membership

stocks = get_index_stocks('000300.SS')            # Get index constituents
stocks = get_industry_stocks('银行')              # Get industry constituents
stocks = get_Ashares()                            # Get all A-share list
etfs = get_etf_list()                             # Get ETF list
```

### Convertible Bond Data

```python
cb_codes = get_cb_list()                          # Get convertible bond code list
cb_info = get_cb_info()                           # Get convertible bond info DataFrame
# Fields: bond_code (bond code), bond_name (bond name), stock_code (underlying stock code), stock_name (underlying stock name),
#         list_date (listing date), premium_rate (premium rate %), convert_date (conversion start date),
#         maturity_date (maturity date), convert_rate (conversion ratio), convert_price (conversion price), convert_value (conversion value)
```

### Financial Data

```python
get_fundamentals(security, table, fields=None, date=None, start_year=None, end_year=None,
                 report_types=None, date_type=None, merge_type=None)
```

```python
# Query by date (returns the latest report data before that date)
df = get_fundamentals('600570.SS', 'balance_statement', 'total_assets', date='20240630')

# Query by year range
df = get_fundamentals('600570.SS', 'income_statement', fields=['revenue', 'net_profit'],
                      start_year='2022', end_year='2024')

# report_types: '1'=Q1 report, '2'=semi-annual, '3'=Q3 report, '4'=annual
# date_type: None=by disclosure date, 1=by accounting period
# merge_type: None=original data (avoids look-ahead bias), 1=latest revised data

# Available tables: balance_statement, income_statement,
#                   cash_flow_statement, valuation, indicator
```

> ⚠️ Rate limit: Max 100 calls per second, max 500 records per call. Add `sleep` for batch queries.

### Trading Calendar

```python
today = get_trading_day()                         # Get current trading day
all_days = get_all_trades_days()                  # Get all trading days list
days = get_trade_days('2024-01-01', '2024-06-30') # Get trading days in range
```

---

## Trading Functions

### order — Buy/Sell by Quantity

```python
order(security, amount, limit_price=None)
# amount: positive=buy, negative=sell
# Returns: order_id (str) or None

order('600570.SS', 100)                           # Buy 100 shares at latest price
order('600570.SS', 100, limit_price=39.0)         # Buy 100 shares at limit price 39.0
order('600570.SS', -500)                          # Sell 500 shares
order('131810.SZ', -10)                           # Treasury reverse repo 1000 CNY (10 lots)
```

### order_target — Adjust to Target Quantity

```python
order_target('600570.SS', 1000)                   # Adjust position to 1000 shares
order_target('600570.SS', 0)                      # Close position
```

### order_value — Buy by Value

```python
order_value('600570.SS', 100000)                  # Buy 100,000 CNY worth of stock
```

### order_target_value — Adjust to Target Value

```python
order_target_value('600570.SS', 200000)           # Adjust position value to 200,000 CNY
```

### order_market — Market Order Types (Live Only)

```python
order_market(security, amount, market_type, limit_price=None)
# market_type:
#   0 = Best counterparty price
#   1 = Best 5 levels fill, remainder to limit (Shanghai only, requires limit_price)
#   2 = Best own-side price
#   3 = Immediate fill, remainder cancel (Shenzhen only)
#   4 = Best 5 levels fill, remainder cancel
#   5 = Fill all or cancel (Shenzhen only)

order_market('600570.SS', 100, 0, limit_price=35.0)    # Shanghai: best counterparty + protective limit
order_market('000001.SZ', 100, 4)                       # Shenzhen: best 5 levels fill, remainder cancel
```

> ⚠️ Shanghai stocks require `limit_price` when using `order_market`. Convertible bonds are not supported.

### order_tick — Tick-Triggered Order (Use Only in tick_data)

```python
def tick_data(context, data):
    order_tick('600570.SS', 100, limit_price=39.0)
```

### cancel_order — Cancel Order

```python
cancel_order(order_id)          # Cancel order
cancel_order_ex(order_id)       # Extended cancel order
```

### IPO Subscription

```python
ipo_stocks_order()              # One-click IPO stock/bond subscription
```

### After-Hours Fixed Price Order

```python
after_trading_order('600570.SS', 100)             # After-hours fixed price order
after_trading_cancel_order(order_id)              # After-hours cancel order
```

### ETF Operations

```python
# ETF constituent basket order
etf_basket_order('510050.SS', 1,
                 price_style='S3',     # B1-B5 (bid levels), S1-S5 (ask levels), 'new' (latest price)
                 position=True,        # Use existing holdings as substitutes
                 info={'600000.SS': {'cash_replace_flag': 1, 'position_replace_flag': 1, 'limit_price': 12}})

# ETF creation/redemption
etf_purchase_redemption('510050.SS', 900000)      # Positive=creation
etf_purchase_redemption('510050.SS', -900000)     # Negative=redemption
```

---

## Query Functions

### Position Query

```python
pos = get_position('600570.SS')
# Position object: amount (holding quantity), cost_basis (cost price), last_sale_price (latest price), sid (security code), ...

positions = get_positions(['600570.SS', '000001.SZ'])  # Query positions for multiple stocks
```

### Order Query

```python
open_orders = get_open_orders()                   # Query unfilled orders
order = get_order(order_id)                       # Query specific order
orders = get_orders()                             # Query all orders today (within strategy)
all_orders = get_all_orders()                     # Query all orders today (including manual)
trades = get_trades()                             # Query today's trades
```

### Account Information (via context)

```python
context.portfolio.cash                            # Available cash
context.portfolio.total_value                     # Total assets (cash + position value)
context.portfolio.positions_value                 # Position market value
context.portfolio.positions                       # Position dict (Position objects)
context.capital_base                              # Initial capital
context.previous_date                             # Previous trading day
context.blotter.current_dt                        # Current datetime
```

---

## Margin Trading

### Trading Operations

```python
margin_trade('600570.SS', 1000, limit_price=39.0) # Collateral buy/sell
margincash_open('600570.SS', 1000, limit_price=39.0)   # Margin buy (borrow cash)
margincash_close('600570.SS', 1000, limit_price=40.0)  # Sell to repay margin loan
margincash_direct_refund(amount=100000)                 # Direct cash repayment
marginsec_open('600570.SS', 1000, limit_price=40.0)    # Short sell (borrow securities)
marginsec_close('600570.SS', 1000, limit_price=39.0)   # Buy to return borrowed securities
marginsec_direct_refund('600570.SS', 1000)              # Direct securities return
```

### Query Operations

```python
cash_stocks = get_margincash_stocks()             # Query margin-eligible stocks (cash borrowing)
sec_stocks = get_marginsec_stocks()               # Query margin-eligible stocks (securities borrowing)
contract = get_margin_contract()                  # Query margin contract
margin_asset = get_margin_assert()                # Query margin account assets
assure_list = get_assure_security_list()           # Query collateral securities list
max_buy = get_margincash_open_amount('600570.SS')  # Query max margin buy quantity
max_sell = get_margincash_close_amount('600570.SS') # Query max sell-to-repay quantity
max_short = get_marginsec_open_amount('600570.SS') # Query max short sell quantity
max_cover = get_marginsec_close_amount('600570.SS') # Query max buy-to-cover quantity
```

---

## Futures Trading

### Trading Operations

```python
buy_open('IF2401.CFX', 1, limit_price=3500.0)     # Long open (buy to open)
sell_close('IF2401.CFX', 1, limit_price=3550.0)   # Long close (sell to close)
sell_open('IF2401.CFX', 1, limit_price=3550.0)    # Short open (sell to open)
buy_close('IF2401.CFX', 1, limit_price=3500.0)    # Short close (buy to close)
```

### Query & Settings (Backtest)

```python
margin_rate = get_margin_rate('IF2401.CFX')       # Query margin rate
instruments = get_instruments('IF2401.CFX')       # Query contract information
set_future_commission(0.000023)                   # Set futures commission (backtest only)
set_margin_rate('IF2401.CFX', 0.15)               # Set margin rate (backtest only)
```

---

## Built-in Technical Indicators

```python
macd = get_MACD('600570.SS', N1=12, N2=26, M=9)  # MACD indicator
kdj = get_KDJ('600570.SS', N=9, M1=3, M2=3)      # KDJ indicator
rsi = get_RSI('600570.SS', N=14)                  # RSI indicator
cci = get_CCI('600570.SS', N=14)                  # CCI indicator
```

---

## Utility Functions

```python
log.info('message')                               # Logging (also log.warn, log.error)
is_trade('600570.SS')                             # Check if tradable
check_limit('600570.SS')                          # Check limit up/down status
freq = get_frequency()                            # Get current strategy execution frequency
```

### Notification Functions

```python
send_email(context, subject='Signal', content='Buy 600570', to_address='you@email.com')
send_qywx(context, msg='Buy signal triggered')   # WeCom (Enterprise WeChat) notification
```

---

## Global Objects & Context

```python
# g — Global object (persisted across bars, auto-serialized)
g.my_var = 100
g.stock_list = ['600570.SS', '000001.SZ']
# Variables prefixed with '__' are private and will not be persisted:
g.__my_class_instance = SomeClass()

# context — Strategy context
context.portfolio.cash              # Available cash
context.portfolio.total_value       # Total assets
context.portfolio.positions_value   # Position market value
context.portfolio.positions         # Position dict (Position objects)
context.capital_base                # Initial capital
context.previous_date               # Previous trading day
context.blotter.current_dt          # Current datetime (datetime.datetime)
```

---

## Persistence Mechanism

Ptrade automatically serializes and saves the `g` object using pickle after `before_trading_start`, `handle_data`, and `after_trading_end` execute. On restart, `initialize` runs first, then persisted data is restored.

Custom persistence example:

```python
import pickle
NOTEBOOK_PATH = get_research_path()

def initialize(context):
    # Try to restore persisted data from file
    try:
        with open(NOTEBOOK_PATH + 'hold_days.pkl', 'rb') as f:
            g.hold_days = pickle.load(f)
    except:
        g.hold_days = {}  # Initialize as empty dict on first run
    g.security = '600570.SS'
    set_universe(g.security)

def handle_data(context, data):
    # ... trading logic ...
    # Save persisted data
    with open(NOTEBOOK_PATH + 'hold_days.pkl', 'wb') as f:
        pickle.dump(g.hold_days, f, -1)
```

> ⚠️ IO objects (open files, class instances) cannot be serialized. Use `g.__private_var` (double underscore prefix) for non-serializable objects.

---

## Strategy Examples

### Example 1: Call Auction Limit-Up Chasing

```python
def initialize(context):
    g.security = '600570.SS'
    set_universe(g.security)
    # Execute call auction function at 9:23 daily
    run_daily(context, aggregate_auction_func, time='9:23')

def aggregate_auction_func(context):
    stock = g.security
    # Get real-time snapshot to check if at limit up
    snapshot = get_snapshot(stock)
    price = snapshot[stock]['last_px']      # Current price
    up_limit = snapshot[stock]['up_px']     # Upper limit price
    if float(price) >= float(up_limit):
        # Price at upper limit, place buy order at limit-up price
        order(g.security, 100, limit_price=up_limit)

def handle_data(context, data):
    pass
```

### Example 2: Tick-Level Moving Average Strategy

```python
def initialize(context):
    g.security = '600570.SS'
    set_universe(g.security)
    # Execute strategy function every 3 seconds
    run_interval(context, func, seconds=3)

def before_trading_start(context, data):
    # Pre-market: get last 10 days' close prices for MA calculation
    history = get_history(10, '1d', 'close', g.security, fq='pre', include=False)
    g.close_array = history['close'].values

def func(context):
    stock = g.security
    # Get latest price
    snapshot = get_snapshot(stock)
    price = snapshot[stock]['last_px']
    # Calculate 5-day and 10-day MAs (using historical data + current price)
    ma5 = (g.close_array[-4:].sum() + price) / 5
    ma10 = (g.close_array[-9:].sum() + price) / 10
    cash = context.portfolio.cash

    if ma5 > ma10:
        # 5-day MA above 10-day MA, buy
        order_value(stock, cash)
        log.info('Buy %s' % stock)
    elif ma5 < ma10 and get_position(stock).amount > 0:
        # 5-day MA below 10-day MA and holding position, sell
        order_target(stock, 0)
        log.info('Sell %s' % stock)

def handle_data(context, data):
    pass
```

### Example 3: Dual Moving Average Strategy

```python
def initialize(context):
    g.security = '600570.SS'
    set_universe(g.security)

def handle_data(context, data):
    security = g.security
    # Get last 20 days' close prices
    df = get_history(20, '1d', 'close', security, fq=None, include=False)
    ma5 = df['close'][-5:].mean()      # 5-day MA
    ma20 = df['close'][-20:].mean()    # 20-day MA
    current_price = data[security]['close']
    cash = context.portfolio.cash
    position = get_position(security)

    # Price breaks above 20-day MA by 1% and no position, buy
    if current_price > 1.01 * ma20 and position.amount == 0:
        order_value(security, cash * 0.95)
        log.info(f'Buy {security}')
    # Price drops below 5-day MA and holding position, sell
    elif current_price < ma5 and position.amount > 0:
        order_target(security, 0)
        log.info(f'Sell {security}')
```

### Example 4: After-Hours Reverse Repo + IPO Subscription

```python
def initialize(context):
    g.security = '131810.SZ'           # Shenzhen 1-day treasury reverse repo
    set_universe(g.security)
    run_daily(context, reverse_repo, time='14:50')    # Execute reverse repo at 14:50 daily
    run_daily(context, ipo_subscribe, time='09:31')   # Execute IPO subscription at 09:31 daily

def reverse_repo(context):
    cash = context.portfolio.cash
    lots = int(cash / 1000) * 10       # Calculate lots (100 CNY per lot)
    if lots >= 10:
        order(g.security, -lots)       # Negative means reverse repo sell
        log.info(f'Reverse repo: {lots} lots')

def ipo_subscribe(context):
    ipo_stocks_order()                 # One-click subscribe to today's IPOs
    log.info('IPO subscription submitted')

def handle_data(context, data):
    pass
```

---

## Order Status Codes

| Status Code | Description |
|---|---|
| 0 | Not submitted |
| 1 | Pending submission |
| 2 | Submitted |
| 5 | Partially filled |
| 6 | Fully filled (backtest) |
| 7 | Partially cancelled |
| 8 | Fully filled (live) |
| 9 | Rejected |
| a | Cancelled |

---

## Usage Tips

- Strategies run on **broker intranet servers** — no external network access, cannot `pip install`.
- Use `g` (global object) to persist variables across functions. Variables prefixed with `__` will not be persisted.
- Built-in third-party libraries include: pandas, numpy, talib, scipy, sklearn, etc.
- `handle_data` execution frequency depends on strategy period setting (tick/1m/5m/1d, etc.).
- Backtest and live trading use the same code — `set_commission`/`set_slippage` only take effect in backtesting.
- Always add exception handling (`try/except`) in trading strategies to prevent unexpected termination.
- `get_history` and `get_price` **cannot be called concurrently from different threads**.
- When using limit orders, ensure price decimal precision matches the asset type.
- When multiple strategies run concurrently, callback events are **independent of each other**.
- Use `get_research_path()` for file I/O (CSV, pickle files).
- Documentation: https://ptradeapi.com
- QMT API Documentation: http://qmt.ptradeapi.com

---

## Advanced Examples

### Tick-Level Volume-Price Strategy — Large Order Tracking

```python
def initialize(context):
    g.security = '600570.SS'
    set_universe(g.security)
    g.big_order_threshold = 500000   # Large order threshold: 500,000 CNY
    g.buy_signal_count = 0           # Large buy order signal count
    g.sell_signal_count = 0          # Large sell order signal count
    g.signal_window = 10             # Signal window (trigger after N accumulated large order signals)

def tick_data(context, data):
    """Triggered every 3 seconds, analyzes tick-by-tick trade data"""
    stock = g.security
    if stock not in data:
        return

    tick = data[stock]['tick']
    trans = data[stock].get('transcation', None)  # Tick-by-tick trades (requires L2 access)

    # Get current price and price change
    last_price = tick['last_px']
    pre_close = tick['preclose_px']
    change_pct = (last_price - pre_close) / pre_close * 100

    if trans is not None and len(trans) > 0:
        # Analyze large orders in tick-by-tick trades
        for _, row in trans.iterrows():
            amount = row['hq_px'] * row['business_amount']  # Trade value
            if amount >= g.big_order_threshold:
                direction = 'Buy' if row['business_direction'] == 1 else 'Sell'
                log.info(f'Large {direction} order: {amount/10000:.1f}0k CNY @ {row["hq_px"]}')
                if row['business_direction'] == 1:
                    g.buy_signal_count += 1
                else:
                    g.sell_signal_count += 1

    # Accumulated large buy signals reach threshold and no position, buy
    position = get_position(stock)
    cash = context.portfolio.cash

    if g.buy_signal_count >= g.signal_window and position.amount == 0:
        order_value(stock, cash * 0.9)
        log.info(f'Large order tracking buy: accumulated {g.buy_signal_count} large buy orders')
        g.buy_signal_count = 0
        g.sell_signal_count = 0

    # Accumulated large sell signals reach threshold and holding position, sell
    elif g.sell_signal_count >= g.signal_window and position.amount > 0:
        order_target(stock, 0)
        log.info(f'Large order tracking sell: accumulated {g.sell_signal_count} large sell orders')
        g.buy_signal_count = 0
        g.sell_signal_count = 0

def handle_data(context, data):
    pass

def after_trading_end(context, data):
    # Reset signal counts after market close each day
    g.buy_signal_count = 0
    g.sell_signal_count = 0
    log.info('Signal counts reset')
```

### ETF Arbitrage Strategy — Premium/Discount Monitoring & Trading

```python
def initialize(context):
    g.etf_code = '510050.SS'       # SSE 50 ETF
    set_universe(g.etf_code)
    g.premium_threshold = 0.005    # Premium threshold 0.5% (short ETF when premium exceeds this)
    g.discount_threshold = -0.005  # Discount threshold -0.5% (long ETF when discount exceeds this)
    g.min_unit = 900000            # ETF minimum creation/redemption unit (shares)
    # Check premium/discount every 10 seconds
    run_interval(context, check_premium, seconds=10)

def check_premium(context):
    """Check ETF premium/discount rate and execute arbitrage"""
    etf = g.etf_code
    snapshot = get_snapshot(etf)
    if etf not in snapshot:
        return

    etf_price = snapshot[etf]['last_px']       # ETF market price
    # Note: Actual IOPV needs to be calculated from ETF creation/redemption list; simplified here
    # In real scenarios, use the iopv field from get_snapshot (if provided by broker)
    nav_estimate = snapshot[etf].get('iopv', etf_price)  # ETF NAV estimate

    if nav_estimate <= 0 or etf_price <= 0:
        return

    # Calculate premium/discount rate
    premium_rate = (etf_price - nav_estimate) / nav_estimate
    log.info(f'ETF price={etf_price:.4f}, NAV={nav_estimate:.4f}, premium/discount={premium_rate*100:.3f}%')

    position = get_position(etf)
    cash = context.portfolio.cash

    if premium_rate > g.premium_threshold:
        # Premium arbitrage: Create ETF → Sell ETF
        # Step 1: Buy constituent basket and create ETF
        if cash > nav_estimate * g.min_unit:
            etf_basket_order(etf, 1, price_style='S1', position=True)
            log.info(f'Premium arbitrage: create ETF basket, premium rate={premium_rate*100:.3f}%')
            # Step 2: Sell ETF (need to wait for creation to complete, sell in next cycle)

    elif premium_rate < g.discount_threshold:
        # Discount arbitrage: Buy ETF → Redeem ETF → Sell constituents
        if cash > etf_price * g.min_unit:
            order(etf, g.min_unit, limit_price=etf_price)
            log.info(f'Discount arbitrage: buy ETF, discount rate={premium_rate*100:.3f}%')
            # Follow-up: Redeem ETF and sell constituent stocks

def handle_data(context, data):
    pass
```

### Convertible Bond T+0 Intraday Trading Strategy

```python
def initialize(context):
    # Convertible bonds support T+0 trading
    g.cb_list = []                  # Convertible bond pool (dynamically updated)
    g.intraday_profit = 0.003      # Intraday target profit 0.3%
    g.stop_loss = -0.005           # Intraday stop loss -0.5%
    g.max_hold_value = 100000      # Max holding value per convertible bond
    set_universe(['110059.SS'])     # Example: SPDB convertible bond
    run_interval(context, intraday_trade, seconds=10)

def before_trading_start(context, data):
    # Pre-market: screen convertible bonds with low premium and active trading
    cb_info = get_cb_info()
    if cb_info is not None and len(cb_info) > 0:
        # Filter: premium rate < 20% and already listed
        filtered = cb_info[cb_info['premium_rate'] < 20]
        g.cb_list = filtered['bond_code'].tolist()[:10]  # Take top 10
        log.info(f'Today\'s CB pool: {len(g.cb_list)} bonds')

def intraday_trade(context):
    """Intraday T+0 trading logic"""
    for cb_code in g.cb_list[:5]:  # Monitor max 5 at a time
        try:
            snapshot = get_snapshot(cb_code)
            if cb_code not in snapshot:
                continue

            price = snapshot[cb_code]['last_px']
            pre_close = snapshot[cb_code]['preclose_px']
            change_pct = (price - pre_close) / pre_close if pre_close > 0 else 0

            position = get_position(cb_code)
            hold_amount = position.amount if position else 0

            if hold_amount > 0:
                # Holding position: check if take-profit or stop-loss triggered
                cost = position.cost_basis
                pnl = (price - cost) / cost if cost > 0 else 0

                if pnl >= g.intraday_profit:
                    # Take profit (convertible bonds are T+0, can sell same day)
                    order_target(cb_code, 0)
                    log.info(f'CB take profit: {cb_code} profit {pnl*100:.2f}%')
                elif pnl <= g.stop_loss:
                    # Stop loss
                    order_target(cb_code, 0)
                    log.info(f'CB stop loss: {cb_code} loss {pnl*100:.2f}%')
            else:
                # No position: look for buy opportunities
                # Simple strategy: buy on small pullback (change between -1% and 0%)
                if -0.01 < change_pct < 0:
                    buy_value = min(g.max_hold_value, context.portfolio.cash * 0.2)
                    if buy_value > 1000:
                        order_value(cb_code, buy_value)
                        log.info(f'CB buy: {cb_code} @ {price:.3f}')
        except Exception as e:
            log.error(f'CB trading error: {cb_code}, {str(e)}')

def handle_data(context, data):
    pass
```

### Scheduled Task Comprehensive Strategy — Pre-Market Selection + Intraday Trading + Post-Market Summary

```python
import pickle

NOTEBOOK_PATH = get_research_path()

def initialize(context):
    g.stock_pool = []              # Today's stock pool
    g.traded_today = False         # Whether traded today
    set_universe(['000300.SS'])    # Benchmark: CSI 300

    # Schedule tasks
    run_daily(context, morning_select, time='09:25')    # Pre-market stock selection
    run_daily(context, morning_trade, time='09:35')     # Opening trade
    run_daily(context, noon_check, time='13:05')        # Midday check
    run_daily(context, afternoon_close, time='14:50')   # End-of-day operations

def morning_select(context):
    """Pre-market stock selection: screen stocks based on previous day's data"""
    # Get CSI 300 constituents
    hs300 = get_index_stocks('000300.SS')

    candidates = []
    for stock in hs300[:50]:  # Process 50 at a time to avoid timeout
        try:
            # Get last 20 days' bars
            df = get_history(20, '1d', ['close', 'volume'], stock, fq='pre', include=False)
            if len(df) < 20:
                continue

            close = df['close'].values
            volume = df['volume'].values

            # Selection criteria:
            # 1. 5-day MA > 20-day MA (uptrend)
            ma5 = close[-5:].mean()
            ma20 = close.mean()
            if ma5 <= ma20:
                continue

            # 2. Recent 5-day volume increase (volume ratio > 1.2)
            vol_5d = volume[-5:].mean()
            vol_20d = volume.mean()
            if vol_5d / vol_20d < 1.2:
                continue

            # 3. Price near 20-day MA (within 5%)
            if abs(close[-1] - ma20) / ma20 > 0.05:
                continue

            candidates.append({
                'stock': stock,
                'ma5': ma5,
                'ma20': ma20,
                'vol_ratio': vol_5d / vol_20d
            })
        except:
            continue

    # Sort by volume ratio, select top 5
    candidates.sort(key=lambda x: x['vol_ratio'], reverse=True)
    g.stock_pool = [c['stock'] for c in candidates[:5]]
    g.traded_today = False
    log.info(f'Pre-market selection complete: {g.stock_pool}')

def morning_trade(context):
    """Opening trade: buy selected stocks"""
    if g.traded_today or not g.stock_pool:
        return

    cash = context.portfolio.cash
    per_stock_value = cash * 0.9 / len(g.stock_pool)  # Equal-weight allocation

    for stock in g.stock_pool:
        try:
            if not is_trade(stock):
                continue
            # Check if at limit up (don't buy at limit up)
            status = check_limit(stock)
            if status == 1:  # Limit up
                continue
            order_value(stock, per_stock_value)
            log.info(f'Buy: {stock}, value={per_stock_value:.0f}')
        except Exception as e:
            log.error(f'Buy error: {stock}, {str(e)}')

    g.traded_today = True

def noon_check(context):
    """Midday check: stop loss and exception handling"""
    positions = context.portfolio.positions
    for stock, pos in positions.items():
        if pos.amount <= 0:
            continue
        # Calculate P&L
        pnl = (pos.last_sale_price - pos.cost_basis) / pos.cost_basis if pos.cost_basis > 0 else 0
        if pnl < -0.03:
            # Loss exceeds 3%, midday stop loss
            order_target(stock, 0)
            log.info(f'Midday stop loss: {stock}, loss={pnl*100:.2f}%')

def afternoon_close(context):
    """End-of-day operations: summarize today's P&L"""
    total_value = context.portfolio.total_value
    cash = context.portfolio.cash
    positions = context.portfolio.positions

    log.info(f'=== End-of-Day Summary ===')
    log.info(f'Total assets: {total_value:.2f}')
    log.info(f'Available cash: {cash:.2f}')
    log.info(f'Number of positions: {len([p for p in positions.values() if p.amount > 0])}')

    for stock, pos in positions.items():
        if pos.amount > 0:
            pnl = (pos.last_sale_price - pos.cost_basis) / pos.cost_basis * 100
            log.info(f'  {stock}: {pos.amount} shares, cost={pos.cost_basis:.2f}, '
                     f'price={pos.last_sale_price:.2f}, P&L={pnl:.2f}%')

    # Persist trade log
    try:
        with open(NOTEBOOK_PATH + 'trade_log.pkl', 'rb') as f:
            trade_log = pickle.load(f)
    except:
        trade_log = []

    trade_log.append({
        'date': str(context.blotter.current_dt),
        'total_value': total_value,
        'cash': cash,
        'stock_pool': g.stock_pool
    })

    with open(NOTEBOOK_PATH + 'trade_log.pkl', 'wb') as f:
        pickle.dump(trade_log, f, -1)

def handle_data(context, data):
    pass
```

### Multi-Strategy Parallel — MACD + KDJ Dual Signal Confirmation

```python
def initialize(context):
    g.security = '600570.SS'
    set_universe(g.security)

def handle_data(context, data):
    stock = g.security
    # Get last 60 days' bar data
    df = get_history(60, '1d', ['open', 'high', 'low', 'close', 'volume'], stock, fq='pre')
    if len(df) < 60:
        return

    close = df['close'].values
    high = df['high'].values
    low = df['low'].values

    # Calculate MACD indicator
    macd = get_MACD(stock, N1=12, N2=26, M=9)
    dif = macd['DIF']
    dea = macd['DEA']
    macd_hist = macd['MACD']

    # Calculate KDJ indicator
    kdj = get_KDJ(stock, N=9, M1=3, M2=3)
    k_value = kdj['K']
    d_value = kdj['D']
    j_value = kdj['J']

    # Calculate RSI indicator
    rsi = get_RSI(stock, N=14)
    rsi_value = rsi['RSI']

    position = get_position(stock)
    cash = context.portfolio.cash
    current_price = data[stock]['close']

    # Buy conditions (triple confirmation):
    # 1. MACD golden cross (DIF crosses above DEA)
    # 2. KDJ golden cross (K crosses above D) and J < 80 (not overbought)
    # 3. RSI between 30-70 (not in extreme zone)
    macd_golden = dif > dea  # Simplified check
    kdj_golden = k_value > d_value and j_value < 80
    rsi_normal = 30 < rsi_value < 70

    if macd_golden and kdj_golden and rsi_normal and position.amount == 0:
        order_value(stock, cash * 0.95)
        log.info(f'Buy signal: MACD golden cross + KDJ golden cross + RSI normal, DIF={dif:.2f}, K={k_value:.1f}, RSI={rsi_value:.1f}')

    # Sell conditions (any one triggers):
    # 1. MACD death cross (DIF crosses below DEA)
    # 2. KDJ overbought (J > 100)
    # 3. RSI overbought (RSI > 80)
    elif position.amount > 0:
        if dif < dea or j_value > 100 or rsi_value > 80:
            reason = []
            if dif < dea: reason.append('MACD death cross')
            if j_value > 100: reason.append(f'KDJ overbought J={j_value:.1f}')
            if rsi_value > 80: reason.append(f'RSI overbought={rsi_value:.1f}')
            order_target(stock, 0)
            log.info(f'Sell signal: {"+".join(reason)}')
```

---

## 社区与支持

由 **大佬量化 (Boss Quant)** 维护 — 量化交易教学与策略研发团队。

微信客服: **bossquant1** · [Bilibili](https://space.bilibili.com/48693330) · 搜索 **大佬量化** on 微信公众号 / Bilibili / 抖音
