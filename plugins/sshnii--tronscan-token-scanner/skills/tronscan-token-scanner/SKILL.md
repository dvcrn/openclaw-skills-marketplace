---
name: tronscan-token-scanner
description: "Scan TRON tokens for total supply, market cap, price, rating, launch time, holders.\n Includes TRX: TRX price, TRX supply, market cap, daily net change, and supply trend.\n Use when user asks \"how is this token\", \"USDT price\", \"top holders\", \"TRX market cap\", \"token due diligence\", \"supply of contract address\", or provides a token contract address.\n Do NOT use for token list or trending rankings (use tronscan-token-list or tronscan-data-insights)."
---

# Token Scanner

## Overview

| Tool | Function | Use Case |
|------|----------|----------|
| getTokenPrice | Token price (default TRX) | TRX price or any token price |
| getFunds | TRX supply & market | TRX supply, market cap, burn |
| getTrxVolume | TRX history | TRX historical price, volume, market cap |
| getTurnover | TRX turnover | TRX turnover, supply, revenue, mint/burn |
| getTrxVolumeSourceList | TRX price sources | TRX price data source list |
| getTrc20TokenDetail | TRC20/721/1155 detail | Name, symbol, supply, holders, price |
| getTrc10TokenDetail | TRC10 detail | Name, issuer, supply, description |
| getTrc20TokenHolders | TRC20/721/1155 holders | Holder list, balance, share |
| getTrc10TokenHolders | TRC10 holders | TRC10 holder list |
| getTokenPositionDistribution | Position distribution | Holder count by balance range |
| getTrc20TotalSupply | TRC20 supply | Circulating / total supply |
| getTrc721Inventory | TRC721 inventory | NFT contract inventory |
| getTrc1155Inventory | TRC1155 inventory | Multi-token contract inventory |

## Use Cases

1. **TRX price, TRX supply, TRX market cap**: Use `getTokenPrice` (default token is TRX) for current price; use `getFunds` for real-time TRX supply, market cap, and burn; use `getTrxVolume` for historical price/volume; use `getTurnover` for supply, mint/burn, turnover.
2. **Token Overview**: Get name, symbol, supply, holders, price via `getTrc20TokenDetail` or `getTrc10TokenDetail`.
3. **Holder Analysis**: Use `getTrc20TokenHolders` / `getTrc10TokenHolders` for list; use `getTokenPositionDistribution` for concentration.
4. **Price & Valuation**: Use `getTokenPrice` and detail tools for market cap.
5. **Supply**: Use `getTrc20TotalSupply` for TRC20 supply/circulation.
6. **Launch Time**: Available in token detail responses (creation/deploy time).
7. **NFT / Multi-token**: Use `getTrc721Inventory` and `getTrc1155Inventory` for inventory.

## MCP Server

