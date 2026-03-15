---
name: trongrid-token-list
description: "Browse and rank TRC-20 and TRC-10 tokens on TRON with price, volume, market cap, holder count, and category filters. Use when a user wants to discover tokens, see token rankings, find trending tokens, compare tokens by market cap, or explore categories like stablecoins and DeFi tokens on TRON."
---

# Token List

Comprehensive listing of TRC-20 and TRC-10 tokens on TRON with market metrics, rankings, and category filters for token discovery and market overview.

# MCP Server
- **Prerequisite**: [TronGrid MCP Guide](https://developers.tron.network/reference/mcp-api)

## Instructions

### Step 1: Fetch TRC-10 Asset List

For TRC-10 tokens (legacy standard):

1. `listAllAssets` or `getAssetIssueList` — Full TRC-10 list
2. `getPaginatedAssetIssueList` — For paginated browsing
3. Each asset includes: name, abbreviation, total supply, precision, issuer, description, URL

### Step 2: Fetch TRC-20 Token Data

No single "list all TRC-20" endpoint exists. Use a combined approach:

1. **Web search** for current TRC-20 rankings from TronScan, CoinGecko, or CoinMarketCap (filter: TRON network)
2. For each top token, call `getTrc20Info` with contract address for on-chain metadata
3. Call `getTrc20TokenHolders` for holder distribution data

### Step 3: Enrich Token Data

For each token, gather:

**On-chain** (MCP tools):
- Name, symbol, decimals (`getTrc20Info`)
- Holder count (`getTrc20TokenHolders`)
- Contract info (`getContractInfo`)
- Recent activity (`getContractTransactions`)

**Market** (web search):
- Price (USD), 24h change (%), volume, market cap, FDV

### Step 4: Rank and Categorize

**By Market Cap**: Large (>$1B), Mid ($100M-$1B), Small ($10M-$100M), Micro (<$10M)

**By Category**:
- Stablecoins: USDT, USDC, TUSD, USDJ
- DeFi: SUN, JST, WIN
- GameFi / Metaverse
- Infrastructure / Utility
- Meme tokens

**By Performance**: Top gainers, top losers, highest volume, most holders

### Step 5: Compile Token List

```
## TRON Token Rankings

### Top TRC-20 by Market Cap
| Rank | Token | Symbol | Price | 24h Change | Volume | Market Cap | Holders |
|------|-------|--------|-------|-----------|--------|-----------|---------|
| 1 | Tether | USDT | $1.00 | +0.01% | $XX.XB | $XX.XB | X,XXX,XXX |

### Top Gainers (24h)
| Token | Symbol | Price | 24h Change |
|-------|--------|-------|-----------|

### Top Losers (24h)
| Token | Symbol | Price | 24h Change |
|-------|--------|-------|-----------|

### Most Active (by Tx Count)
| Token | Symbol | 24h Transactions |
|-------|--------|-----------------|

### TRC-10 Tokens (Top by Supply)
| Token | ID | Total Supply | Issuer |
|-------|----|-------------|--------|
```

## Quality Signals

When evaluating tokens, flag these patterns:
- Low holder count + high market cap = potential wash trading
- Growing holder count = positive adoption signal
- Unverified contract + mint/pause functions = caution
- For "best" or "quality" queries, weigh holder count, tx activity, and contract verification heavily

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| No market data | Token not listed on price aggregators | Show on-chain data only (holders, tx count), note "No market data available" |
| `getTrc20Info` returns empty | Invalid contract address | Skip token or note as unresolvable |
| Too many tokens to process | User asks for full list | Limit to top 20-50 by market cap, offer pagination |
| TRC-10 list very large | Thousands of TRC-10 assets | Use `getPaginatedAssetIssueList` with reasonable limit (20-50) |

## Examples

- [Top TRON tokens by market cap](examples/top-tron-tokens.md)
- [DeFi tokens on TRON](examples/defi-tokens.md)
