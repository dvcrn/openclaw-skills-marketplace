# Open Broker

Hyperliquid trading CLI. Execute orders, manage positions, and run trading strategies on Hyperliquid DEX.

## Installation

```bash
npm install -g openbroker
```

## Quick Start

```bash
# 1. Setup (generates wallet, creates config, approves builder fee)
openbroker setup

# 2. Fund your wallet with USDC on Arbitrum, then deposit at https://app.hyperliquid.xyz/

# 3. Start trading
openbroker account                          # View account info
openbroker buy --coin ETH --size 0.1        # Market buy
openbroker search --query GOLD              # Find markets
```

## Commands

### Setup

```bash
openbroker setup                # One-command setup (wallet + config + builder approval)
```

The setup command handles everything automatically:
- Generates a new wallet or accepts your existing private key
- Saves configuration to `~/.openbroker/.env` (permissions `0600`)
- Approves the builder fee (required for trading)

---

### Info Commands

#### `account` — View Account Info

Show balance, equity, margin, and positions summary.

```bash
openbroker account              # Balance, equity, margin, positions
openbroker account --orders     # Also show open orders
```

| Flag | Description | Default |
|------|-------------|---------|
| `--orders` | Include open orders in the output | — |

#### `positions` — View Positions

Detailed position view with entry/mark prices, PnL, leverage, liquidation distance, and margin used.

```bash
openbroker positions             # All open positions
openbroker positions --coin ETH  # Single position detail
```

| Flag | Description | Default |
|------|-------------|---------|
| `--coin` | Filter to a single asset | — |

#### `funding` — Funding Rates

View funding rates sorted by annualized rate. Highlights high-funding opportunities.

```bash
openbroker funding              # Top 20 by annualized rate
openbroker funding --top 50     # Top 50
openbroker funding --coin ETH   # Single asset
openbroker funding --sort oi    # Sort by open interest
```

| Flag | Description | Default |
|------|-------------|---------|
| `--top` | Number of results to show | `20` |
| `--coin` | Filter to a single asset | — |
| `--sort` | Sort by: `annualized`, `hourly`, or `oi` | `annualized` |
| `--all` | Show all assets including low OI | — |

#### `markets` — Market Data

Market data for perpetuals. Pass `--coin` for a detailed single-asset view with oracle price, min size, and more.

```bash
openbroker markets              # Top 30 perps by volume
openbroker markets --coin ETH   # Detailed view for ETH
openbroker markets --sort change --top 10  # Top movers
```

| Flag | Description | Default |
|------|-------------|---------|
| `--coin` | Detailed view for a single asset | — |
| `--top` | Number of results | `30` |
| `--sort` | Sort by: `volume`, `oi`, or `change` | `volume` |

#### `all-markets` — All Markets

Browse all available markets across main perps, HIP-3 perps, and spot — grouped by type.

```bash
openbroker all-markets                # Everything
openbroker all-markets --type perp    # Main perps only
openbroker all-markets --type hip3    # HIP-3 perps only
openbroker all-markets --type spot    # Spot only
openbroker all-markets --top 20       # Top 20 by volume
```

| Flag | Description | Default |
|------|-------------|---------|
| `--type` | Filter: `perp`, `spot`, `hip3`, or `all` | `all` |
| `--top` | Limit to top N by volume | — |
| `--verbose` | Show detailed output | — |

#### `search` — Search Markets

Search for assets by name across all providers (perps, HIP-3, spot). Shows funding comparison when an asset is listed on multiple venues.

```bash
openbroker search --query GOLD             # Find all GOLD markets
openbroker search --query ETH --type perp  # ETH perps only
openbroker search --query PURR --type spot # PURR spot only
```

| Flag | Description | Default |
|------|-------------|---------|
| `--query` | Search term (matches coin name) | **required** |
| `--type` | Filter: `perp`, `spot`, `hip3`, or `all` | `all` |
| `--verbose` | Show detailed output | — |

#### `spot` — Spot Markets & Balances

```bash
openbroker spot                  # All spot markets
openbroker spot --balances       # Your spot token balances
openbroker spot --coin PURR      # Filter by coin
openbroker spot --top 20         # Top 20 by volume
```

| Flag | Description | Default |
|------|-------------|---------|
| `--balances` | Show your spot token balances instead of markets | — |
| `--coin` | Filter by coin symbol | — |
| `--top` | Limit to top N by volume | — |
| `--verbose` | Show token metadata | — |

