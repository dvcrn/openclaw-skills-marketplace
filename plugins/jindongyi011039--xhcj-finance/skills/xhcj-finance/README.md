# Openclaw CLI Tool

A CLI tool for interacting with Xinhua Finance APIs to retrieve market data and news.

## Features

1. **Read Xinhua Finance Market Data**
   - Query real-time and historical market data
   - Support for various financial instruments

2. **Read Xinhua Finance News**
   - Retrieve latest financial news
   - Support for different news categories

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Link the CLI tool:
   ```bash
   npm link
   ```

## Configuration

Set the `XHCJ_API_KEY` environment variable with your Xinhua Finance API key:

### Windows
```powershell
Set-Item -Path "Env:XHCJ_API_KEY" -Value "your-api-key"
```

### Linux/macOS
```bash
export XHCJ_API_KEY="your-api-key"
```

## Usage

### Query Market Data
```bash
xhcj-finance market --symbol <symbol>
```

### Query Kline Data
```bash
xhcj-finance kline --symbol <symbol>
```

### Query Stock Symbol
```bash
xhcj-finance symbol --name <name>
```

### Get News
```bash
xhcj-finance news [--category <category>] [--limit <limit>]
```

**Parameters**:
- `--category` (optional): News category (1-股票, 2-商品期货, 3-外汇, 4-债券, 5-宏观, 9-全部, default 9)
- `--limit` (optional): Number of results to return (default 10, max 20)

## Examples

1. **Query market data for a specific symbol**:
   ```bash
   xhcj-finance market --symbol 600000.SS
   ```

2. **Query kline data for a specific symbol**:
   ```bash
   xhcj-finance kline --symbol 600000.SS
   ```

3. **Query stock symbol by name**:
   ```bash
   xhcj-finance symbol --name "中国平安"
   ```

4. **Get latest news**:
   ```bash
   xhcj-finance news --limit 10
   ```

5. **Get news from a specific category**:
   ```bash
   xhcj-finance news --category 1 --limit 5
   ```
