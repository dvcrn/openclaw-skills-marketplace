# 📈 stock-price-query

An [OpenClaw](https://github.com/openclaw/openclaw) skill for querying real-time stock prices across multiple markets.

## Features

- **Multi-market support**: A-shares (Shanghai & Shenzhen), Hong Kong stocks, and US stocks
- **Auto market detection**: Automatically identifies the market based on stock code format
- **Zero dependencies**: Pure Python 3 standard library, no external packages required
- **Structured output**: Returns JSON with price, change, volume, and more

## Supported Markets

| Market | Code Format | Example |
|--------|------------|---------|
| Shanghai (SH) | 6-digit starting with 6 | `600519` (Kweichow Moutai) |
| Shenzhen (SZ) | 6-digit starting with 0/3 | `300750` (CATL) |
| Hong Kong (HK) | Up to 5 digits | `00700` (Tencent) |
| US | Alphabetic ticker | `AAPL` (Apple) |

## Usage

### As an OpenClaw Skill

Copy this repository to your OpenClaw skills directory:

```bash
# User-level
cp -r stock-price-query ~/.openclaw/skills/

# Or project-level
cp -r stock-price-query /path/to/project/skills/
```

Then ask naturally in OpenClaw:

- "What's the current price of AAPL?"
- "查一下贵州茅台的股价"
- "How is Tencent doing today?"

### Standalone

```bash
python3 scripts/stock_query.py <stock_code> [market]

# Examples
python3 scripts/stock_query.py 600519        # A-share (auto-detect)
python3 scripts/stock_query.py AAPL          # US stock
python3 scripts/stock_query.py 00700 hk      # Hong Kong stock
```

### Output Example

```json
{
  "code": "600519",
  "name": "贵州茅台",
  "market": "sh",
  "current_price": 1466.80,
  "change": -18.50,
  "change_percent": -1.25,
  "open": 1521.00,
  "high": 1524.40,
  "low": 1463.60,
  "prev_close": 1485.30,
  "volume": 4191300,
  "amount": 6198840000.00,
  "time": "20260224161416",
  "status": "success"
}
```

## Project Structure

```
stock-price-query/
├── SKILL.md              # OpenClaw skill definition
├── CHANGELOG.md          # Version history
├── README.md             # This file
├── scripts/
│   └── stock_query.py    # Query script (Python 3)
└── references/
    └── api-docs.md       # API documentation
```

## Data Source

Uses Tencent Finance API (`qt.gtimg.cn`) — free, no API key required, no special headers needed.

## License

MIT
