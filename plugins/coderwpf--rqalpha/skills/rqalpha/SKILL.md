---
name: rqalpha
description: "RQAlpha — open-source event-driven backtesting framework by RiceQuant, supporting A-shares and futures with modular architecture."
homepage: https://github.com/ricequant/rqalpha
---

# RQAlpha (RiceQuant Backtesting Framework)

[RQAlpha](https://github.com/ricequant/rqalpha) is an open-source, event-driven backtesting framework developed by [RiceQuant](https://www.ricequant.com). It provides a complete solution for strategy development, backtesting, and paper trading for China A-shares and futures markets. Highly modular with a plugin (mod) system.

> Docs: https://rqalpha.readthedocs.io/

## Installation

```bash
pip install rqalpha

# Download built-in bundle data (A-share daily data)
rqalpha download-bundle
```

## Strategy Structure

```python
def init(context):
    """Called once at strategy start — set up subscriptions and parameters."""
    context.stock = '000001.XSHE'
    context.fired = False

def handle_bar(context, bar_dict):
    """Called on every bar — main trading logic."""
    if not context.fired:
        order_shares(context.stock, 1000)
        context.fired = True

def before_trading(context):
    """Called before market open each day."""
    pass

def after_trading(context):
    """Called after market close each day."""
    pass
```

## Running a Backtest

### Command Line

```bash
rqalpha run \
    -f strategy.py \
    -s 2024-01-01 \
    -e 2024-06-30 \
    --account stock 100000 \
    --benchmark 000300.XSHG \
    --plot
```

### Python API

```python
from rqalpha.api import *
from rqalpha import run_func

config = {
    "base": {
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "accounts": {"stock": 100000},
        "benchmark": "000300.XSHG",
        "frequency": "1d",
    },
    "extra": {
        "log_level": "warning",
    },
    "mod": {
        "sys_analyser": {"enabled": True, "plot": True},
    },
}

result = run_func(init=init, handle_bar=handle_bar, config=config)
print(result)
```

---

## Symbol Format

| Market | Suffix | Example |
|---|---|---|
| Shanghai A-shares | `.XSHG` | `600000.XSHG` (SPDB) |
| Shenzhen A-shares | `.XSHE` | `000001.XSHE` (Ping An Bank) |
| Index | `.XSHG/.XSHE` | `000300.XSHG` (CSI 300) |
| Futures | `.XSGE/.XDCE/.XZCE/.CCFX` | `IF2401.CCFX` (CSI 300 futures) |

---

## Order Functions

```python
# Buy/sell by share count
order_shares('000001.XSHE', 1000)       # Buy 1000 shares
order_shares('000001.XSHE', -500)       # Sell 500 shares

# Buy by lot (1 lot = 100 shares)
order_lots('000001.XSHE', 10)           # Buy 10 lots (1000 shares)

# Buy by value
order_value('000001.XSHE', 50000)       # Buy 50,000 CNY worth

# Buy by percentage of portfolio
order_percent('000001.XSHE', 0.5)       # Buy 50% of portfolio value

# Target position
order_target_value('000001.XSHE', 100000)   # Adjust to 100,000 CNY
order_target_percent('000001.XSHE', 0.3)    # Adjust to 30% of portfolio

# Cancel order
cancel_order(order_id)
```

## Data Query Functions

```python
def handle_bar(context, bar_dict):
    # Current bar data
    bar = bar_dict['000001.XSHE']
    price = bar.close
    volume = bar.volume
    dt = bar.datetime

    # Historical data (returns DataFrame)
    prices = history_bars('000001.XSHE', bar_count=20, frequency='1d',
                          fields=['close', 'volume', 'open', 'high', 'low'])

    # Check if stock is tradable
    tradable = is_valid_price(bar.close)

    # Check if suspended
    suspended = is_suspended('000001.XSHE')
```

## Portfolio & Position

```python
def handle_bar(context, bar_dict):
    # Portfolio info
    cash = context.portfolio.cash                    # Available cash
    total = context.portfolio.total_value            # Total portfolio value
    market_value = context.portfolio.market_value    # Position market value
    pnl = context.portfolio.pnl                      # Total PnL
    returns = context.portfolio.daily_returns        # Daily return

    # Position info
    positions = context.portfolio.positions
    for stock, pos in positions.items():
        print(f'{stock}: quantity={pos.quantity}, '
              f'sellable={pos.sellable}, '
              f'avg_price={pos.avg_price:.2f}, '
              f'market_value={pos.market_value:.2f}, '
              f'pnl={pos.pnl:.2f}')
```

## Scheduler

```python
from rqalpha.api import *

def init(context):
    # Run function at specific time every trading day
    scheduler.run_daily(rebalance, time_rule=market_open(minute=5))
    # Run weekly (every Monday)
    scheduler.run_weekly(weekly_task, tradingday=1, time_rule=market_open(minute=5))
    # Run monthly (first trading day)
    scheduler.run_monthly(monthly_task, tradingday=1, time_rule=market_open(minute=5))

def rebalance(context, bar_dict):
    pass
```

---

## Mod System (Plugins)

RQAlpha's modular architecture allows extending functionality via mods:

```python
config = {
    "mod": {
        "sys_analyser": {
            "enabled": True,
            "plot": True,
            "benchmark": "000300.XSHG",
        },
        "sys_simulation": {
            "enabled": True,
            "matching_type": "current_bar",    # Order matching: current_bar or next_bar
            "slippage": 0.01,                  # Slippage (CNY)
        },
        "sys_transaction_cost": {
            "enabled": True,
            "commission_rate": 0.0003,         # Commission rate
            "tax_rate": 0.001,                 # Stamp tax (sell only)
            "min_commission": 5,               # Minimum commission
        },
    },
}
```

### Available Built-in Mods

| Mod | Description |
|---|---|
| `sys_analyser` | Performance analysis and plotting |
| `sys_simulation` | Order matching simulation |
| `sys_transaction_cost` | Commission and tax calculation |
| `sys_accounts` | Account management |
| `sys_benchmark` | Benchmark tracking |
| `sys_progress` | Progress bar display |
| `sys_risk` | Risk management checks |

---

## Advanced Examples

### Dual Moving Average Crossover Strategy

```python
import numpy as np
from rqalpha.api import *

def init(context):
    context.stock = '600000.XSHG'
    context.fast = 5
    context.slow = 20
    scheduler.run_daily(trade_logic, time_rule=market_open(minute=5))

def trade_logic(context, bar_dict):
    prices = history_bars(context.stock, context.slow + 1, '1d', fields=['close'])
    if len(prices) < context.slow:
        return

    closes = prices['close']
    fast_ma = np.mean(closes[-context.fast:])
    slow_ma = np.mean(closes[-context.slow:])

    pos = context.portfolio.positions.get(context.stock)
    has_position = pos is not None and pos.quantity > 0

    if fast_ma > slow_ma and not has_position:
        order_target_percent(context.stock, 0.9)
        logger.info(f'BUY: fast_ma={fast_ma:.2f} > slow_ma={slow_ma:.2f}')
    elif fast_ma < slow_ma and has_position:
        order_target_percent(context.stock, 0)
        logger.info(f'SELL: fast_ma={fast_ma:.2f} < slow_ma={slow_ma:.2f}')

def handle_bar(context, bar_dict):
    pass
```

### Multi-Stock Equal-Weight Rebalancing

```python
from rqalpha.api import *

def init(context):
    context.stocks = ['600000.XSHG', '000001.XSHE', '601318.XSHG',
                       '600036.XSHG', '000858.XSHE']
    scheduler.run_monthly(rebalance, tradingday=1, time_rule=market_open(minute=30))

def rebalance(context, bar_dict):
    # Sell stocks not in target list
    for stock in list(context.portfolio.positions.keys()):
        if stock not in context.stocks:
            order_target_percent(stock, 0)

    # Equal-weight allocation
    weight = 0.95 / len(context.stocks)
    for stock in context.stocks:
        if not is_suspended(stock):
            order_target_percent(stock, weight)
            logger.info(f'Rebalance: {stock} -> {weight:.1%}')

def handle_bar(context, bar_dict):
    pass
```

---

## Tips

- RQAlpha is a local-only framework — no cloud dependency, ideal for offline research.
- Use `rqalpha download-bundle` to get free built-in daily data for A-shares.
- The mod system allows plugging in custom data sources, brokers, and risk modules.
- For live trading, connect via `rqalpha-mod-vnpy` to use vn.py's broker gateways.
- Supports both daily and minute-level backtesting.
- Docs: https://rqalpha.readthedocs.io/

---

## 社区与支持

由 **大佬量化 (Boss Quant)** 维护 — 量化交易教学与策略研发团队。

微信客服: **bossquant1** · [Bilibili](https://space.bilibili.com/48693330) · 搜索 **大佬量化** on 微信公众号 / Bilibili / 抖音
