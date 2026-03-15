---
name: tronscan-data-insights
description: "TRON network insights: new accounts, daily tx count, tx type distribution,\n hot tokens, hot contracts, top accounts by tx count or staked TRX.\n Use when user asks \"what is happening on TRON\", \"new accounts\", \"daily new addresses\", \"hot tokens\", \"network activity\", \"accounts with most TRX transfers yesterday\", \"TRX staking rankings\".\n Do NOT use for single token details (use tronscan-token-scanner); single address profiling (use tronscan-account-profiler); non-TRX token transfer count rankings; non-TRX token transfer volume rankings."
---

# Data Insights

## Overview

| Tool | Function | Use Case |
|------|----------|----------|
| getDailyAccounts | Daily new accounts | Daily new addresses (newAddressSeen), up to 2000 days |
| getTransactionStatistics | Tx statistics | Total tx, token tx volume, aggregates |
| getTransferStatistics | Transfer stats | Transfer activity by token type |
| getTriggerStatistic | Contract triggers | Daily contract call count |
| getTop10 | Top10 rankings | Multiple dimensions (time, category) |
| getHotSearch | Hot tokens/contracts | Hot tokens and contracts with metrics |
| getHomepageData | Homepage data | TPS, node count, overview, TVL, frozen |
| getCurrentTps | Current TPS | Current TPS, latest height, historical max TPS |
| getTriggerAmountStatistic | Trigger by date | Contract call volume distribution by date |
| getContractCallerStatisticOverview | Caller overview | Contract caller stats (default 7d) |

## Use Cases

1. **New Accounts**: Use `getDailyAccounts` for daily new addresses (newAddressSeen), as an activity proxy—not precise DAU.
2. **Daily Transaction Count**: Use `getTransactionStatistics` and `getTriggerStatistic` for tx and contract call volume.
3. **Transaction Type Distribution**: Use `getTransactionStatistics` and `getTransferStatistics` for type/segment distribution.
4. **Hot Tokens**: Use `getHotSearch` for trending tokens with price and activity.
5. **Hot Contracts**: Use `getHotSearch` and `getTriggerStatistic` or `getTop10` for hot contracts.
6. **Top Accounts by Tx Count**: Use `getTop10` with appropriate category (e.g. by tx count).
7. **Top Account by Staked TRX**: Use `getTop10` or account list sorted by frozen/stake (category as per API).


## MCP Server

- **Prerequisite**: [TronScan MCP Guide](https://mcpdoc.tronscan.org)

## Tools

### getDailyAccounts

- **API**: `getDailyAccounts` — Get daily new account data (default last 15 days, max 2000 days)
- **Data source**: Returns `newAddressSeen` (daily new addresses). This is an activity proxy, not precise DAU.
- **Use when**: User asks for "new accounts", "daily new addresses", or "new accounts per day".
- **If user asks for DAU**: First declare that "this API returns daily new addresses, not precise DAU; it can be used as a reference but must not be presented as exact DAU".
- **Input**: Optional start/end or day count.
- **Response**: Daily new account series.

### getTransactionStatistics

- **API**: `getTransactionStatistics` — Get transaction statistics (total tx, token tx volume, etc.)
- **Use when**: User asks for "transaction count", "tx volume", or "network activity".
- **Response**: Aggregated tx and token volume.

### getTransferStatistics

- **API**: `getTransferStatistics` — Get transfer statistics by token type
- **Use when**: User asks for "transfer distribution" or "tx type distribution".
- **Response**: Transfer activity by type.

### getTriggerStatistic

- **API**: `getTriggerStatistic` — Get daily contract trigger data in a time range
- **Use when**: User asks for "contract calls per day" or "smart contract activity".
- **Input**: Time range.
- **Response**: Daily trigger count.

### getTop10

- **API**: `getTop10` — Get Top10 rankings (multiple time/category dimensions)
- **Use when**: User asks for "top 10 accounts", "most tx", "most staked TRX", or similar rankings.
- **Input**: Category, time range (as per API).
- **Response**: Top 10 list for selected dimension.

### getHotSearch

- **API**: `getHotSearch` — Get hot tokens and contracts (trading metrics and price data)
- **Use when**: User asks for "hot tokens", "hot contracts", or "trending on TRON".
- **Response**: Hot tokens/contracts with price and activity.

### getHomepageData

- **API**: `getHomepageData` — Get homepage data (TPS, node count, overview, frozen, TVL, etc.)
- **Use when**: User asks for "TRON overview" or "network summary".
- **Response**: TPS, nodes, overview, TVL, frozen.

### getCurrentTps

- **API**: `getCurrentTps` — Get current TPS, latest block height, and historical max TPS
- **Use when**: User asks for "current TPS" or "network throughput".
- **Response**: currentTps, latest block, max TPS.

### getTriggerAmountStatistic

- **API**: `getTriggerAmountStatistic` — Get contract call volume distribution by date
- **Use when**: User asks for "contract call distribution" by date.

### getContractCallerStatisticOverview

- **API**: `getContractCallerStatisticOverview` — Get contract caller statistics (default last 7 days)
- **Use when**: User asks for "who is calling contracts" or "caller overview".

## Troubleshooting

- **MCP connection failed**: If you see "Connection refused", verify TronScan MCP is connected in Settings > Extensions.
- **API rate limit / 429**: TronScan API has call count and frequency limits when no API key is used. If you encounter rate limiting or 429 errors, go to [TronScan Developer API](https://tronscan.org/#/developer/api) to apply for an API key, then add it to your MCP configuration and retry.

### Empty or unexpected results
Check time range parameters; some APIs have default limits (e.g. getDailyAccounts max 2000 days).

## Notes

- `getDailyAccounts` returns `newAddressSeen` (daily new addresses)—an activity proxy, not precise DAU. When user asks for DAU, the model must first declare that this is a new-address metric and must not be presented as exact DAU.
- Top accounts by "staked TRX" use `getTop10` with the appropriate category (see TronScan API list for category values).
- For a single dashboard of "what’s happening", combine: `getHomepageData` + `getCurrentTps` + `getHotSearch` + `getTop10` + `getTransactionStatistics`.
