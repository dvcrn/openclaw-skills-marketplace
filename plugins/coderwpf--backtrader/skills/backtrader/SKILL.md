---
name: backtrader
description: "Backtrader open-source quantitative backtesting framework — supports multiple data sources, strategies, and timeframes for backtesting and live trading, implemented in pure Python."
homepage: https://github.com/mementum/backtrader
---

# Backtrader (Open-Source Quantitative Backtesting Framework)

[Backtrader](https://github.com/mementum/backtrader) is a powerful open-source Python quantitative backtesting framework that supports multiple data sources, strategies, and timeframes for backtesting and live trading. Implemented in pure Python with no external dependencies, it features a clean and extensible architecture.

> Documentation: https://www.backtrader.com/docu/

## Installation

```bash
pip install backtrader
# If plotting is needed
pip install backtrader[plotting]
# Or
pip install matplotlib
```

## Core Concepts

Backtrader uses an object-oriented, event-driven architecture:

- **Cerebro**: The strategy engine, responsible for coordinating data, strategies, and the broker
- **Strategy**: The strategy class where trading logic is written
- **Data Feed**: Data sources, supporting CSV, Pandas, and online data
- **Broker**: Broker simulation, managing funds and orders
- **Indicator**: Technical indicators, with 100+ built-in common indicators
- **Analyzer**: Analyzers for calculating strategy performance metrics
- **Observer**: Observers that record strategy runtime status

## Minimal Example

```python
import backtrader as bt

class MyStrategy(bt.Strategy):
    """Simple moving average strategy"""
    params = (('period', 20),)  # Strategy parameter: MA period

    def __init__(self):
        # Initialize indicators (defined in __init__, calculated automatically)
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.period)

    def next(self):
        # Triggered once per bar, write trading logic here
        if self.data.close[0] > self.sma[0]:
            if not self.position:  # Buy if no position
                self.buy()
        elif self.data.close[0] < self.sma[0]:
            if self.position:      # Sell if holding position
                self.sell()

# Create engine
cerebro = bt.Cerebro()
cerebro.addstrategy(MyStrategy)

# Load data (Yahoo CSV format)
data = bt.feeds.YahooFinanceCSVData(dataname='stock_data.csv')
cerebro.adddata(data)

# Set initial capital
cerebro.broker.setcash(100000.0)
# Set commission
cerebro.broker.setcommission(commission=0.001)

# Run backtest
print(f'Initial capital: {cerebro.broker.getvalue():.2f}')
cerebro.run()
print(f'Final capital: {cerebro.broker.getvalue():.2f}')

# Plot results
cerebro.plot()
```

---

## Data Sources

### Loading from Pandas DataFrame

```python
import backtrader as bt
import pandas as pd

# Read data from CSV
df = pd.read_csv('stock_data.csv', parse_dates=['date'], index_col='date')
# DataFrame must contain columns: open, high, low, close, volume (lowercase column names)

data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data)
```

### Loading from CSV File

```python
# Generic CSV format
data = bt.feeds.GenericCSVData(
    dataname='stock_data.csv',
    dtformat='%Y-%m-%d',    # Date format
    datetime=0,              # Date column index
    open=1,                  # Open price column index
    high=2,                  # High price column index
    low=3,                   # Low price column index
    close=4,                 # Close price column index
    volume=5,                # Volume column index
    openinterest=-1          # Open interest column index (-1 means no such column)
)
cerebro.adddata(data)
```

### Multiple Stocks / Multiple Timeframes

```python
# Load multiple stock data
data1 = bt.feeds.PandasData(dataname=df1, name='stock1')
data2 = bt.feeds.PandasData(dataname=df2, name='stock2')
cerebro.adddata(data1)
cerebro.adddata(data2)

# Access multiple stocks in strategy
class MultiStockStrategy(bt.Strategy):
    def __init__(self):
        # self.datas[0] is the first stock, self.datas[1] is the second
        self.sma1 = bt.indicators.SMA(self.datas[0].close, period=20)
        self.sma2 = bt.indicators.SMA(self.datas[1].close, period=20)

    def next(self):
        for i, d in enumerate(self.datas):
            print(f'{d._name}: close={d.close[0]:.2f}')
```

### Data Resampling (Minute Bars to Daily Bars)

```python
# Load minute data
data_min = bt.feeds.GenericCSVData(dataname='1min_data.csv', timeframe=bt.TimeFrame.Minutes)
cerebro.adddata(data_min)

# Resample to daily bars
cerebro.resampledata(data_min, timeframe=bt.TimeFrame.Days)
```


---

## Strategy Class In-Depth

### Strategy Parameters

```python
class MyStrategy(bt.Strategy):
    # Define adjustable parameters (tuple format)
    params = (
        ('fast_period', 5),     # Fast MA period
        ('slow_period', 20),    # Slow MA period
        ('stake', 100),         # Trade size per order
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SMA(period=self.p.fast_period)
        self.slow_ma = bt.indicators.SMA(period=self.p.slow_period)
        # self.p is shorthand for self.params

    def next(self):
        if self.fast_ma[0] > self.slow_ma[0]:
            self.buy(size=self.p.stake)

# Parameters can be overridden at runtime
cerebro.addstrategy(MyStrategy, fast_period=10, slow_period=30)
```

### Trading Methods

```python
class MyStrategy(bt.Strategy):
    def next(self):
        # Buy by quantity
        self.buy(size=100)                    # Buy 100 shares
        self.sell(size=100)                   # Sell 100 shares

        # Adjust to target position
        self.order_target_size(target=500)    # Adjust position to 500 shares
        self.order_target_value(target=50000) # Adjust position to 50,000 in market value
        self.order_target_percent(target=0.5) # Adjust position to 50% of total assets

        # Limit order
        self.buy(size=100, price=10.5, exectype=bt.Order.Limit)
        # Stop order
        self.sell(size=100, price=9.0, exectype=bt.Order.Stop)
        # Stop-limit order
        self.buy(size=100, price=10.5, pricelimit=10.8, exectype=bt.Order.StopLimit)

        # Cancel order
        order = self.buy(size=100)
        self.cancel(order)

        # Place order for a different stock
        self.buy(data=self.datas[1], size=200)  # Buy the second stock
```

### Order Notification Callbacks

```python
class MyStrategy(bt.Strategy):
    def notify_order(self, order):
        """Triggered when order status changes"""
        if order.status in [order.Submitted, order.Accepted]:
            return  # Order submitted/accepted, waiting for execution

        if order.status in [order.Completed]:
            if order.isbuy():
                print(f'Buy executed: price={order.executed.price:.2f}, '
                      f'size={order.executed.size}, commission={order.executed.comm:.2f}')
            else:
                print(f'Sell executed: price={order.executed.price:.2f}, '
                      f'size={order.executed.size}, commission={order.executed.comm:.2f}')

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print(f'Order failed: status={order.getstatusname()}')

    def notify_trade(self, trade):
        """Triggered when a trade is completed (a buy and sell form a complete trade)"""
        if trade.isclosed:
            print(f'Trade completed: gross P&L={trade.pnl:.2f}, net P&L={trade.pnlcomm:.2f}')
```

### Accessing Data and Positions

```python
class MyStrategy(bt.Strategy):
    def next(self):
        # Current bar data
        current_close = self.data.close[0]     # Current close price
        prev_close = self.data.close[-1]       # Previous bar close price
        current_volume = self.data.volume[0]   # Current volume
        current_date = self.data.datetime.date(0)  # Current date

        # Position info
        position = self.getposition(self.data)
        print(f'Position size: {position.size}')
        print(f'Average price: {position.price:.2f}')

        # Account info
        cash = self.broker.getcash()           # Available cash
        value = self.broker.getvalue()         # Total portfolio value
        print(f'Available cash: {cash:.2f}, Total value: {value:.2f}')
```


---

## Built-in Technical Indicators

```python
class MyStrategy(bt.Strategy):
    def __init__(self):
        # Moving averages
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=20)
        self.ema = bt.indicators.ExponentialMovingAverage(self.data.close, period=20)
        self.wma = bt.indicators.WeightedMovingAverage(self.data.close, period=20)

        # MACD
        self.macd = bt.indicators.MACD(self.data.close)
        # self.macd.macd = DIF line, self.macd.signal = DEA line, self.macd.histo = MACD histogram

        # RSI
        self.rsi = bt.indicators.RSI(self.data.close, period=14)

        # Bollinger Bands
        self.boll = bt.indicators.BollingerBands(self.data.close, period=20, devfactor=2.0)
        # self.boll.mid = middle band, self.boll.top = upper band, self.boll.bot = lower band

        # KDJ (Stochastic Oscillator)
        self.stoch = bt.indicators.Stochastic(self.data, period=14)

        # ATR (Average True Range)
        self.atr = bt.indicators.ATR(self.data, period=14)

        # Crossover signals
        self.crossover = bt.indicators.CrossOver(self.sma, self.ema)
        # crossover > 0 means golden cross, < 0 means death cross
```

---

## Broker Settings

```python
cerebro = bt.Cerebro()

# Set initial capital
cerebro.broker.setcash(1000000.0)

# Set commission
cerebro.broker.setcommission(commission=0.001)  # 0.1%

# Set commission by percentage
cerebro.broker.setcommission(
    commission=0.0003,     # 0.03%
    margin=None,           # Margin (for futures)
    mult=1.0               # Contract multiplier (for futures)
)

# Set slippage
cerebro.broker.set_slippage_perc(perc=0.001)    # Percentage-based slippage
cerebro.broker.set_slippage_fixed(fixed=0.02)   # Fixed slippage

# Set trade size per order
cerebro.addsizer(bt.sizers.FixedSize, stake=100)        # Fixed 100 shares
cerebro.addsizer(bt.sizers.PercentSizer, percents=95)   # 95% of total assets
```

---

## Analyzers

```python
cerebro = bt.Cerebro()
cerebro.addstrategy(MyStrategy)

# Add analyzers
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')       # Sharpe Ratio
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')        # Max Drawdown
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')          # Returns
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')     # Trade Statistics
cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')                 # System Quality Number
cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='annual')     # Annual Return

results = cerebro.run()
strat = results[0]

# Get analysis results
print(f"Sharpe Ratio: {strat.analyzers.sharpe.get_analysis()['sharperatio']:.2f}")
print(f"Max Drawdown: {strat.analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")
print(f"Total Return: {strat.analyzers.returns.get_analysis()['rtot']:.4f}")

# Trade statistics
trade_analysis = strat.analyzers.trades.get_analysis()
print(f"Total trades: {trade_analysis['total']['total']}")
print(f"Winning trades: {trade_analysis['won']['total']}")
print(f"Losing trades: {trade_analysis['lost']['total']}")
```


---

## Parameter Optimization

```python
# Use optstrategy for parameter grid search
cerebro = bt.Cerebro()
cerebro.optstrategy(
    MyStrategy,
    fast_period=range(5, 15),     # Fast MA: 5 to 14
    slow_period=range(20, 40, 5)  # Slow MA: 20, 25, 30, 35
)

data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data)
cerebro.broker.setcash(100000)
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')

# Run optimization (automatically iterates through all parameter combinations)
results = cerebro.run(maxcpus=4)  # Multi-core parallel

# Extract best parameters
best_sharpe = -999
best_params = None
for result in results:
    for strat in result:
        sharpe = strat.analyzers.sharpe.get_analysis().get('sharperatio', 0)
        if sharpe and sharpe > best_sharpe:
            best_sharpe = sharpe
            best_params = strat.params
            
print(f'Best params: fast={best_params.fast_period}, slow={best_params.slow_period}')
print(f'Best Sharpe: {best_sharpe:.2f}')
```

---

## Advanced Examples

### MACD + Bollinger Bands Combination Strategy

```python
import backtrader as bt

class MACDBollStrategy(bt.Strategy):
    """MACD golden cross + Bollinger Band lower band support combination buy strategy"""
    params = (
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
        ('boll_period', 20),
        ('boll_dev', 2.0),
        ('stake', 100),
    )

    def __init__(self):
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.p.macd_fast,
            period_me2=self.p.macd_slow,
            period_signal=self.p.macd_signal
        )
        self.boll = bt.indicators.BollingerBands(
            self.data.close, period=self.p.boll_period, devfactor=self.p.boll_dev
        )
        # MACD golden cross signal
        self.macd_cross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

    def next(self):
        if not self.position:
            # Buy condition: MACD golden cross AND price below Bollinger middle band (buy at low levels)
            if self.macd_cross[0] > 0 and self.data.close[0] < self.boll.mid[0]:
                self.buy(size=self.p.stake)
                print(f'{self.data.datetime.date(0)} Buy: {self.data.close[0]:.2f}')
        else:
            # Sell condition: price touches Bollinger upper band OR MACD death cross
            if self.data.close[0] > self.boll.top[0] or self.macd_cross[0] < 0:
                self.sell(size=self.p.stake)
                print(f'{self.data.datetime.date(0)} Sell: {self.data.close[0]:.2f}')

    def notify_trade(self, trade):
        if trade.isclosed:
            print(f'Trade completed: net profit={trade.pnlcomm:.2f}')

# Run backtest
cerebro = bt.Cerebro()
cerebro.addstrategy(MACDBollStrategy)
data = bt.feeds.PandasData(dataname=df)  # df is a DataFrame containing OHLCV data
cerebro.adddata(data)
cerebro.broker.setcash(100000)
cerebro.broker.setcommission(commission=0.001)
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='dd')
results = cerebro.run()
strat = results[0]
print(f'Sharpe Ratio: {strat.analyzers.sharpe.get_analysis()["sharperatio"]:.2f}')
print(f'Max Drawdown: {strat.analyzers.dd.get_analysis()["max"]["drawdown"]:.2f}%')
cerebro.plot()
```


### Turtle Trading Strategy (Complete Implementation)

```python
import backtrader as bt

class TurtleStrategy(bt.Strategy):
    """Classic Turtle Trading Strategy — Donchian Channel breakout + ATR position sizing"""
    params = (
        ('entry_period', 20),    # Entry channel period
        ('exit_period', 10),     # Exit channel period
        ('atr_period', 20),      # ATR period
        ('risk_pct', 0.01),      # Risk per trade as percentage
    )

    def __init__(self):
        self.entry_high = bt.indicators.Highest(self.data.high, period=self.p.entry_period)
        self.entry_low = bt.indicators.Lowest(self.data.low, period=self.p.entry_period)
        self.exit_high = bt.indicators.Highest(self.data.high, period=self.p.exit_period)
        self.exit_low = bt.indicators.Lowest(self.data.low, period=self.p.exit_period)
        self.atr = bt.indicators.ATR(self.data, period=self.p.atr_period)
        self.order = None

    def next(self):
        if self.order:
            return  # Pending order exists, wait

        # Calculate position size (ATR-based risk management)
        atr_val = self.atr[0]
        if atr_val <= 0:
            return
        unit_size = int(self.broker.getvalue() * self.p.risk_pct / atr_val)
        unit_size = max(unit_size, 1)

        if not self.position:
            # Break above 20-day high → go long
            if self.data.close[0] > self.entry_high[-1]:
                self.order = self.buy(size=unit_size)
        else:
            # Break below 10-day low → close position
            if self.data.close[0] < self.exit_low[-1]:
                self.order = self.close()

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f'{self.data.datetime.date(0)} Buy {order.executed.size} shares @ {order.executed.price:.2f}')
            else:
                print(f'{self.data.datetime.date(0)} Sell @ {order.executed.price:.2f}')
        self.order = None
```

### Multi-Stock Rotation Strategy

```python
import backtrader as bt

class MomentumRotation(bt.Strategy):
    """Momentum rotation strategy — hold the top N stocks with strongest momentum each month"""
    params = (
        ('momentum_period', 20),  # Momentum calculation period (trading days)
        ('hold_num', 3),          # Number of stocks to hold
        ('rebalance_days', 20),   # Rebalancing period
    )

    def __init__(self):
        self.counter = 0
        # Calculate momentum indicator (N-day rate of return) for each stock
        self.momentums = {}
        for d in self.datas:
            self.momentums[d._name] = bt.indicators.RateOfChange(
                d.close, period=self.p.momentum_period
            )

    def next(self):
        self.counter += 1
        if self.counter % self.p.rebalance_days != 0:
            return  # Not rebalancing day

        # Calculate and rank momentum for each stock
        rankings = []
        for d in self.datas:
            mom = self.momentums[d._name][0]
            rankings.append((d._name, d, mom))
        rankings.sort(key=lambda x: x[2], reverse=True)

        # Select top N stocks by momentum
        selected = [r[1] for r in rankings[:self.p.hold_num]]
        selected_names = [r[0] for r in rankings[:self.p.hold_num]]
        print(f'{self.data.datetime.date(0)} Selected stocks: {selected_names}')

        # Sell positions not in the target list
        for d in self.datas:
            if self.getposition(d).size > 0 and d not in selected:
                self.close(data=d)

        # Equal-weight buy target stocks
        if selected:
            per_value = self.broker.getvalue() * 0.95 / len(selected)
            for d in selected:
                target_size = int(per_value / d.close[0])
                current_size = self.getposition(d).size
                if target_size > current_size:
                    self.buy(data=d, size=target_size - current_size)
                elif target_size < current_size:
                    self.sell(data=d, size=current_size - target_size)
```


---

## Usage Tips

- Backtrader is a purely local framework with no dependency on online services, ideal for offline research.
- Data must be prepared by the user (can be used with data sources like AKShare, Tushare, etc.).
- Define indicators in `__init__`, write trading logic in `next` — this is the core pattern.
- Use `self.data.close[0]` to access the current value, `[-1]` to access the previous value.
- Parameter optimization via `optstrategy` supports multi-core parallelism for significant speedup.
- Plotting requires matplotlib to be installed; simply call `cerebro.plot()`.
- Documentation: https://www.backtrader.com/docu/

---

## 社区与支持

由 **大佬量化 (Boss Quant)** 维护 — 量化交易教学与策略研发团队。

微信客服: **bossquant1** · [Bilibili](https://space.bilibili.com/48693330) · 搜索 **大佬量化** on 微信公众号 / Bilibili / 抖音
