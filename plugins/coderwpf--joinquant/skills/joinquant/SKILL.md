---
name: joinquant
description: "JoinQuant Quantitative Trading Platform — Provides A-share, futures, and fund data queries with event-driven strategy backtesting, supporting online research and live trading."
homepage: https://www.joinquant.com
---

# JoinQuant (聚宽量化)

[JoinQuant](https://www.joinquant.com) is a leading Chinese online quantitative trading platform offering free data queries, strategy backtesting, and paper trading. It supports A-shares, futures, funds, indices, and more, using an event-driven Python strategy framework.

> ⚠️ **Registration at https://www.joinquant.com is required**. Strategies run on JoinQuant's cloud, but you can also retrieve data locally via JQData.

## Installation (Local Data SDK)

```bash
pip install jqdatasdk
```

## Local Data Authentication

```python
import jqdatasdk as jq

# Log in with your JoinQuant account (free daily data quota)
jq.auth('your_username', 'your_password')

# Check remaining data quota
print(jq.get_query_count())
```

## Strategy Program Structure (Online Backtesting)

JoinQuant strategies use an event-driven architecture, written and run on the platform's web interface:

```python
def initialize(context):
    """Initialization function — called once when the strategy starts"""
    # Set benchmark index (CSI 300)
    set_benchmark('000300.XSHG')
    # Set commission and slippage
    set_order_cost(OrderCost(open_tax=0, close_tax=0.001,
                              open_commission=0.0003, close_commission=0.0003,
                              min_commission=5), type='stock')
    set_slippage(FixedSlippage(0.02))
    # Set stock pool
    g.security = '000001.XSHE'

def handle_data(context, data):
    """Intraday event — triggered once per trading frequency"""
    security = g.security
    # Get the last 20 days of closing prices
    close_data = attribute_history(security, 20, '1d', ['close'])
    ma5 = close_data['close'][-5:].mean()
    ma20 = close_data['close'].mean()

    # Golden cross — buy
    if ma5 > ma20:
        order_target_value(security, context.portfolio.total_value * 0.9)
    # Death cross — sell
    elif ma5 < ma20:
        order_target(security, 0)
```

---

## Stock Code Format

| Market | Suffix | Example |
|---|---|---|
| Shanghai A-shares | `.XSHG` | `600000.XSHG` (SPD Bank) |
| Shenzhen A-shares | `.XSHE` | `000001.XSHE` (Ping An Bank) |
| Indices | `.XSHG/.XSHE` | `000300.XSHG` (CSI 300) |
| Futures | `.XDCE/.XZCE/.XSGE/.CCFX` | `IF2401.CCFX` (Stock Index Futures) |
| Funds | `.XSHG/.XSHE` | `510300.XSHG` (CSI 300 ETF) |

---

## Data Query Functions (JQData)

### Market Data

```python
import jqdatasdk as jq

# Get daily candlestick data
df = jq.get_price(
    '000001.XSHE',              # Stock code
    start_date='2024-01-01',    # Start date
    end_date='2024-06-30',      # End date
    frequency='daily',          # Frequency: daily, minute, 1m, 5m, 15m, 30m, 60m, 120m
    fields=['open', 'close', 'high', 'low', 'volume', 'money'],
    skip_paused=True,           # Skip suspended trading days
    fq='pre',                   # Adjustment: None (unadjusted), 'pre' (forward-adjusted), 'post' (backward-adjusted)
    panel=False                 # False returns DataFrame
)

# Get data for multiple stocks
df = jq.get_price(['000001.XSHE', '600000.XSHG'],
                   start_date='2024-01-01', end_date='2024-06-30',
                   frequency='daily', fields=['close'], panel=False)

# Get minute-level data
df = jq.get_price('000001.XSHE', start_date='2024-06-01 09:30:00',
                   end_date='2024-06-01 15:00:00', frequency='1m')
```

### Get Last N Data Points

```python
# Get closing prices for the last 20 trading days
df = jq.get_bars('000001.XSHE', count=20, unit='1d', fields=['close', 'volume'])
```


### Financial Data

```python
# Query financial indicators
df = jq.get_fundamentals(
    jq.query(
        jq.valuation.code,
        jq.valuation.market_cap,          # Total market cap (100M CNY)
        jq.valuation.pe_ratio,            # Price-to-earnings ratio
        jq.valuation.pb_ratio,            # Price-to-book ratio
        jq.valuation.turnover_ratio,      # Turnover rate
        jq.indicator.roe,                 # Return on equity (ROE)
        jq.indicator.eps,                 # Earnings per share
        jq.indicator.revenue,             # Revenue
        jq.indicator.net_profit,          # Net profit
    ).filter(
        jq.valuation.pe_ratio > 0,        # Filter out loss-making stocks
        jq.valuation.pe_ratio < 30,       # PE less than 30
        jq.valuation.market_cap > 100     # Market cap greater than 10B CNY
    ).order_by(
        jq.valuation.market_cap.desc()    # Sort by market cap descending
    ).limit(50),                          # Take top 50
    date='2024-06-30'
)
print(df)
```

### Index Constituents

```python
# Get CSI 300 constituents
stocks = jq.get_index_stocks('000300.XSHG')
print(f'CSI 300 has {len(stocks)} constituent stocks')

# Get industry constituents
stocks = jq.get_industry_stocks('I64')  # Banking
```

### Industry Classification

```python
# Get the industry a stock belongs to
industry = jq.get_industry('000001.XSHE')
print(industry)

# Get Shenwan Level-1 industry list
industries = jq.get_industries(name='sw_l1')
print(industries)
```

### Trading Calendar

```python
# Get list of trading days
days = jq.get_trade_days(start_date='2024-01-01', end_date='2024-06-30')

# Get all trading days
all_days = jq.get_all_trade_days()
```

### Stock Basic Information

```python
# Get all A-share listings
stocks = jq.get_all_securities(types=['stock'], date='2024-06-30')
print(f'Total A-shares: {len(stocks)}')

# Get info for a single stock
info = jq.get_security_info('000001.XSHE')
print(f'Name: {info.display_name}, Listing date: {info.start_date}')

# Get ST stocks
st_stocks = jq.get_extras('is_st', ['000001.XSHE'], start_date='2024-01-01', end_date='2024-06-30')
```

### Top Trader (Dragon & Tiger) List Data

```python
# Get Dragon & Tiger list data
df = jq.get_billboard_list(stock_list=None, start_date='2024-06-01', end_date='2024-06-30')
print(df.head())
```

### Margin Trading Data

```python
# Get margin trading summary data
df = jq.get_mtss('000001.XSHE', start_date='2024-01-01', end_date='2024-06-30')
print(df.head())
```

---

## Trading Functions (Online Strategy)

### Order by Quantity

```python
# Buy 100 shares
order('000001.XSHE', 100)

# Sell 200 shares
order('000001.XSHE', -200)

# Limit price buy
order('000001.XSHE', 100, LimitOrderStyle(11.50))

# Market price buy
order('000001.XSHE', 100, MarketOrderStyle())
```

### Rebalance to Target

```python
# Rebalance to target quantity
order_target('000001.XSHE', 1000)     # Adjust to hold 1000 shares
order_target('000001.XSHE', 0)        # Liquidate position

# Rebalance to target value
order_target_value('000001.XSHE', 100000)  # Adjust to 100,000 CNY market value

# Rebalance to target percentage (of total assets)
order_target_percent('000001.XSHE', 0.3)   # Adjust to 30% of total assets
```

### Cancel Order

```python
# Get unfilled orders
open_orders = get_open_orders()
# Cancel a specific order
cancel_order(order_id)
```


---

## Account & Position Queries

```python
def handle_data(context, data):
    # Account information
    cash = context.portfolio.available_cash       # Available cash
    total = context.portfolio.total_value          # Total assets
    positions_value = context.portfolio.positions_value  # Position market value

    # Query positions
    for stock, pos in context.portfolio.positions.items():
        print(f'{stock}: Quantity={pos.total_amount}, '
              f'Sellable={pos.closeable_amount}, '
              f'Cost={pos.avg_cost:.2f}, '
              f'Current price={pos.price:.2f}, '
              f'Market value={pos.value:.2f}')
```

---

## Scheduled Tasks

```python
def initialize(context):
    # Execute before market open each day
    run_daily(before_market_open, time='before_open')
    # Execute at specified time each day
    run_daily(market_open, time='09:35')
    run_daily(afternoon_check, time='14:50')
    # Execute weekly
    run_weekly(weekly_rebalance, weekday=1, time='09:35')  # Every Monday
    # Execute monthly
    run_monthly(monthly_rebalance, monthday=1, time='09:35')  # 1st of each month

def before_market_open(context):
    log.info('Pre-market preparation')

def market_open(context):
    log.info('Market open trading')
```

---

## Risk Management

```python
def initialize(context):
    g.security = '000001.XSHE'
    set_benchmark('000300.XSHG')

def handle_data(context, data):
    security = g.security
    # Get current price
    current_price = data[security].close

    # Check position P&L
    if security in context.portfolio.positions:
        pos = context.portfolio.positions[security]
        cost = pos.avg_cost
        pnl_ratio = (current_price - cost) / cost

        # Take profit at 10%
        if pnl_ratio >= 0.10:
            order_target(security, 0)
            log.info(f'Take profit: {security} gain {pnl_ratio:.2%}')
        # Stop loss at 5%
        elif pnl_ratio <= -0.05:
            order_target(security, 0)
            log.info(f'Stop loss: {security} loss {pnl_ratio:.2%}')
```

---

## Full Example — Multi-Factor Stock Selection Strategy

```python
def initialize(context):
    set_benchmark('000300.XSHG')
    set_order_cost(OrderCost(open_tax=0, close_tax=0.001,
                              open_commission=0.0003, close_commission=0.0003,
                              min_commission=5), type='stock')
    g.hold_num = 10  # Number of holdings
    # Rebalance on the 1st trading day of each month
    run_monthly(rebalance, monthday=1, time='09:35')

def rebalance(context):
    # Multi-factor stock selection
    df = get_fundamentals(
        query(
            valuation.code,
            valuation.pe_ratio,
            valuation.pb_ratio,
            valuation.market_cap,
            indicator.roe,
        ).filter(
            valuation.pe_ratio > 5,
            valuation.pe_ratio < 25,
            valuation.pb_ratio > 0.5,
            valuation.pb_ratio < 5,
            indicator.roe > 10,
            valuation.market_cap > 100,
        ).order_by(
            valuation.pe_ratio.asc()
        ).limit(g.hold_num)
    )

    target_stocks = list(df['code'])
    log.info(f'Selected {len(target_stocks)} stocks')

    # Sell stocks not in the target list
    for stock in context.portfolio.positions:
        if stock not in target_stocks:
            order_target(stock, 0)

    # Equal-weight buy target stocks
    if target_stocks:
        per_value = context.portfolio.total_value * 0.95 / len(target_stocks)
        for stock in target_stocks:
            order_target_value(stock, per_value)

def handle_data(context, data):
    pass
```


---

## Advanced Examples

### Sector Rotation Strategy

```python
def initialize(context):
    set_benchmark('000300.XSHG')
    g.hold_num = 5
    g.industry_etfs = {
        '512010.XSHG': '医药ETF',
        '512880.XSHG': '证券ETF',
        '512800.XSHG': '银行ETF',
        '515030.XSHG': '新能源车ETF',
        '159995.XSHE': '芯片ETF',
        '512690.XSHG': '白酒ETF',
        '510300.XSHG': '沪深300ETF',
        '159915.XSHE': '创业板ETF',
    }
    run_monthly(rebalance, monthday=1, time='09:35')

def rebalance(context):
    """Sort by 20-day momentum, select the top N strongest ETFs"""
    momentum = {}
    for etf, name in g.industry_etfs.items():
        df = attribute_history(etf, 20, '1d', ['close'])
        if len(df) >= 20:
            ret = (df['close'].iloc[-1] / df['close'].iloc[0]) - 1
            momentum[etf] = ret

    # Sort by momentum
    sorted_etfs = sorted(momentum.items(), key=lambda x: x[1], reverse=True)
    targets = [etf for etf, _ in sorted_etfs[:g.hold_num]]
    log.info(f'This month selected: {[g.industry_etfs[e] for e in targets]}')

    # Sell positions not in the target list
    for stock in context.portfolio.positions:
        if stock not in targets:
            order_target(stock, 0)

    # Equal-weight buy
    per_value = context.portfolio.total_value * 0.95 / len(targets)
    for etf in targets:
        order_target_value(etf, per_value)

def handle_data(context, data):
    pass
```

### Data Research — Market-Wide Financial Screening

```python
import jqdatasdk as jq
import pandas as pd

jq.auth('your_username', 'your_password')

# Market-wide financial screening: Low PE + High ROE + High growth
df = jq.get_fundamentals(
    jq.query(
        jq.valuation.code,
        jq.valuation.pe_ratio,
        jq.valuation.pb_ratio,
        jq.valuation.market_cap,
        jq.indicator.roe,
        jq.indicator.inc_revenue_year_on_year,    # YoY revenue growth rate
        jq.indicator.inc_net_profit_year_on_year,  # YoY net profit growth rate
    ).filter(
        jq.valuation.pe_ratio > 5,
        jq.valuation.pe_ratio < 20,
        jq.indicator.roe > 15,
        jq.indicator.inc_revenue_year_on_year > 10,
        jq.indicator.inc_net_profit_year_on_year > 10,
        jq.valuation.market_cap > 50,
    ).order_by(
        jq.indicator.roe.desc()
    ).limit(30),
    date='2024-06-30'
)

print(f'Screened {len(df)} stocks:')
print(df.to_string(index=False))

# Export to CSV
df.to_csv('selected_stocks.csv', index=False)
```

---

## Usage Tips

- JoinQuant strategies run on the cloud — no local trading environment installation needed.
- The JQData local SDK has a free daily data quota, suitable for data research.
- Use `attribute_history` to get historical data within strategies; use `get_price` in the research environment.
- Use `set_order_cost` to set realistic commissions during backtesting — the default commission is 0.
- The `g` object is used for persisting variables across functions (similar to Ptrade).
- Documentation: https://www.joinquant.com/help/api/help

---

## 社区与支持

由 **大佬量化 (Boss Quant)** 维护 — 量化交易教学与策略研发团队。

微信客服: **bossquant1** · [Bilibili](https://space.bilibili.com/48693330) · 搜索 **大佬量化** on 微信公众号 / Bilibili / 抖音