---

### Trading Commands

#### `buy` / `sell` / `market` — Market Orders

Execute market orders with slippage protection. `buy` and `sell` are shortcuts that set `--side` automatically.

```bash
openbroker buy --coin ETH --size 0.1
openbroker sell --coin BTC --size 0.01
openbroker buy --coin SOL --size 10 --slippage 100 --dry
openbroker buy --coin ETH --size 0.1 --verbose
```

| Flag | Description | Default |
|------|-------------|---------|
| `--coin` | Asset to trade (ETH, BTC, SOL, HYPE, etc.) | **required** |
| `--side` | Order direction: `buy` or `sell` (auto-set by buy/sell command) | **required** |
| `--size` | Order size in base asset | **required** |
| `--slippage` | Slippage tolerance in bps (basis points) | `50` (0.5%) |
| `--reduce` | Reduce-only order (won't increase position) | `false` |
| `--dry` | Preview order details without executing | — |
| `--verbose` | Show full API request/response | — |

#### `limit` — Limit Orders

Place a limit order at a specific price. Supports three time-in-force modes.

```bash
openbroker limit --coin ETH --side buy --size 1 --price 3000
openbroker limit --coin BTC --side sell --size 0.1 --price 100000 --tif ALO
openbroker limit --coin SOL --side buy --size 10 --price 150 --reduce
```

| Flag | Description | Default |
|------|-------------|---------|
| `--coin` | Asset to trade | **required** |
| `--side` | `buy` or `sell` | **required** |
| `--size` | Order size in base asset | **required** |
| `--price` | Limit price | **required** |
| `--tif` | Time in force: `GTC` (rest on book), `IOC` (fill or cancel), `ALO` (post-only, maker only) | `GTC` |
| `--reduce` | Reduce-only order | `false` |
| `--dry` | Preview without executing | — |

#### `trigger` — Trigger Orders (Conditional TP/SL)

Place conditional orders that activate when price reaches a trigger level. Used for stop losses, take profits, and conditional entries.

```bash
# Take profit: sell HYPE when price rises to $40
openbroker trigger --coin HYPE --side sell --size 0.5 --trigger 40 --type tp

# Stop loss: sell HYPE when price drops to $30
openbroker trigger --coin HYPE --side sell --size 0.5 --trigger 30 --type sl

# Buy stop: buy BTC on breakout above $75k
openbroker trigger --coin BTC --side buy --size 0.01 --trigger 75000 --type sl --reduce false
```

| Flag | Description | Default |
|------|-------------|---------|
| `--coin` | Asset to trade | **required** |
| `--side` | Order side when triggered: `buy` or `sell` | **required** |
| `--size` | Order size in base asset | **required** |
| `--trigger` | Trigger price (order activates at this level) | **required** |
| `--type` | Order type: `tp` (take profit) or `sl` (stop loss) | **required** |
| `--limit` | Custom limit price when triggered (overrides auto-calculation) | auto |
| `--slippage` | Slippage for stop loss limit price in bps | `100` (1%) |
| `--reduce` | Reduce-only order | `true` |
| `--dry` | Preview without placing | — |
| `--verbose` | Show debug output | — |

**Trigger behavior:**
- TP: Limit price = trigger price (favorable fill)
- SL: Limit price = trigger ± slippage (ensures fill in fast markets)

#### `tpsl` — Set TP/SL on Existing Position

Attach take-profit and/or stop-loss trigger orders to an open position. Supports absolute prices, percentage offsets, and breakeven stops.

```bash
openbroker tpsl --coin HYPE --tp 40 --sl 30          # Absolute prices
openbroker tpsl --coin ETH --tp +10% --sl -5%        # Percentage from entry
openbroker tpsl --coin HYPE --tp +10% --sl entry      # Breakeven stop
openbroker tpsl --coin ETH --sl -5%                   # Stop loss only
openbroker tpsl --coin ETH --tp 4000 --sl 3500 --size 0.5  # Partial position
```

| Flag | Description | Default |
|------|-------------|---------|
| `--coin` | Asset with an open position | **required** |
| `--tp` | Take profit price: absolute (`40`), percentage (`+10%`), or `entry` | — |
| `--sl` | Stop loss price: absolute (`30`), percentage (`-5%`), or `entry` | — |
| `--size` | Size to protect (for partial TP/SL) | full position |
| `--sl-slippage` | Stop loss slippage buffer in bps | `100` (1%) |
| `--dry` | Preview orders without placing | — |
| `--verbose` | Show debug output | — |

Shows risk/reward ratio and potential profit/loss before placing.

#### `cancel` — Cancel Orders

```bash
openbroker cancel --all                    # Cancel all open orders
openbroker cancel --coin ETH               # Cancel all ETH orders
openbroker cancel --coin ETH --oid 123456  # Cancel specific order
openbroker cancel --all --dry              # Preview what would be cancelled
```

| Flag | Description | Default |
|------|-------------|---------|
| `--coin` | Cancel orders for a specific coin only | — |
| `--oid` | Cancel a specific order by ID | — |
| `--all` | Cancel all open orders | — |
| `--dry` | Show orders without cancelling | — |

---

### Advanced Execution

#### `twap` — Time-Weighted Average Price

Split a large order into smaller slices executed at regular intervals to minimize market impact.

```bash
# Buy 1 ETH over 1 hour (auto ~12 slices)
openbroker twap --coin ETH --side buy --size 1 --duration 3600

# Sell 0.5 BTC over 30 min, 6 slices, randomized timing
openbroker twap --coin BTC --side sell --size 0.5 --duration 1800 --intervals 6 --randomize 20
```

| Flag | Description | Default |
|------|-------------|---------|
| `--coin` | Asset to trade | **required** |
| `--side` | `buy` or `sell` | **required** |
| `--size` | Total order size in base asset | **required** |
| `--duration` | Total execution time in seconds | **required** |
| `--intervals` | Number of slices | 1 per 5 min |
| `--randomize` | Randomize timing by ±X percent | `0` |
| `--slippage` | Slippage per slice in bps | `50` |
| `--dry` | Show execution plan without trading | — |
| `--verbose` | Show debug output | — |

Reports VWAP, actual slippage, fill rate, and total execution time.

#### `scale` — Scale In/Out

Place a grid of limit orders to scale into or out of a position. Three distribution modes control how size is allocated across price levels.

```bash
openbroker scale --coin ETH --side buy --size 1 --levels 5 --range 2
openbroker scale --coin ETH --side buy --size 2 --levels 8 --range 5 --distribution exponential
openbroker scale --coin BTC --side sell --size 0.5 --levels 4 --range 3 --reduce
```

| Flag | Description | Default |
|------|-------------|---------|
| `--coin` | Asset to trade | **required** |
| `--side` | `buy` or `sell` | **required** |
| `--size` | Total order size in base asset | **required** |
| `--levels` | Number of price levels (orders) | **required** |
| `--range` | Price range from current mid in % | **required** |
| `--distribution` | Size distribution: `linear` (more at better prices), `exponential` (much more), `flat` (equal) | `linear` |
| `--tif` | Time in force: `GTC` or `ALO` | `GTC` |
| `--reduce` | Reduce-only orders (for scaling out) | `false` |
| `--dry` | Show order grid without placing | — |
| `--verbose` | Show debug output | — |

#### `bracket` — Bracket Order (Entry + TP + SL)

Complete trade setup in one command. Supports market or limit entry with automatic take-profit and stop-loss trigger orders.

```bash
openbroker bracket --coin ETH --side buy --size 0.5 --tp 3 --sl 1.5
openbroker bracket --coin BTC --side sell --size 0.1 --entry limit --price 100000 --tp 5 --sl 2
```

| Flag | Description | Default |
|------|-------------|---------|
| `--coin` | Asset to trade | **required** |
| `--side` | Entry direction: `buy` (long) or `sell` (short) | **required** |
| `--size` | Position size in base asset | **required** |
| `--tp` | Take profit distance in % from entry | **required** |
| `--sl` | Stop loss distance in % from entry | **required** |
| `--entry` | Entry type: `market` or `limit` | `market` |
| `--price` | Entry price (required if `--entry limit`) | — |
| `--slippage` | Slippage for market entry in bps | `50` |
| `--dry` | Show bracket plan without executing | — |
| `--verbose` | Show debug output | — |

Executes in 3 steps: Entry → TP trigger → SL trigger. Shows risk/reward ratio and potential profit/loss.

#### `chase` — Chase Order

Follow the price with ALO (post-only) limit orders to get maker fills and avoid taker fees.

```bash
openbroker chase --coin ETH --side buy --size 0.5
openbroker chase --coin SOL --side buy --size 10 --offset 1 --timeout 60 --max-chase 50
openbroker chase --coin BTC --side sell --size 0.1 --offset 2 --timeout 600
```

| Flag | Description | Default |
|------|-------------|---------|
| `--coin` | Asset to trade | **required** |
| `--side` | `buy` or `sell` | **required** |
| `--size` | Order size in base asset | **required** |
| `--offset` | Offset from mid price in bps | `5` (0.05%) |
| `--timeout` | Max time to chase in seconds | `300` (5 min) |
| `--interval` | Price check / order update interval in ms | `2000` |
| `--max-chase` | Max price to chase to in bps from start | `100` (1%) |
| `--reduce` | Reduce-only order | — |
| `--dry` | Show chase parameters without executing | — |
| `--verbose` | Show debug output | — |

Uses ALO orders exclusively, guaranteeing maker rebates. Stops when filled, timed out, or max chase reached.

---

### Strategies

#### `funding-arb` — Funding Arbitrage

Collect funding payments by taking positions opposite to the majority. Monitors funding continuously and auto-closes when rates drop.

```bash
openbroker funding-arb --coin ETH --size 5000 --min-funding 25
openbroker funding-arb --coin BTC --size 10000 --duration 24 --check 30
openbroker funding-arb --coin ETH --size 5000 --dry
```

| Flag | Description | Default |
|------|-------------|---------|
| `--coin` | Asset to trade | **required** |
| `--size` | Position size in USD notional | **required** |
| `--min-funding` | Minimum annualized funding rate to enter (%) | `20` |
| `--max-funding` | Maximum rate — avoid extreme/squeeze risk (%) | `200` |
| `--duration` | How long to run in hours | ∞ |
| `--check` | Funding check interval in minutes | `60` |
| `--close-at` | Close position when funding drops below X% | `5` |
| `--mode` | `perp` (directional) or `hedge` (delta neutral — not yet implemented) | `perp` |
| `--dry` | Show opportunity analysis without trading | — |
| `--verbose` | Show debug output | — |

**Note:** Hyperliquid funding is paid **hourly** (not 8h like CEXs). Annualized = hourly × 8,760.

#### `grid` — Grid Trading

Automatically buy low and sell high within a price range. Replaces filled orders on the opposite side.

```bash
openbroker grid --coin ETH --lower 3000 --upper 4000 --grids 10 --size 0.1
openbroker grid --coin BTC --lower 90000 --upper 100000 --grids 5 --size 0.01 --mode long
```

| Flag | Description | Default |
|------|-------------|---------|
| `--coin` | Asset to trade | **required** |
| `--lower` | Lower bound of grid (price) | **required** |
| `--upper` | Upper bound of grid (price) | **required** |
| `--grids` | Number of grid levels | `10` |
| `--size` | Size per grid level in base asset | — |
| `--total-size` | OR total size to distribute across grids | — |
| `--mode` | `neutral` (buy+sell), `long` (buys only), `short` (sells only) | `neutral` |
| `--refresh` | Rebalance check interval in seconds | `60` |
| `--duration` | How long to run in hours | ∞ |
| `--dry` | Show grid plan without placing orders | — |
| `--verbose` | Show debug output | — |

Handles graceful shutdown (Ctrl+C) — cancels all grid orders and prints PnL summary.

#### `dca` — Dollar Cost Averaging

Accumulate a position over time with regular purchases at fixed USD amounts.

```bash
openbroker dca --coin ETH --amount 100 --interval 1h --count 24
openbroker dca --coin BTC --total 5000 --interval 1d --count 30
```

| Flag | Description | Default |
|------|-------------|---------|
| `--coin` | Asset to accumulate | **required** |
| `--amount` | USD amount per purchase | — |
| `--total` | OR total USD to invest (calculates per-purchase) | — |
| `--interval` | Time between purchases: `Xm`, `Xh`, `Xd`, `Xw` | **required** |
| `--count` | Number of purchases to make | **required** |
| `--slippage` | Slippage tolerance in bps | `50` |
| `--dry` | Show DCA plan and schedule without executing | — |
| `--verbose` | Show debug output | — |

Reports running average price, total acquired, and unrealized PnL after completion.

#### `mm-maker` — Market Making (ALO / Maker-Only)

Provide liquidity using ALO (Add Liquidity Only) orders that are **rejected** if they would cross the spread. Guarantees you always earn the maker rebate (~0.3 bps). Reads the actual order book for pricing.

```bash
openbroker mm-maker --coin HYPE --size 1 --offset 1
openbroker mm-maker --coin ETH --size 0.1 --offset 2 --max-position 0.5
```

| Flag | Description | Default |
|------|-------------|---------|
| `--coin` | Asset to market make | **required** |
| `--size` | Order size on each side (base asset) | **required** |
| `--offset` | Offset from best bid/ask in bps | `1` |
| `--max-position` | Max net position before stopping that side | 3× size |
| `--skew-factor` | How aggressively to skew for inventory | `2.0` |
| `--refresh` | Refresh interval in milliseconds | `2000` |
| `--duration` | How long to run in minutes | ∞ |
| `--dry` | Show setup without trading | — |
| `--verbose` | Show debug output | — |

**Fee structure:** Taker ~2.5 bps (you pay), Maker ~0.3 bps (you earn). ALO-only = always earn.

#### `mm-spread` — Market Making (Spread-Based)

Place bid/ask quotes around the mid price, earning the spread when both sides fill. Includes inventory skewing and cooldown after fills.

```bash
openbroker mm-spread --coin ETH --size 0.1 --spread 10
openbroker mm-spread --coin BTC --size 0.01 --spread 5 --max-position 0.03 --cooldown 3000
```

| Flag | Description | Default |
|------|-------------|---------|
| `--coin` | Asset to market make | **required** |
| `--size` | Order size on each side (base asset) | **required** |
| `--spread` | Total spread width in bps from mid | **required** |
| `--skew-factor` | How aggressively to skew for inventory | `2.0` |
| `--max-position` | Maximum net position | 3× size |
| `--cooldown` | Cooldown after fill before same-side requote (ms) | `5000` |
| `--refresh` | Refresh interval in milliseconds | `2000` |
| `--duration` | How long to run in minutes | ∞ |
| `--dry` | Show strategy parameters without trading | — |
| `--verbose` | Show debug output | — |

**Inventory management:** When LONG → bid wider, ask tighter. When SHORT → bid tighter, ask wider. At max position → stops quoting that side.

---

## Global Options

| Flag | Description |
|------|-------------|
| `--help`, `-h` | Show help for a command |
| `--dry` | Preview without executing (all trading/strategy commands) |
| `--verbose` | Show debug output including API requests/responses |
| `--version`, `-v` | Print the CLI version |

## Safety

**Always use `--dry` first** to preview any operation:

```bash
openbroker buy --coin ETH --size 0.1 --dry
```

**Use testnet** for testing:

```bash
export HYPERLIQUID_NETWORK="testnet"
```

## Configuration

Config is loaded from these locations (in order of priority):
1. Environment variables
2. `.env` file in current directory
3. `~/.openbroker/.env` (global config)

Run `openbroker setup` to create the global config, or set environment variables:

```bash
export HYPERLIQUID_PRIVATE_KEY=0x...     # Required: wallet private key
export HYPERLIQUID_NETWORK=mainnet       # Optional: mainnet (default) or testnet
export HYPERLIQUID_ACCOUNT_ADDRESS=0x... # Optional: for API wallets
```

### API Wallet Setup

For automated trading, use an API wallet:

```bash
export HYPERLIQUID_PRIVATE_KEY="0x..."        # API wallet private key
export HYPERLIQUID_ACCOUNT_ADDRESS="0x..."    # Main account address
```

**Note:** Builder fee must be approved with the main wallet first. Sub-accounts cannot approve builder fees. After approval, you can switch to using the API wallet for trading.

## Builder Fee

Open Broker charges **1 bps (0.01%)** per trade to fund development. The builder fee is automatically approved during `openbroker setup`.

```bash
openbroker approve-builder --check       # Check approval status
openbroker approve-builder               # Retry approval if needed
openbroker approve-builder --max-fee "0.05%"  # Custom max fee
```

| Flag | Description | Default |
|------|-------------|---------|
| `--check` | Only check current approval status, don't approve | — |
| `--max-fee` | Maximum fee rate to approve | `0.1%` |
| `--builder` | Custom builder address (advanced) | Open Broker |
| `--verbose` | Show debug output | — |

## Development

For local development without global install:

```bash
git clone https://github.com/monemetrics/openbroker.git
cd openbroker
npm install
npx tsx scripts/info/account.ts
```

## License

MIT