- **Prerequisite**: [TronScan MCP Guide](https://mcpdoc.tronscan.org)

## Tools

### getTokenPrice

- **API**: `getTokenPrice` — Get token price (default: TRX)
- **Use when**: User asks for "TRX price", "current TRX price", or any token price.
- **Note**: Omit or pass default to get TRX price.

### getFunds

- **API**: `getFunds` — Get TRX real-time supply, market cap, and burn data
- **Use when**: User asks for "TRX supply", "TRX circulation", "TRX market cap", or "TRX burn".

### getTrxVolume

- **API**: `getTrxVolume` — Get TRX historical price, volume, and market cap data
- **Use when**: User asks for "TRX history", "TRX price history", or "TRX volume trend".
- **Input**: startTimestamp, endTimestamp, limit, source.

### getTurnover

- **API**: `getTurnover` — Get TRX turnover, supply, revenue, mint and burn statistics
- **Use when**: User asks for "TRX turnover", "TRX mint/burn", or "TRX supply change".
- **Input**: from, start, end, type (as per API).

### getTrxVolumeSourceList

- **API**: `getTrxVolumeSourceList` — Get TRX price data source list
- **Use when**: User asks for "TRX price source" or "where TRX price comes from".

### getTrc20TokenDetail

- **API**: `getTrc20TokenDetail` — Get TRC20/TRC721/TRC1155 token details (name, symbol, supply, holders, price, etc.)
- **Use when**: User asks for "token info", "token details", or specifies a contract address.
- **Input**: Contract address (and token type if needed).

### getTrc10TokenDetail

- **API**: `getTrc10TokenDetail` — Get TRC10 token details (name, abbreviation, issuer, supply, description, etc.)
- **Use when**: Token is TRC10 (native asset).

### getTrc20TokenHolders / getTrc10TokenHolders

- **API**: `getTrc20TokenHolders` — Get TRC20/TRC721/TRC1155 holder list (address, balance, share); `getTrc10TokenHolders` — Get TRC10 holder list
- **Use when**: User asks for "token holders" or "top holders".

### getTokenPositionDistribution

- **API**: `getTokenPositionDistribution` — Get token position distribution (holder count and share by balance range)
- **Use when**: User asks for "holder distribution" or "concentration".

### getTrc20TotalSupply

- **API**: `getTrc20TotalSupply` — Get TRC20 circulating supply and total supply
- **Use when**: User asks for "supply" or "circulation" of a TRC20.

## Token Rating (level)

TronScan returns `level` as a string 0–4. Mapping:

| Level | Rating | Description |
|-------|--------|-------------|
| 0 | Unknown | Cannot be determined |
| 1 | Neutral | Neutral |
| 2 | OK | Passes basic security checks |
| 3 | Suspicious | Suspicious |
| 4 | Unsafe | Unsafe |

When presenting to users, convert the numeric value to the rating label above.

## Workflow: Query Token Info

> User: "What is USDT?" or "Tell me about this token" (provides token name/symbol as text)

1. **Resolve text to address** — If user provides name/symbol (e.g. "USDT", "BTT"), use **tronscan-search** `search` with `term` and `type: "token"` to get contract address (`token_id` in result). If user already provides contract address, skip this step.
2. **tronscan-token-scanner** — Call `getTrc20TokenDetail` (or `getTrc10TokenDetail`) with the contract address / asset ID from step 1.
3. **Convert level** — Map raw `level` (0–4) to rating text before presenting:
   - 0 → Unknown | 1 → Neutral | 2 → OK | 3 → Suspicious | 4 → Unsafe
4. **Optional** — `getTrc20TokenHolders` / `getTokenPositionDistribution` for holder list; `getTokenPrice` for USD conversion if values are in TRX.
5. **Present to user** — Return name, symbol, supply, holders, price, market cap (prefer USD), and **rating** (converted text, not raw level).

**Key**: Never show raw `level` (e.g. "2") to users; always convert to rating label (e.g. "OK").

## Workflow: Query TRX Info

> User: "What is TRX?" or "TRX price/supply/market cap/detail/info" (queries TRON native token)

1. **tronscan-token-scanner** — Call `getTrc10TokenDetail` with **asset ID = 0**. TRX is TRON's native token (TRC10), id = 0.
2. **Enrich with** — `getFunds` (supply, market cap, burn); `getTokenPrice` (current USD price); `getTurnover` (turnover, mint/burn); `getTrxVolume` (24h volume, price change, historical); `getTrc10TokenHolders` (holder count). For total/yesterday transfer count, use **tronscan-transaction-info** `getTransactionStatistics` or **tronscan-data-insights** if needed.
3. **Present to user** — Return a rich summary including:
   - **Basic**: name, symbol, description, issuance time
   - **Supply**: total supply, circulating supply
   - **Price**: current price (USD), 24h change
   - **Market**: market cap (USD), 24h volume
   - **Chain**: burn amount, turnover, mint/burn stats (if available)
   - **Activity**: holders, total transfer count, yesterday's transfer count
   - **Links**: whitepaper, media links (if available)

**Note**: No search step needed; TRX is always asset ID 0.

## Workflow: Search by Name, Then Analyze

> User: "What is the USDT contract address on TRON? Who are the top holders?"

1. **tronscan-search** — Use `search` with `term: "USDT"`, `type: "token"` to resolve name/symbol to TRC20 contract address (`token_id` in result).
2. **tronscan-token-scanner** — Call `getTrc20TokenDetail` with contract address for supply, holders, price, market cap, rating.
3. **tronscan-token-scanner** — `getTrc20TokenHolders` / `getTokenPositionDistribution` for top holders and concentration.
4. Optional **tronscan-account-profiler** — For top holder addresses, call `getAccountDetail` or `getTokenAssetOverview` for wallet profile.

**Data handoff**: Contract address from step 1 feeds into tronscan-token-scanner in steps 2–3; holder addresses from step 3 feed into tronscan-account-profiler in step 4.

## Troubleshooting

- **MCP connection failed**: If you see "Connection refused", verify TronScan MCP is connected in Settings > Extensions.
- **API rate limit / 429**: TronScan API has call count and frequency limits when no API key is used. If you encounter rate limiting or 429 errors, go to [TronScan Developer API](https://tronscan.org/#/developer/api) to apply for an API key, then add it to your MCP configuration and retry.

### Invalid contract address or asset ID
TRC20/TRC721/TRC1155 require contract address; TRC10 requires asset ID. Do not mix them.

## Notes

- For TRX: use `getTokenPrice`, `getFunds`, `getTrxVolume`, `getTurnover` for price, supply, market cap, and trends.
- For "rating" or risk metrics, combine with contract analysis (contract verification, holders, distribution).
- TRC20/TRC721/TRC1155 use contract address; TRC10 uses asset ID.
- **market_cap, price, volume units**: Check whether values are in USD or TRX. Prefer returning USD to users. If only TRX is available, query TRX price via `getTokenPrice` and convert to USD before returning.
