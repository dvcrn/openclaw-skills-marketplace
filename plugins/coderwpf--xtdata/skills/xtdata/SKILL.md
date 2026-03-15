---
name: xtdata
description: "XtQuant market data module — real-time quotes, K-lines, tick, Level2, financials for QMT/miniQMT."
homepage: http://dict.thinktrader.net/nativeApi/xtdata.html
---

# XtData (XtQuant 行情模块)

`xtdata` is the market data module of [XtQuant](http://dict.thinktrader.net/nativeApi/start_now.html), providing real-time and historical market data via the local miniQMT client.

> ⚠️ **Requires miniQMT running locally**. xtdata communicates with miniQMT via TCP to fetch data.

## Install

```bash
pip install xtquant
```

## Connect

```python
from xtquant import xtdata

xtdata.connect()  # connects to local miniQMT
```

Optionally specify data directory:

```python
xtdata.data_dir = r'D:\QMT\userdata_mini'
```

---

## Download historical data

Must download before accessing local data:

```python
# Download daily K-line
xtdata.download_history_data('000001.SZ', '1d', start_time='20240101', end_time='20240630')

# Download 1-minute K-line
xtdata.download_history_data('000001.SZ', '1m', start_time='20240101', end_time='20240630')

# Download tick data
xtdata.download_history_data('000001.SZ', 'tick', start_time='20240601', end_time='20240630')
```

## Get K-line data

```python
# Get market data (returns dict of DataFrames keyed by stock code)
data = xtdata.get_market_data_ex(
    [],                    # field_list, empty = all fields
    ['000001.SZ'],         # stock_list
    period='1d',           # tick, 1m, 5m, 15m, 30m, 1h, 1d, 1w, 1mon
    start_time='20240101',
    end_time='20240630',
    count=-1,              # -1 = all data
    dividend_type='front',  # none, front, back, front_ratio, back_ratio
    fill_data=True
)
df = data['000001.SZ']
# columns: open, high, low, close, volume, amount, settelementPrice, openInterest, preClose, suspendFlag
```

## Get local data (no download needed if already cached)

```python
data = xtdata.get_local_data(
    field_list=[],
    stock_list=['000001.SZ'],
    period='1d',
    start_time='20240101',
    end_time='20240630'
)
```

## Real-time subscription

### Subscribe single stock

```python
def on_data(datas):
    for stock_code, data in datas.items():
        print(stock_code, data)

xtdata.subscribe_quote('000001.SZ', period='tick', callback=on_data)
xtdata.run()  # block and receive callbacks
```

### Subscribe all stocks (全推)

```python
xtdata.subscribe_whole_quote(['SH', 'SZ'], callback=on_data)
# Markets: 'SH' (Shanghai), 'SZ' (Shenzhen), 'BJ' (Beijing)
xtdata.run()
```

## Get full snapshot

```python
data = xtdata.get_full_tick(['SH', 'SZ'])
# Returns dict: {stock_code: tick_data, ...}
```

## Financial data

```python
# Download financial data first
xtdata.download_financial_data(['000001.SZ'])

# Get financial data
data = xtdata.get_financial_data(['000001.SZ'])
```

Available tables: `Balance` (资产负债表), `Income` (利润表), `CashFlow` (现金流量表), `PershareIndex` (主要指标), `Capital` (股本表), `Top10holder`, `Top10flowholder`, `Holdernum`

## Ex-rights data (除权数据)

```python
data = xtdata.get_divid_factors('000001.SZ')
```

## Basic info

```python
# Get contract info
info = xtdata.get_instrument_detail('000001.SZ')
# Returns: InstrumentName, ExchangeID, ProductID, UpStopPrice, DownStopPrice, ...

# Get instrument type
itype = xtdata.get_instrument_type('000001.SZ')  # 'stock', 'index', 'fund', 'bond', etc.

# Trading days
days = xtdata.get_trading_dates('SH', start_time='20240101', end_time='20240630')

# Sector/block lists
blocks = xtdata.get_stock_list_in_sector('沪深A股')
```

## Index constituents

```python
# Download first
xtdata.download_index_weight()

# Get weights
weights = xtdata.get_index_weight('000300.SH')
# Returns: {stock_code: weight, ...}
```

## Convertible bond info

```python
xtdata.download_cb_data()
data = xtdata.get_cb_data()
```

## Available periods

`tick`, `1m`, `5m`, `15m`, `30m`, `1h`, `1d`, `1w`, `1mon`

## Level2 data fields

If your broker supports Level2:

- **l2quote** — Level2 实时行情快照
- **l2order** — Level2 逐笔委托
- **l2transaction** — Level2 逐笔成交
- **l2quoteaux** — 总买总卖
- **l2orderqueue** — 委买委卖队列

## Tips

- Always call `xtdata.download_history_data()` before `get_market_data_ex()` for first-time data access.
- Data is cached locally after download — subsequent reads are fast.
- `xtdata.run()` blocks the thread — use in a separate thread if combining with trading.
- Docs: http://dict.thinktrader.net/nativeApi/xtdata.html
